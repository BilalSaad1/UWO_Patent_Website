from scrapper.cli import get_engine
from sqlalchemy import text

SQL = """
CREATE TABLE IF NOT EXISTS patents_index (
  jurisdiction TEXT NOT NULL,       -- 'US' or 'CN'
  patent_id TEXT NOT NULL,           -- US: patent number, CN: chosen id later
  title TEXT,
  date DATE,                         -- US: grant_date; CN: inactive_date (or pub_date if needed)
  inactive_reason TEXT,              -- 'FEES'/'TERM'/NULL
  PRIMARY KEY (jurisdiction, patent_id)
);

CREATE INDEX IF NOT EXISTS patents_index_jur_idx
  ON patents_index (jurisdiction);

CREATE INDEX IF NOT EXISTS patents_index_jur_date_idx
  ON patents_index (jurisdiction, date);
"""

if __name__ == "__main__":
    eng = get_engine()
    with eng.begin() as conn:
        conn.execute(text(SQL))
    print("patents_index created.")