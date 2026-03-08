from __future__ import annotations

import os
import re
import tarfile
import time
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, List, Optional

from sqlalchemy import create_engine, text


def _env_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Put it in repo .env or backend/.env or your shell.")
    return url


def get_engine():
    return create_engine(_env_database_url(), future=True)


def _to_date_yyyymmdd(s: str) -> Optional[date]:
    s = (s or "").strip()
    if not s or s == "00000000":
        return None
    if not re.fullmatch(r"\d{8}", s):
        return None
    try:
        return datetime.strptime(s, "%Y%m%d").date()
    except Exception:
        return None


def _is_all_zeros_digits(x: str) -> bool:
    """
    Returns True if x contains only digits and all are '0'
    e.g. '000', '0000000000'. Also True for '' after cleaning.
    """
    x = (x or "").strip()
    if not x:
        return True
    if not re.fullmatch(r"\d+", x):
        return False
    return x.lstrip("0") == ""


def _clean_digits_keep_nonzero(x: str) -> str:
    d = re.sub(r"\D", "", (x or "").strip())
    # treat all-zero as missing
    if _is_all_zeros_digits(d):
        return ""
    # normalize by removing leading zeros so ids don't collapse
    return d.lstrip("0")


def _pick_patent_id(app_exam_pub_num: str, reg_num: str, app_num: str) -> str:
    """
    Choose a stable JP identifier for patents_index.

    Priority:
      1) app_exam_pub_num (publication) if present and not all zeros
      2) reg_num (registration) if present and not all zeros
      3) app_num (application) if present and not all zeros

    Returned format: 'JP' + digits-without-leading-zeros
    """
    pub = _clean_digits_keep_nonzero(app_exam_pub_num)
    if pub:
        return f"JP{pub}"

    reg = _clean_digits_keep_nonzero(reg_num)
    if reg:
        return f"JP{reg}"

    app = _clean_digits_keep_nonzero(app_num)
    if app:
        return f"JP{app}"

    return "JPUNKNOWN"


def _pick_display_date(
    app_exam_pub_year_month_day: Optional[date],
    set_reg_year_month_day: Optional[date],
    app_year_month_day: Optional[date],
) -> Optional[date]:
    # best: publication date, else registration date, else filing date
    return app_exam_pub_year_month_day or set_reg_year_month_day or app_year_month_day


def _is_inactive_reason(
    conti_prd_expire_ymd: Optional[date],
    next_pen_pymnt_tm_lmt_ymd: Optional[date],
    app_year_month_day: Optional[date],
    today: date,
) -> Optional[str]:
    """
    Heuristic inactivity rules from JPDRP fields:

    - FEES: next penalty payment limit date passed
    - TERM: continuation/term expired date passed, OR fallback: app date older than 20 years

    Priority: FEES first, then TERM.
    """
    if next_pen_pymnt_tm_lmt_ymd and next_pen_pymnt_tm_lmt_ymd <= today:
        return "FEES"

    if conti_prd_expire_ymd and conti_prd_expire_ymd <= today:
        return "TERM"

    if app_year_month_day:
        # fallback: 20-year age check like US (approx)
        try:
            if app_year_month_day <= date(today.year - 20, today.month, today.day):
                return "TERM"
        except Exception:
            if app_year_month_day.year <= today.year - 20:
                return "TERM"

    return None


def _translate_titles(titles: List[str]) -> List[Optional[str]]:
    """
    Translate a list of Japanese titles to English using Google Translate (free).
    Returns a list of the same length; entries are None if translation failed.
    Translates in sub-batches of 50 to stay within free API limits.
    """
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        return [None] * len(titles)

    results: List[Optional[str]] = []
    chunk_size = 50
    for i in range(0, len(titles), chunk_size):
        chunk = titles[i : i + chunk_size]
        try:
            translated = GoogleTranslator(source="ja", target="en").translate_batch(chunk)
            for orig, en in zip(chunk, translated):
                # If translation returned the same string or empty, store None
                results.append(en if en and en.strip() and en.strip() != orig else None)
        except Exception:
            results.extend([None] * len(chunk))
        if i + chunk_size < len(titles):
            time.sleep(0.5)  # be polite to the free API between chunks

    return results


@dataclass
class JpRow:
    patent_id: str
    title: str
    title_en: Optional[str]
    date: Optional[date]
    inactive_reason: str


def _iter_mgt_rows_from_member(tf: tarfile.TarFile, member_name: str, today: date) -> Iterable[JpRow]:
    """
    Parse one TSV member (upd_mgt_info_p.tsv or upd_mgt_info_u.tsv) and yield inactive records.
    TSV is UTF-8 with BOM (utf-8-sig).
    """
    m = tf.getmember(member_name)
    f = tf.extractfile(m)
    if f is None:
        return

    header_line = f.readline().decode("utf-8-sig", errors="replace").rstrip("\n\r")
    cols = header_line.split("\t")
    idx = {c: i for i, c in enumerate(cols)}

    required = [
        "reg_num",
        "app_num",
        "conti_prd_expire_ymd",
        "next_pen_pymnt_tm_lmt_ymd",
        "app_year_month_day",
        "app_exam_pub_num",
        "app_exam_pub_year_month_day",
        "set_reg_year_month_day",
        "invent_title_etc",
    ]
    for r in required:
        if r not in idx:
            raise RuntimeError(f"[JPDRP] Missing required column '{r}' in {member_name}")

    for raw in f:
        line = raw.decode("utf-8", errors="replace").rstrip("\n\r")
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < len(cols):
            continue

        reg_num = parts[idx["reg_num"]].strip()
        app_num = parts[idx["app_num"]].strip()

        conti = _to_date_yyyymmdd(parts[idx["conti_prd_expire_ymd"]])
        next_pen = _to_date_yyyymmdd(parts[idx["next_pen_pymnt_tm_lmt_ymd"]])
        app_dt = _to_date_yyyymmdd(parts[idx["app_year_month_day"]])

        pub_num = parts[idx["app_exam_pub_num"]].strip()
        pub_dt = _to_date_yyyymmdd(parts[idx["app_exam_pub_year_month_day"]])

        set_reg_dt = _to_date_yyyymmdd(parts[idx["set_reg_year_month_day"]])

        title = (parts[idx["invent_title_etc"]] or "").strip()
        title = re.sub(r"\s+", " ", title)

        reason = _is_inactive_reason(conti, next_pen, app_dt, today)
        if not reason:
            continue

        patent_id = _pick_patent_id(pub_num, reg_num, app_num)
        display_date = _pick_display_date(pub_dt, set_reg_dt, app_dt)

        if not title:
            title = "(no title)"

        yield JpRow(
            patent_id=patent_id,
            title=title,
            title_en=None,  # filled in during flush
            date=display_date,
            inactive_reason=reason,
        )


def ingest_jpdrp_to_index(jpdrp_tar_gz: str) -> int:
    """
    Ingest JPDRP daily update (tar.gz) into patents_index as jurisdiction='JP',
    inserting ONLY inactive (TERM/FEES) records.

    Returns number of upserted rows attempted.
    """
    eng = get_engine()
    today = date.today()

    with eng.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS patents_index (
                    jurisdiction    TEXT NOT NULL,
                    patent_id       TEXT NOT NULL,
                    title           TEXT,
                    title_en        TEXT,
                    date            DATE,
                    inactive_reason TEXT,
                    PRIMARY KEY (jurisdiction, patent_id)
                );
                """
            )
        )
        # Add title_en column if the table already exists without it
        conn.execute(
            text(
                "ALTER TABLE patents_index ADD COLUMN IF NOT EXISTS title_en TEXT;"
            )
        )

    total = 0
    row_batch: List[JpRow] = []

    def flush():
        nonlocal row_batch, total
        if not row_batch:
            return
        # Translate Japanese titles to English in bulk before inserting
        english = _translate_titles([r.title for r in row_batch])
        dicts = [
            {
                "patent_id": r.patent_id,
                "title": r.title,
                "title_en": en,
                "date": r.date,
                "inactive_reason": r.inactive_reason,
            }
            for r, en in zip(row_batch, english)
        ]
        with eng.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO patents_index (jurisdiction, patent_id, title, title_en, date, inactive_reason)
                    VALUES ('JP', :patent_id, :title, :title_en, :date, :inactive_reason)
                    ON CONFLICT (jurisdiction, patent_id) DO UPDATE
                      SET title           = EXCLUDED.title,
                          title_en        = EXCLUDED.title_en,
                          date            = EXCLUDED.date,
                          inactive_reason = EXCLUDED.inactive_reason;
                    """
                ),
                dicts,
            )
        total += len(row_batch)
        row_batch = []

    with tarfile.open(jpdrp_tar_gz, "r:gz") as tf:
        names = [m.name for m in tf.getmembers() if m.isfile()]
        targets = [n for n in names if n.endswith("upd_mgt_info_p.tsv") or n.endswith("upd_mgt_info_u.tsv")]
        if not targets:
            raise RuntimeError("JPDRP tar.gz did not contain upd_mgt_info_p.tsv or upd_mgt_info_u.tsv")

        for member_name in targets:
            for row in _iter_mgt_rows_from_member(tf, member_name, today):
                row_batch.append(row)
                if len(row_batch) >= 5000:
                    flush()

        flush()

    return total


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser("jp_ingest")
    ap.add_argument("--jpdrp-tar", required=True, help="Path to JPDRP_YYYYMMDD.tar.gz")
    args = ap.parse_args()

    n = ingest_jpdrp_to_index(args.jpdrp_tar)
    print(f"[JP] patents_index upserted: {n:,} rows")