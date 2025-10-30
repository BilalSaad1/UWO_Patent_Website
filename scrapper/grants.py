from pathlib import Path
from zipfile import ZipFile
from lxml import etree
from typing import Iterable, Tuple
import re

# minimal XML fields
def _iter_grant_xml(zf: ZipFile) -> Iterable[bytes]:
    for n in zf.namelist():
        if n.lower().endswith((".xml", ".sgm")):
            with zf.open(n) as fh:
                yield fh.read()

def _extract_one(doc: bytes) -> Tuple[str,str,str|None]:
    # Handle common IPG structures (US patent grants)
    root = etree.fromstring(doc)
    # Patent number
    pn = root.xpath("string(//us-bibliographic-data-grant/publication-reference/document-id/doc-number)")
    if not pn:
        pn = root.xpath("string(//publication-reference/document-id/doc-number)")
    pn = pn.strip()
    if not pn:
        return None  # skip non-grant docs

    # Title
    title = root.xpath("string(//invention-title)")
    title = re.sub(r"\s+", " ", title).strip()

    # Grant date
    gd = root.xpath("string(//us-bibliographic-data-grant/publication-reference/document-id/date)")
    gd = gd.strip() or None
    return pn, title, gd

def load_grants(zip_path: Path, engine) -> int:
    from sqlalchemy import text
    count = 0
    with ZipFile(zip_path) as zf, engine.begin() as conn:
        for xml in _iter_grant_xml(zf):
            try:
                rec = _extract_one(xml)
                if not rec: 
                    continue
                pn, title, gd = rec
                conn.execute(text("""
                    INSERT INTO grants_raw (patent, title, grant_date)
                    VALUES (:pn, :title, to_date(:gd,'YYYYMMDD'))
                    ON CONFLICT (patent) DO UPDATE
                      SET title=EXCLUDED.title,
                          grant_date=COALESCE(EXCLUDED.grant_date, grants_raw.grant_date)
                """), {"pn": pn, "title": title, "gd": gd or ""})
                count += 1
            except Exception:
                # ignore malformed members for now
                pass
    return count