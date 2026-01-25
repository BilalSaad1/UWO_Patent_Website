from scrapper.cli import get_engine
from sqlalchemy import text

def rebuild_index_us():
    eng = get_engine()
    with eng.begin() as conn:
        # Upsert US inactive patents into unified index
        conn.execute(text("""
            INSERT INTO patents_index (jurisdiction, patent_id, title, date, inactive_reason)
            SELECT 'US', patent, title, grant_date, NULL
            FROM inactive_patents
            ON CONFLICT (jurisdiction, patent_id) DO UPDATE
              SET title = EXCLUDED.title,
                  date  = EXCLUDED.date;
        """))
    print("US index updated from inactive_patents.")

if __name__ == "__main__":
    rebuild_index_us()