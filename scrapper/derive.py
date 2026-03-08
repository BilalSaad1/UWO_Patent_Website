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

        # Keep patents_index in sync: replace all US rows with current inactive set
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS patents_index (
                jurisdiction    TEXT NOT NULL,
                patent_id       TEXT NOT NULL,
                title           TEXT,
                title_en        TEXT,
                date            DATE,
                inactive_reason TEXT,
                PRIMARY KEY (jurisdiction, patent_id)
            );
        """))
        conn.execute(text("DELETE FROM patents_index WHERE jurisdiction = 'US'"))
        conn.execute(text("""
            INSERT INTO patents_index (jurisdiction, patent_id, title, date, inactive_reason)
            SELECT 'US', patent, title, grant_date, NULL
            FROM inactive_patents
        """))

        return int(cnt)