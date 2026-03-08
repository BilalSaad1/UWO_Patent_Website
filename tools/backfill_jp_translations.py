"""
backfill_jp_translations.py

Fills in title_en for all JP rows in patents_index where title_en IS NULL.
Run this once after adding the translation feature to jp_ingest.py.

Usage:
    python tools/backfill_jp_translations.py
    python tools/backfill_jp_translations.py --batch-size 100 --pause 1.0
"""
from __future__ import annotations

import argparse
import os
import time
import requests as _requests
from pathlib import Path

# Patch requests with a default timeout so translation calls never hang forever
_original_get = _requests.get
def _get_with_timeout(*args, **kwargs):
    kwargs.setdefault("timeout", 15)
    return _original_get(*args, **kwargs)
_requests.get = _get_with_timeout

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
# Try all known .env locations in priority order
for _env in [ROOT / ".env", ROOT / "backend" / ".env", ROOT / "scrapper" / ".env"]:
    if _env.exists():
        load_dotenv(_env, override=False)

from sqlalchemy import create_engine, text


def get_engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set.")
    return create_engine(url, future=True)


def _clean(translations: list, originals: list) -> list[str | None]:
    return [
        en if en and en.strip() and en.strip() != orig else None
        for orig, en in zip(originals, translations)
    ]


def translate_batch(titles: list[str]) -> list[str | None]:
    try:
        from deep_translator import GoogleTranslator, MyMemoryTranslator
    except ImportError:
        print("  [warn] deep-translator not installed. Run: pip install deep-translator")
        return [None] * len(titles)

    # Try Google first
    try:
        translated = GoogleTranslator(source="ja", target="en").translate_batch(titles)
        return _clean(translated, titles)
    except Exception as e:
        print(f"  [warn] Google Translate failed ({type(e).__name__}: {e}), trying MyMemory...")

    # Fallback: MyMemory (translate one at a time — its batch calls translate individually anyway)
    results: list[str | None] = []
    translator = MyMemoryTranslator(source="ja-JP", target="en-GB")
    for orig in titles:
        try:
            en = translator.translate(orig)
            results.append(en if en and en.strip() and en.strip() != orig else None)
        except Exception:
            results.append(None)
        time.sleep(0.1)  # MyMemory rate limit is generous but be polite
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=10,
                    help="Titles to translate per API call (default 10)")
    ap.add_argument("--pause", type=float, default=0.5,
                    help="Seconds to sleep between batches (default 0.5)")
    args = ap.parse_args()

    eng = get_engine()

    # Fetch all JP rows with no English title
    with eng.connect() as conn:
        rows = conn.execute(text("""
            SELECT patent_id, title
            FROM patents_index
            WHERE jurisdiction = 'JP'
              AND title_en IS NULL
              AND title IS NOT NULL
              AND title != '(no title)'
            ORDER BY patent_id
        """)).fetchall()

    total = len(rows)
    if total == 0:
        print("Nothing to backfill — all JP rows already have title_en.")
        return

    print(f"Backfilling {total:,} JP patents...")
    updated = 0

    for i in range(0, total, args.batch_size):
        chunk = rows[i : i + args.batch_size]
        ids = [r[0] for r in chunk]
        titles = [r[1] for r in chunk]

        translations = translate_batch(titles)

        pairs = [
            {"patent_id": pid, "title_en": en}
            for pid, en in zip(ids, translations)
            if en is not None
        ]

        if pairs:
            with eng.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE patents_index
                        SET title_en = :title_en
                        WHERE jurisdiction = 'JP' AND patent_id = :patent_id
                    """),
                    pairs,
                )
            updated += len(pairs)

        done = min(i + args.batch_size, total)
        print(f"  {done:,}/{total:,} processed, {updated:,} translations written")

        if done < total:
            time.sleep(args.pause)

    print(f"Done. {updated:,} of {total:,} rows now have an English title.")


if __name__ == "__main__":
    main()
