from __future__ import annotations
import csv, io, zipfile, re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
import requests

from .config import CFG
from .paths import ensure_dirs
from .http import download

ODP_BASE = "https://data.uspto.gov/bulkdata/datasets"

@dataclass
class MaintEvent:
    patent: str
    code: str
    date: str  # YYYY-MM-DD

def _dataset_url() -> str:
    qs = []
    if CFG.odp_from: qs.append(f"fileDataFromDate={CFG.odp_from}")
    if CFG.odp_to:   qs.append(f"fileDataToDate={CFG.odp_to}")
    return f"{ODP_BASE}/{CFG.maint_product_id}" + (("?" + "&".join(qs)) if qs else "")

def _discover_zip_from_dataset_page(url: str) -> str:
    # Very light-weight: fetch HTML and look for first .zip URL
    html = requests.get(url, timeout=60).text
    m = re.search(r'https?://[^\s"]+\.zip', html, flags=re.I)
    if not m:
        raise RuntimeError("Could not find .zip on dataset page. Set MAINT_ZIP_URL env var.")
    return m.group(0)

def fetch_latest_zip() -> Path:
    paths = ensure_dirs()
    tag = ""
    if CFG.odp_from: tag += f"_{CFG.odp_from}"
    if CFG.odp_to:   tag += f"_{CFG.odp_to}"
    out = paths["downloads"] / f"ptmnfee2{tag or '_latest'}.zip"

    if CFG.maint_zip_url:
        url = CFG.maint_zip_url
    else:
        url = _discover_zip_from_dataset_page(_dataset_url())
    return download(url, out)

def parse_zip(zip_path: Path) -> Iterator[MaintEvent]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        # choose the largest .txt file (weekly cumulative dumps often have one)
        name = max((n for n in zf.namelist() if n.lower().endswith(".txt")),
                   key=lambda n: zf.getinfo(n).file_size)
        with zf.open(name) as fh:
            data = fh.read()

    text = data.decode("utf-8", errors="replace").replace("\r\n", "\n")
    reader = csv.reader(io.StringIO(text), delimiter="|")
    for row in reader:
        if len(row) < 5:
            continue
        fields = [c.strip() for c in row]

        # patent number (US######## or digits)
        patent = next((c for c in fields if c.upper().startswith("US") or c.isdigit()), "")
        if patent.isdigit():
            patent = f"US{patent}"

        # event code (prefer ones with EXP/PMT hints)
        code = ""
        for c in fields:
            uc = c.upper().strip(".")
            if 2 <= len(uc) <= 5 and uc.isalpha():
                if "EXP" in uc or "PMT" in uc:
                    code = uc
                    break

        # date: YYYYMMDD or YYYY-MM-DD
        date = ""
        for c in fields:
            d = c.strip()
            if len(d) == 8 and d.isdigit():
                date = f"{d[0:4]}-{d[4:6]}-{d[6:8]}"; break
            if len(d) == 10 and d[4] == "-" and d[7] == "-":
                date = d; break

        if patent and code and date:
            yield MaintEvent(patent=patent, code=code, date=date)