from pathlib import Path
from zipfile import ZipFile
from io import TextIOWrapper
from sqlalchemy import text
import re

def _norm(s): return (s or "").strip().upper()

def _to_yyyymmdd(s: str):
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

def load_maintenance(zip_path: Path, engine) -> int:
    """Handles the USPTO fixed-width, space-separated maintenance file (e.g., MaintFeeEvents_YYYYMMDD.txt)."""
    count = 0
    with ZipFile(zip_path) as zf, engine.begin() as conn:
        # choose largest .txt/.csv member (the big events file)
        names = [n for n in zf.namelist() if n.lower().endswith((".txt", ".csv"))]
        if not names:
            return 0
        names.sort(key=lambda n: zf.getinfo(n).file_size, reverse=True)
        name = names[0]

        lines = 0
        with zf.open(name) as fh:
            for raw in TextIOWrapper(fh, encoding="utf-8", errors="ignore"):
                lines += 1
                line = raw.strip()
                if not line:
                    continue
                parts = line.split()
                # empirical layout from your probe:
                # [cust_id, patent, ?, pay_date?, event_date, code]
                if len(parts) < 6:
                    continue
                pn   = parts[1]
                dt   = _to_yyyymmdd(parts[-2])
                code = _norm(parts[-1])
                if not pn or not dt or not code:
                    continue
                try:
                    conn.execute(text("""
                        INSERT INTO maint_events_raw (patent, event_code, event_date, details)
                        VALUES (:pn, :code, to_date(:dt,'YYYYMMDD'), NULL)
                    """), {"pn": pn, "code": code, "dt": dt})
                    count += 1
                except Exception:
                    # ignore malformed lines/duplicates
                    pass

                if lines % 100000 == 0:
                    print(f"[maint] read={lines:,} inserted={count:,}", flush=True)
    return count