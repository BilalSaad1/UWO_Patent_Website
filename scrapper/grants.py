from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from typing import Optional
import re
from sqlalchemy import text

def _norm(s: Optional[str]) -> str:
    return (s or "").strip()

def _to_yyyymmdd(s: str) -> Optional[str]:
    s = (s or "").strip()
    if not s:
        return None
    if re.fullmatch(r"\d{8}", s):
        return s
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return s.replace("-", "")
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        mm, dd, yy = m.groups()
        return f"{yy}{int(mm):02d}{int(dd):02d}"
    return None

def _extract_from_tree(root: etree._Element):
    """
    Namespace-agnostic pulls for PN, Title, Grant/Publication Date.

    Order:
      1) Modern PTBLXML (us-patent-grant) fields
      2) APS PGB (2002–2004) fields: PATDOC/B100/B110/DNUM, B540/STEXT, B140/DATE
      3) Very generic fallbacks (unchanged)
    """
    def first_text(path_exprs):
        for xp in path_exprs:
            try:
                t = root.xpath(f"string({xp})")
            except Exception:
                t = ""
            if t:
                t = t.strip()
                if t:
                    return t
        return ""

    # ---- (1) Modern PTBLXML (your existing paths, kept first) ----
    pn = first_text([
        "//us-bibliographic-data-grant/publication-reference/document-id/doc-number",
        "//publication-reference/document-id/doc-number",
        "//*/document-id/doc-number",
        "//*/doc-number",
    ])
    title = first_text([
        "//invention-title",
        "//*/invention-title",
        "//*/title",
    ])
    gd = first_text([
        "//us-bibliographic-data-grant/publication-reference/document-id/date",
        "//publication-reference/document-id/date",
        "//*/document-id/date",
        "//*/date",
    ])

    pn = _norm(pn)
    title = re.sub(r"\s+", " ", _norm(title))
    gd = _to_yyyymmdd(gd)

    if pn and title:
        return pn, title, gd

    # ---- (2) APS PGB (2002–2004) under PATDOC ----
    # Patent number often under B100/B110/DNUM/PDAT (designs use DNUM),
    # Title under B540/STEXT/PDAT, Date under B140/DATE/PDAT (YYYYMMDD).
    aps_pn = first_text([
        ".//B100//DNUM/PDAT",
        ".//B110//DNUM/PDAT",
        # occasionally plain text under B110/PDAT in some dumps:
        ".//B110/PDAT",
    ])
    aps_title = first_text([
        ".//B540//STEXT/PDAT",
        ".//B540/PDAT",
    ])
    aps_gd = first_text([
        ".//B140/DATE/PDAT",
        ".//B140/PDAT",
    ])

    aps_pn = _norm(aps_pn)
    aps_title = re.sub(r"\s+", " ", _norm(aps_title))
    aps_gd = _to_yyyymmdd(aps_gd)

    if aps_pn and aps_title:
        return aps_pn, aps_title, aps_gd

    # ---- (3) Very generic last-ditch fallback (unchanged) ----
    pn = first_text(["//doc-number"])
    pn = _norm(pn)
    if pn and title:
        return pn, title, gd

    return None, None, None

def _iter_docs(zf: ZipFile, member_name: str):
    """
    Yield each document inside the weekly member.
    - XML weekly: one big XML file containing multiple <us-patent-grant> docs.
    - SGML/XML APS weekly (PGB): repeated <PATDOC>...</PATDOC>.
    We split heuristically, keeping the opening tag with each chunk.
    """
    with zf.open(member_name) as fh:
        data = fh.read()

    lower_name = member_name.lower()
    upper = data.upper()

    # APS PGB (2002–2004): PATDOC blocks (present in .sgm and some .xml)
    if lower_name.endswith(".sgm") or b"<PATDOC" in upper:
        marker = b"<PATDOC"
        idxs = []
        start = 0
        while True:
            i = upper.find(marker, start)
            if i == -1:
                break
            idxs.append(i)
            start = i + len(marker)
        if not idxs:
            # Fall back to whole file
            yield data
        else:
            idxs.append(len(data))
            for a, b in zip(idxs, idxs[1:]):
                yield data[a:b]
        return

    # Modern PTBLXML: us-patent-grant blocks
    marker = b"<us-patent-grant"
    idxs = []
    start = 0
    while True:
        i = data.find(marker, start)
        if i == -1:
            break
        idxs.append(i)
        start = i + len(marker)
    if not idxs:
        yield data
    else:
        idxs.append(len(data))
        for a, b in zip(idxs, idxs[1:]):
            yield data[a:b]

def load_grants(zip_path: Path, engine) -> int:
    total = 0
    with ZipFile(zip_path) as zf, engine.begin() as conn:
        names = [n for n in zf.namelist() if n.lower().endswith((".xml", ".sgm"))]
        if not names:
            return 0
        # pick the largest member (unchanged)
        names.sort(key=lambda n: zf.getinfo(n).file_size, reverse=True)
        member = names[0]

        for doc_bytes in _iter_docs(zf, member):
            root = None
            try:
                # XML parser first
                root = etree.fromstring(doc_bytes, parser=etree.XMLParser(recover=True, huge_tree=True))
            except Exception:
                try:
                    # Some APS chunks are more SGML-ish; fallback to HTML tree so xpath still works
                    root = etree.HTML(doc_bytes)
                except Exception:
                    root = None
            if root is None:
                continue

            pn, title, gd = _extract_from_tree(root)
            if not pn or not title:
                continue

            conn.execute(text("""
                INSERT INTO grants_raw (patent, title, grant_date)
                VALUES (:pn, :title, to_date(:gd,'YYYYMMDD'))
                ON CONFLICT (patent) DO UPDATE
                  SET title = EXCLUDED.title,
                      grant_date = COALESCE(EXCLUDED.grant_date, grants_raw.grant_date)
            """), {"pn": pn, "title": title, "gd": gd or ""})
            total += 1
    return total