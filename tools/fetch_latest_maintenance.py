import os, re, pathlib, requests, zipfile
from datetime import datetime

API_KEY = os.environ.get("ODP_API_KEY") or ""
if not API_KEY:
    raise SystemExit("ERROR: ODP_API_KEY not set in this shell.")

DATA_DIR = pathlib.Path(os.getenv("DATA_DIR", "data")).resolve()
OUT_DIR  = (DATA_DIR / "downloads" / "maintenance")
OUT_DIR.mkdir(parents=True, exist_ok=True)

LISTING_URL = "https://api.uspto.gov/api/v1/datasets/products/PTMNFEE2"
RX_MAINT = re.compile(r"^MaintFeeEvents_(\d{8})\.zip$", re.IGNORECASE)

S = requests.Session()
S.headers.update({
    "x-api-key": API_KEY,
    "Accept": "application/json",
    "User-Agent": "WesternExpiredPatents/1.0",
})

def parse_dt(s: str) -> datetime:
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    return datetime.min

def main():
    params = {
        "fileDataFromDate": "2002-01-01",
        "fileDataToDate":   "2100-01-01",
        "includeFiles":     "true",
    }
    r = S.get(LISTING_URL, params=params, timeout=90)
    r.raise_for_status()
    data = r.json()

    products = data.get("bulkDataProductBag") or []
    if not products:
        raise SystemExit("No bulkDataProductBag in response.")

    files = (products[0].get("productFileBag") or {}).get("fileDataBag") or []
    if not files:
        raise SystemExit("No fileDataBag entries found.")

    candidates = []
    for f in files:
        name = (f.get("fileName") or "").strip()
        m = RX_MAINT.match(name)
        if not m:
            continue
        yyyymmdd = m.group(1)
        key = (
            parse_dt(str(f.get("fileDataToDate") or "")),
            parse_dt(str(f.get("fileReleaseDate") or "")),
            datetime.strptime(yyyymmdd, "%Y%m%d"),
        )
        url = (f.get("fileDownloadURI") or "").strip()
        if not url:
            year = yyyymmdd[:4]
            url = f"https://api.uspto.gov/api/v1/datasets/products/files/PTMNFEE2/{year}/{name}"
        candidates.append((key, name, url))

    if not candidates:
        raise SystemExit("No MaintFeeEvents_YYYYMMDD.zip entries found.")

    candidates.sort()
    _, latest_name, latest_url = candidates[-1]

    dest = OUT_DIR / latest_name
    print("Latest maintenance file:", latest_name)
    print("URL:", latest_url)
    print("Saving to:", dest)

    need = True
    if dest.exists() and dest.stat().st_size > 100_000:
        need = False

    if need:
        with S.get(latest_url, stream=True, timeout=300) as resp:
            resp.raise_for_status()
            head = next(resp.iter_content(256))
            if not head.startswith(b"PK\x03\x04"):
                raise SystemExit(f"Unexpected head bytes (not a ZIP): {head[:64]!r}")
            with open(dest, "wb") as f:
                f.write(head)
                for chunk in resp.iter_content(1 << 20):
                    if chunk:
                        f.write(chunk)
        print("Saved:", dest, "size=", dest.stat().st_size)
    else:
        print("Already have latest:", dest, "size=", dest.stat().st_size)

    try:
        with zipfile.ZipFile(dest) as zf:
            names = sorted(zf.namelist(), key=lambda n: zf.getinfo(n).file_size, reverse=True)
            print("ZIP entries (top 1):", names[:1])
            if names:
                info = zf.getinfo(names[0])
                print(f"  {names[0]}  size={info.file_size:,} bytes")
    except zipfile.BadZipFile as e:
        raise SystemExit(f"Downloaded file is not a valid ZIP: {e}")

    removed = 0
    for p in OUT_DIR.glob("MaintFeeEvents_*.zip"):
        if p.name != latest_name:
            try:
                p.unlink()
                removed += 1
            except Exception:
                pass
    print(f"Pruned {removed} older maintenance ZIP(s).")

if __name__ == "__main__":
    main()
