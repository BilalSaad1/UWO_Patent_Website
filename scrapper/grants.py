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
    """Namespace-agnostic pulls for PN, Title, Grant/Publication Date."""
    def first_text(path_exprs):
        for xp in path_exprs:
            t = root.xpath(f"string({xp})")
            if t:
                t = t.strip()
                if t:
                    return t
        return ""

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
    return pn, title, gd

def _iter_docs(zf: ZipFile, member_name: str):
    """
    Yield each document inside the weekly member.
    - XML weekly: one big XML file containing multiple <us-patent-grant> docs
      (not always cleanly split by XML decls).
    - SGML (APS) weekly: .sgm with repeated <PATDOC>...</PATDOC>.
    We split heuristically, keeping the opening tag with each chunk.
    """
    with zf.open(member_name) as fh:
        data = fh.read()

    lower_name = member_name.lower()
    if lower_name.endswith(".sgm") or b"<PATDOC" in data.upper():
        # --- SGML / APS --- split on <PATDOC ...> boundaries
        marker = b"<PATDOC"
        upper = data.upper()
        idxs = []
        start = 0
        while True:
            i = upper.find(marker, start)
            if i == -1:
                break
            idxs.append(i)
            start = i + 7
        if not idxs:
            yield data  # fallback: single doc
        else:
            idxs.append(len(data))
            for a, b in zip(idxs, idxs[1:]):
                yield data[a:b]
    else:
        # --- XML --- try to split on <us-patent-grant ...> (more reliable than <?xml)
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
            # fallback: whole file might be a single patent
            yield data
        else:
            idxs.append(len(data))
            for a, b in zip(idxs, idxs[1:]):
                yield data[a:b]

def load_grants(zip_path: Path, engine) -> int:
    total = 0
    with ZipFile(zip_path) as zf, engine.begin() as conn:
        # pick largest .xml or .sgm member (weekly payload)
        names = [n for n in zf.namelist() if n.lower().endswith((".xml", ".sgm"))]
        if not names:
            return 0
        names.sort(key=lambda n: zf.getinfo(n).file_size, reverse=True)
        member = names[0]

        for doc_bytes in _iter_docs(zf, member):
            # Try strict XML first; if that fails, try HTML parser (tolerant) as a last resort
            root = None
            try:
                root = etree.fromstring(doc_bytes, parser=etree.XMLParser(recover=True, huge_tree=True))
            except Exception:
                try:
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