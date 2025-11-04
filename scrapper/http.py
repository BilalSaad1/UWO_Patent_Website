from __future__ import annotations
import time
from pathlib import Path
import requests
from tqdm import tqdm

CHUNK = 1 << 15 

def download(url: str, dest: Path, retries: int = 3, timeout: int = 90) -> Path:
    for attempt in range(retries):
        try:
            with requests.get(url, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", "0"))
                with open(dest, "wb") as f, tqdm(
                    total=total if total > 0 else None, unit="B", unit_scale=True, desc=dest.name
                ) as bar:
                    for chunk in r.iter_content(CHUNK):
                        if chunk:
                            f.write(chunk)
                            if total > 0: bar.update(len(chunk))
            return dest
        except Exception:
            if attempt + 1 >= retries:
                raise
            time.sleep(2 ** attempt)
    return dest