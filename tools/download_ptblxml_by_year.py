import os
import re
import time
import pathlib
import requests

# ===== CONFIG =====

API_KEY = os.environ.get("ODP_API_KEY") or ""
if not API_KEY:
    raise SystemExit("ERROR: ODP_API_KEY not set in this shell.")

# Which year of weekly PTBLXML to download
YEAR = int(os.environ.get("PT_YEAR", "2019"))

BASE_URL = "https://api.uspto.gov/api/v1/datasets/products/PTBLXML"

OUT_DIR = pathlib.Path("data/downloads/grants")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ==================

S = requests.Session()
S.headers.update(
    {
        "x-api-key": API_KEY,
        "Accept": "application/json",
        "User-Agent": "WesternExpiredPatents/1.0",
    }
)


def load_listing() -> dict:
    """
    Load PTBLXML metadata with file listing.
    NOTE: date filters on this endpoint do NOT appear to trim fileDataBag
    reliably, so we request includeFiles=true and filter by fileName client-side.
    """
    params = {
        "includeFiles": "true",
        # We still send a range for politeness, but we won't rely on it.
        "fileDataFromDate": "2002-01-01",
        "fileDataToDate": "2100-01-01",
    }
    print("Requesting listing…")
    print(" URL:", BASE_URL)
    print(" Params:", params)
    r = S.get(BASE_URL, params=params, timeout=60)
    print(" HTTP status:", r.status_code, r.reason)
    r.raise_for_status()
    return r.json()


def iter_file_bag(data):
    """
    Yield each fileDataBag entry.
    Structure observed:

    {
      "bulkDataProductBag": [
        {
          ...,
          "productFileBag": {
            "count": N,
            "fileDataBag": [ {fileName, fileDownloadURI, ...}, ... ]
          }
        }
      ]
    }
    """
    if not isinstance(data, dict):
        return
    bag = data.get("bulkDataProductBag") or []
    if not bag:
        return
    prod = bag[0] or {}
    fbag = prod.get("productFileBag") or {}
    files = fbag.get("fileDataBag") or []
    for f in files:
        if isinstance(f, dict):
            yield f


ZIP_PATTERN = re.compile(
    r"^(?:ipgb|pgb|ipg|pg)(?P<year>\d{4})(?P<mm>\d{2})(?P<dd>\d{2})_wk\d{1,3}(?:_r\d+)?(?:_rl)?\.zip$",
    re.IGNORECASE,
)


def is_target_zip(name: str) -> bool:
    """
    True if this is a weekly PTBLXML zip for the selected YEAR.
    """
    m = ZIP_PATTERN.match(name)
    if not m:
        return False
    return int(m.group("year")) == YEAR


def get_download_url(entry: dict) -> str | None:
    """
    Prefer official fileDownloadURI; fall back to similar keys.
    """
    for key in (
        "fileDownloadURI",
        "fileDownloadUri",
        "fileDownloadUrl",
        "downloadUrl",
        "url",
    ):
        v = entry.get(key)
        if isinstance(v, str) and v.startswith("http"):
            return v
    return None


def main():
    print(f"Using ODP_API_KEY length={len(API_KEY)}")
    print(f"Target YEAR (for context) = {YEAR}")
    print(f"Download directory: {OUT_DIR.resolve()}")
    print()

    data = load_listing()

    candidates = []
    total_entries = 0

    for entry in iter_file_bag(data):
        total_entries += 1
        name = (entry.get("fileName") or "").strip()
        if not name:
            continue

        # Debug: show a few entries so we can see the shape
        if total_entries <= 5:
            print(" Sample entry:", name, "keys:", list(entry.keys()))

        if not is_target_zip(name):
            continue

        url = get_download_url(entry)
        if not url:
            # As a last resort, construct from standard pattern (year segment)
            # Only do this if it matches our ipgbYYYYMMDD_wkNN*.zip naming.
            m = ZIP_PATTERN.match(name)
            if m:
                y = m.group("year")
                url = f"https://api.uspto.gov/api/v1/datasets/products/files/PTBLXML/{y}/{name}"
        if not url:
            print(" [WARN] No download URL for", name)
            continue

        candidates.append((name, url))

    print()
    print(f"Total fileDataBag entries seen: {total_entries}")
    print(f"PTBLXML weekly zips matching YEAR={YEAR}: {len(candidates)}")

    if not candidates:
        print("No matching zips found. Dumping a few entries for inspection:")
        # Show first 10 names to help debugging
        shown = 0
        for entry in iter_file_bag(data):
            name = (entry.get("fileName") or "").strip()
            if name:
                print("  ", name)
                shown += 1
                if shown >= 10:
                    break
        return

    # De-dupe while preserving order
    seen = set()
    files = []
    for name, url in candidates:
        if name in seen:
            continue
        seen.add(name)
        files.append((name, url))

    print("\nWill download these files:")
    for n, u in files:
        print("  ", n, "->", u)

    # Download
    for name, url in files:
        dest = OUT_DIR / name
        if dest.exists() and dest.stat().st_size > 0:
            print(f"(skip) already have {name} (size={dest.stat().st_size} bytes)")
            continue

        print(f"\nDownloading {name}")
        print(" URL:", url)
        try:
            with S.get(url, stream=True, timeout=300) as r:
                print(" HTTP status:", r.status_code, r.reason)
                if r.status_code != 200:
                    text_preview = r.text[:300].replace("\n", " ")
                    print("  !! Non-200 response, first 300 chars:", text_preview)
                    continue

                with open(dest, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        if chunk:
                            f.write(chunk)

            print(
                " Saved to",
                dest,
                "size=",
                dest.stat().st_size,
                "bytes",
            )
            # small pause to be polite
            time.sleep(0.25)
        except Exception as e:
            print(f" [WARN] Failed {name}: {e}")

    print("\nDone. Check contents of:", OUT_DIR.resolve())


if __name__ == "__main__":
    main()