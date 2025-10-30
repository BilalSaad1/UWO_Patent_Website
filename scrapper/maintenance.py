from pathlib import Path
from zipfile import ZipFile
import csv
from io import TextIOWrapper
from sqlalchemy import text

# The maintenance ZIP usually contains .txt or .csv (pipe/comma delimited).
CANDIDATE_DELIMS = [",", "|", "\t", ";"]

def _guess_delim(sample: str) -> str:
    return max(CANDIDATE_DELIMS, key=lambda d: sample.count(d))

def load_maintenance(zip_path: Path, engine) -> int:
    count = 0
    with ZipFile(zip_path) as zf, engine.begin() as conn:
        # pick the first text-like file
        name = next(n for n in zf.namelist() if n.lower().endswith((".txt",".csv")))
        with zf.open(name) as fh:
            head = fh.read(4096).decode("utf-8", "ignore")
            delim = _guess_delim(head)
        with zf.open(name) as fh:
            reader = csv.DictReader(TextIOWrapper(fh, encoding="utf-8", errors="ignore"), delimiter=delim)
            for row in reader:
                pn = (row.get("PatentNumber") or row.get("patent") or "").strip()
                code = (row.get("EventCode") or row.get("event_code") or "").strip().upper()
                dt = (row.get("EventDate") or row.get("event_date") or "").strip()
                if not pn or not code or not dt:
                    continue
                conn.execute(text("""
                    INSERT INTO maint_events_raw (patent, event_code, event_date, details)
                    VALUES (:pn, :code, to_date(:dt,'YYYYMMDD'), to_jsonb(:row::json))
                """), {"pn": pn, "code": code, "dt": dt, "row": row})
                count += 1
    return count