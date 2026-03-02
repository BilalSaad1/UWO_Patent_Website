from scrapper.cli import get_engine
from sqlalchemy import text

SQL = """
CREATE TABLE IF NOT EXISTS patents_index (
  jurisdiction TEXT NOT NULL,       -- 'US' or 'JP'
  patent_id TEXT NOT NULL,           -- identifier within the jurisdiction
  title TEXT,
  date DATE,                         -- display date (grant/publication/etc.)
  inactive_reason TEXT,              -- 'FEES'/'TERM'/NULL (optional)
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