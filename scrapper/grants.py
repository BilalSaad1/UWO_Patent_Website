from __future__ import annotations
import zipfile, re, requests
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Dict
from lxml import etree

from .config import CFG
from .paths import ensure_dirs
from .http import download

ODP_BASE = "https://data.uspto.gov/bulkdata/datasets"

@dataclass
class GrantDoc:
    patent: str
    title: str
    grant_date: str | None

def _dataset_url() -> str:
    qs = []
    if CFG.odp_from: qs.append(f"fileDataFromDate={CFG.odp_from}")
    if CFG.odp_to:   qs.append(f"fileDataToDate={CFG.odp_to}")
    return f"{ODP_BASE}/{CFG.biblio_product_id}" + (("?" + "&".join(qs)) if qs else "")

def _discover_zip_from_dataset_page(url: str) -> str:
    html = requests.get(url, timeout=60).text
    m = re.search(r'https?://[^\s"]+\.zip', html, flags=re.I)
    if not m:
        raise RuntimeError("Could not find .zip on dataset page. Set BIBLIO_ZIP_URL env var.")
    return m.group(0)

def fetch_latest_zip() -> Path:
    paths = ensure_dirs()
    tag = ""
    if CFG.odp_from: tag += f"_{CFG.odp_from}"
    if CFG.odp_to:   tag += f"_{CFG.odp_to}"
    out = paths["downloads"] / f"ptblxml{tag or '_latest'}.zip"

    if CFG.biblio_zip_url:
        url = CFG.biblio_zip_url
    else:
        url = _discover_zip_from_dataset_page(_dataset_url())
    return download(url, out)

def parse_zip(zip_path: Path) -> Iterator[GrantDoc]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            if not name.lower().endswith(".xml"):
                continue
            with zf.open(name) as fh:
                try:
                    tree = etree.parse(fh)
                except Exception:
                    continue
            ns = tree.getroot().nsmap

            def text(xpath: str) -> str | None:
                el = tree.find(xpath, namespaces=ns)
                return el.text.strip() if el is not None and el.text else None

            pn = text(".//publication-reference/document-id/doc-number") \
                 or text(".//us-bibliographic-data-grant/publication-reference/document-id/doc-number")
            title = text(".//invention-title")
            gd = text(".//publication-reference/document-id/date") \
                 or text(".//us-bibliographic-data-grant/publication-reference/document-id/date")

            if pn and title:
                if gd and len(gd) == 8 and gd.isdigit():
                    gd = f"{gd[0:4]}-{gd[4:6]}-{gd[6:8]}"
                if not pn.startswith("US"):
                    pn = f"US{pn}"
                yield GrantDoc(patent=pn, title=title, grant_date=gd)

def to_map(docs: Iterator[GrantDoc]) -> Dict[str, GrantDoc]:
    return {d.patent: d for d in docs}