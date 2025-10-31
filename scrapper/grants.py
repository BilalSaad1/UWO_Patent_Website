from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from typing import Optional
import re
from sqlalchemy import text

# --- helpers ---

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

    # Try ST.36 locations first, then loose fallbacks.
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
    # date can be grant/publish — both work for our display
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

def _iter_ipg_documents(zf: ZipFile, xml_name: str):
    """Yield each concatenated XML document as bytes from the single big IPG member."""
    # We split on the XML declaration, but keep it with each doc.
    DECL = b'<?xml'
    with zf.open(xml_name) as fh:
        buf = b""
        chunk = fh.read(1 << 20)  # 1MB chunks
        while chunk:
            buf += chunk
            while True:
                i = buf.find(DECL, 1)  # look for next declaration, skip position 0
                if i == -1:
                    break
                yield buf[:i]
                buf = buf[i:]
            chunk = fh.read(1 << 20)
        if buf.strip():
            yield buf

# --- main loader ---

def load_grants(zip_path: Path, engine) -> int:
    total = 0
    with ZipFile(zip_path) as zf, engine.begin() as conn:
        # Choose the largest .xml/.sgm file — weekly IPG
        names = [n for n in zf.namelist() if n.lower().endswith((".xml", ".sgm"))]
        if not names:
            return 0
        names.sort(key=lambda n: zf.getinfo(n).file_size, reverse=True)
        xml_name = names[0]

        for doc_bytes in _iter_ipg_documents(zf, xml_name):
            try:
                root = etree.fromstring(doc_bytes, parser=etree.XMLParser(recover=True, huge_tree=True))
            except Exception:
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