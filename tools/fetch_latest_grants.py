import os, re, sys
from pathlib import Path
import requests

API_KEY = os.environ.get("ODP_API_KEY") or ""
if not API_KEY:
    raise SystemExit("ERROR: ODP_API_KEY not set in this shell.")

BASE_URL = "https://api.uspto.gov/api/v1/datasets/products/PTBLXML"
OUT_DIR = Path("data/downloads/grants")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ZIP_RE = re.compile(r"^ipgb(?P<yyyymmdd>\d{8})_wk\d{1,3}(_rl)?\.zip$", re.I)

S = requests.Session()
S.headers.update({
    "x-api-key": API_KEY,
    "Accept": "application/json",
    "User-Agent": "WesternExpiredPatents/1.0",
})

def load_listing() -> dict:
    r = S.get(
        BASE_URL,
        params={"includeFiles": "true", "fileDataFromDate": "2002-01-01", "fileDataToDate": "2100-01-01"},
        timeout=90,
    )
    r.raise_for_status()
    return r.json()

def iter_file_bag(data):
    bag = (data or {}).get("bulkDataProductBag") or []
    if not bag: return
    prod = bag[0] or {}
    files = (prod.get("productFileBag") or {}).get("fileDataBag") or []
    for f in files:
        if isinstance(f, dict):
            yield f

def url_from_entry(entry) -> str | None:
    for k in ("fileDownloadURI","fileDownloadUri","fileDownloadUrl","downloadUrl","url"):
        v = entry.get(k)
        if isinstance(v, str) and v.startswith("http"):
            return v
    name = entry.get("fileName") or ""
    m = ZIP_RE.match(name)
    if m:
        y = name[4:8]
        return f"https://api.uspto.gov/api/v1/datasets/products/files/PTBLXML/{y}/{name}"
    return None

def pick_latest(entries):
    best = None
    best_date = ""
    for e in entries:
        name = (e.get("fileName") or "").strip()
        m = ZIP_RE.match(name)
        if not m: continue
        ymd = m.group("yyyymmdd")
        if ymd > best_date:
            best_date, best = ymd, e
    return best

def prune_older(latest_name: str, folder: Path) -> int:
    removed = 0
    for p in folder.glob("ipgb*.zip"):
        if p.name != latest_name and ZIP_RE.match(p.name):
            try:
                p.unlink()
                removed += 1
            except Exception:
                pass
    return removed

def main():
    data = load_listing()
    latest = pick_latest(list(iter_file_bag(data)))
    if not latest:
        print("Could not find any ipgbYYYYMMDD_wk*.zip in listing.")
        sys.exit(1)

    name = latest.get("fileName")
    url = url_from_entry(latest)
    if not url:
        print("No download URL for", name)
        sys.exit(1)

    dest = OUT_DIR / name
    print(f"Latest weekly grants file: {name}")
    print("URL:", url)
    print("Saving to:", dest.resolve())

    if not (dest.exists() and dest.stat().st_size > 0):
        with S.get(url, stream=True, timeout=300) as r:
            if r.status_code != 200:
                preview = r.text[:300].replace("\n"," ")
                raise SystemExit(f"Non-200 ({r.status_code}) for {url}; head={preview}")
            with open(dest, "wb") as f:
                for chunk in r.iter_content(1<<20):
                    if chunk: f.write(chunk)
        print("Downloaded OK:", dest, "size=", dest.stat().st_size)
    else:
        print(f"Already have latest: {dest} size={dest.stat().st_size}")

    removed = prune_older(name, OUT_DIR)
    print(f"Pruned {removed} older grant ZIP(s).")

if __name__ == "__main__":
    main()