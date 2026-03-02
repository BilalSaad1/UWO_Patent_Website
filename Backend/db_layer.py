from __future__ import annotations
from datetime import date
from typing import List, Tuple, Optional
import os
import re

from sqlalchemy import create_engine, String, Date, select, func, text, and_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://uwo_patents:cumbersome@127.0.0.1:5432/patents",
)
engine = create_engine(DATABASE_URL, future=True, echo=False)


class Base(DeclarativeBase):
    pass


class InactivePatent(Base):
    """
    Backwards-compat model used by the existing API response:
      - patent
      - title
      - grant_date

    We will still return these objects from search_patents/get_patent,
    but now the source table is patents_index (with jurisdiction).
    """
    __tablename__ = "inactive_patents"
    patent: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    grant_date: Mapped[date | None] = mapped_column(Date)


class PatentIndex(Base):
    """
    New unified index table used for jurisdiction filtering.
    """
    __tablename__ = "patents_index"
    jurisdiction: Mapped[str] = mapped_column(String, primary_key=True)
    patent_id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    date: Mapped[date | None] = mapped_column(Date)
    inactive_reason: Mapped[str | None] = mapped_column(String, nullable=True)


def init_db() -> None:
    """Ensure required objects exist in the target DB."""
    with engine.begin() as conn:
        try:
            conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        except Exception:
            pass

        conn.exec_driver_sql(
            """
        CREATE TABLE IF NOT EXISTS grants_raw (
            patent     TEXT PRIMARY KEY,
            title      TEXT NOT NULL,
            grant_date DATE
        );
        """
        )
        conn.exec_driver_sql(
            """
        CREATE INDEX IF NOT EXISTS idx_grants_raw_grant_date
        ON grants_raw (grant_date);
        """
        )
        try:
            conn.exec_driver_sql(
                """
            CREATE INDEX IF NOT EXISTS idx_grants_raw_title_trgm
            ON grants_raw USING GIN (title gin_trgm_ops);
            """
            )
        except Exception:
            pass

        conn.exec_driver_sql(
            """
        CREATE TABLE IF NOT EXISTS maint_events_raw (
            id         BIGSERIAL PRIMARY KEY,
            patent     TEXT NOT NULL,
            event_code TEXT NOT NULL,
            event_date DATE NOT NULL,
            details    TEXT
        );
        """
        )
        conn.exec_driver_sql(
            """
        CREATE INDEX IF NOT EXISTS idx_maint_patent ON maint_events_raw (patent);
        """
        )
        conn.exec_driver_sql(
            """
        CREATE INDEX IF NOT EXISTS idx_maint_event_date ON maint_events_raw (event_date);
        """
        )

        conn.exec_driver_sql(
            """
        CREATE TABLE IF NOT EXISTS inactive_patents (
            patent     TEXT PRIMARY KEY,
            title      TEXT NOT NULL,
            grant_date DATE
        );
        """
        )
        conn.exec_driver_sql(
            """
        CREATE INDEX IF NOT EXISTS idx_inactive_patents_grant_date
        ON inactive_patents (grant_date);
        """
        )
        try:
            conn.exec_driver_sql(
                """
            CREATE INDEX IF NOT EXISTS idx_inactive_patents_title_trgm
            ON inactive_patents USING GIN (title gin_trgm_ops);
            """
            )
        except Exception:
            pass

        # ---- NEW: patents_index table (unified index with jurisdiction) ----
        conn.exec_driver_sql(
            """
        CREATE TABLE IF NOT EXISTS patents_index (
            jurisdiction    TEXT NOT NULL,
            patent_id       TEXT NOT NULL,
            title           TEXT,
            date            DATE,
            inactive_reason TEXT,
            PRIMARY KEY (jurisdiction, patent_id)
        );
        """
        )
        conn.exec_driver_sql(
            """
        CREATE INDEX IF NOT EXISTS patents_index_jur_idx
        ON patents_index (jurisdiction);
        """
        )
        conn.exec_driver_sql(
            """
        CREATE INDEX IF NOT EXISTS patents_index_jur_date_idx
        ON patents_index (jurisdiction, date);
        """
        )
        try:
            conn.exec_driver_sql(
                """
            CREATE INDEX IF NOT EXISTS patents_index_title_trgm
            ON patents_index USING GIN (title gin_trgm_ops);
            """
            )
        except Exception:
            pass


def seed_if_empty() -> None:
    return


def _year_bounds(
    year_from: Optional[int],
    year_to: Optional[int],
) -> tuple[Optional[int], Optional[int]]:
    if year_from and year_to and year_from > year_to:
        year_from, year_to = year_to, year_from
    return year_from, year_to


def search_patents(
    q: str,
    page: int = 1,
    per_page: int = 20,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    sort_by: str = "date",
    sort_dir: str = "desc",
    jurisdiction: str = "US",  # NEW: default keeps old behavior
) -> Tuple[List[InactivePatent], int]:
    """
    Search patents_index by title.

    - q is split into whitespace-separated tokens.
    - All tokens must appear somewhere in the title (logical AND).
    - Matching is case-insensitive (ILIKE).
    - jurisdiction defaults to 'US' for backward compatibility.
      Use 'ALL' to search across jurisdictions.
    """
    offset = (page - 1) * per_page
    year_from, year_to = _year_bounds(year_from, year_to)

    q = (q or "").strip()
    tokens = [t for t in re.split(r"\s+", q) if t]
    jurisdiction = (jurisdiction or "US").upper()

    with Session(engine) as s:
        # base condition (tokens -> AND)
        if tokens:
            cond = and_(*[PatentIndex.title.ilike(f"%{t}%") for t in tokens])
        else:
            cond = text("TRUE")

        # jurisdiction filter (unless ALL)
        if jurisdiction != "ALL":
            cond = cond & (PatentIndex.jurisdiction == jurisdiction)

        # year bounds apply to patents_index.date
        if year_from:
            cond = cond & (
                PatentIndex.date >= func.to_date(f"{year_from}-01-01", "YYYY-MM-DD")
            )
        if year_to:
            cond = cond & (
                PatentIndex.date <= func.to_date(f"{year_to}-12-31", "YYYY-MM-DD")
            )

        # ordering
        if (sort_by or "").lower() == "title":
            order_expr = func.lower(PatentIndex.title)
            if (sort_dir or "").lower() == "asc":
                order_by = [order_expr.asc(), PatentIndex.date.desc().nullslast()]
            else:
                order_by = [order_expr.desc(), PatentIndex.date.desc().nullslast()]
        else:
            if (sort_dir or "").lower() == "asc":
                order_by = [
                    PatentIndex.date.asc().nullsfirst(),
                    func.lower(PatentIndex.title).asc(),
                ]
            else:
                order_by = [
                    PatentIndex.date.desc().nullslast(),
                    func.lower(PatentIndex.title).asc(),
                ]

        total = (
            s.scalar(select(func.count()).select_from(PatentIndex).where(cond))
            or 0
        )

        rows = (
            s.scalars(
                select(PatentIndex)
                .where(cond)
                .order_by(*order_by)
                .offset(offset)
                .limit(per_page)
            ).all()
        )

        # Convert to InactivePatent objects (so server.py stays unchanged)
        out: List[InactivePatent] = []
        for r in rows:
            fake = InactivePatent()
            fake.patent = r.patent_id
            fake.title = r.title or ""
            fake.grant_date = r.date
            out.append(fake)

        return out, int(total)


def get_patent(number: str, jurisdiction: str = "US") -> InactivePatent | None:
    """
    Get one patent record from patents_index.

    - jurisdiction defaults to US to preserve old behavior.
    - jurisdiction=ALL will return the first match by patent_id (rare collisions).
    """
    jurisdiction = (jurisdiction or "US").upper()
    with Session(engine) as s:
        if jurisdiction == "ALL":
            r = (
                s.execute(
                    select(PatentIndex)
                    .where(PatentIndex.patent_id == number)
                    .limit(1)
                )
                .scalars()
                .first()
            )
        else:
            r = s.get(PatentIndex, {"jurisdiction": jurisdiction, "patent_id": number})

        if not r:
            return None

        fake = InactivePatent()
        fake.patent = r.patent_id
        fake.title = r.title or ""
        fake.grant_date = r.date
        return fake