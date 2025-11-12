from sqlalchemy import text

EXPIRED_CODES = {"EXP","EXP.","EXP-UNP","EXP-UNE"}  

def rebuild_inactive(engine) -> int:
    with engine.begin() as conn:
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
            ),
            aged AS (
              SELECT patent
              FROM grants_raw
              WHERE grant_date IS NOT NULL
                AND grant_date <= (CURRENT_DATE - INTERVAL '20 years')
            ),
            unioned AS (
              SELECT patent FROM expired
              UNION
              SELECT patent FROM aged
            )
            INSERT INTO inactive_patents (patent, title, grant_date)
            SELECT g.patent, g.title, g.grant_date
            FROM unioned u
            JOIN grants_raw g ON g.patent = u.patent
        """), {"codes": list(EXPIRED_CODES)})
        cnt = conn.execute(text("SELECT count(*) FROM inactive_patents")).scalar_one()
        return int(cnt)