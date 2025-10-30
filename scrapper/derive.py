from sqlalchemy import text

EXPIRED_CODES = {"EXP","EXP.","EXP-UNP","EXP-UNE"}  # extend as needed

def rebuild_inactive(engine) -> int:
    with engine.begin() as conn:
        # Take latest event per patent
        conn.execute(text("TRUNCATE inactive_patents"))
        conn.execute(text("""
            WITH last_evt AS (
              SELECT DISTINCT ON (patent) patent, event_code, event_date
              FROM maint_events_raw
              ORDER BY patent, event_date DESC
            ),
            expired AS (
              SELECT patent FROM last_evt
              WHERE upper(event_code) = ANY (:codes)
            )
            INSERT INTO inactive_patents (patent, title, grant_date)
            SELECT g.patent, g.title, g.grant_date
            FROM expired e
            JOIN grants_raw g ON g.patent = e.patent
        """), {"codes": list(EXPIRED_CODES)})
        cnt = conn.execute(text("SELECT count(*) FROM inactive_patents")).scalar_one()
        return int(cnt)