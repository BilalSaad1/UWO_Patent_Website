from __future__ import annotations
from datetime import date
from typing import List, Tuple, Optional
import os

from sqlalchemy import create_engine, String, Date, select, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://uwo_patents:cumbersome@127.0.0.1:5432/patents",
)
engine = create_engine(DATABASE_URL, future=True, echo=False)


class Base(DeclarativeBase):
    pass


class InactivePatent(Base):
    __tablename__ = "inactive_patents"
    patent: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    grant_date: Mapped[date | None] = mapped_column(Date)


def init_db() -> None:
    """Ensure required objects exist in the target DB."""
    with engine.begin() as conn:
        # Extensions
        try:
            conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        except Exception:
            pass

        # Raw grants (1976–present)
        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS grants_raw (
            patent     TEXT PRIMARY KEY,
            title      TEXT NOT NULL,
            grant_date DATE
        );
        """)
        conn.exec_driver_sql("""
        CREATE INDEX IF NOT EXISTS idx_grants_raw_grant_date
        ON grants_raw (grant_date);
        """)
        try:
            conn.exec_driver_sql("""
            CREATE INDEX IF NOT EXISTS idx_grants_raw_title_trgm
            ON grants_raw USING GIN (title gin_trgm_ops);
            """)
        except Exception:
            pass

        # Raw maintenance fee events
        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS maint_events_raw (
            id         BIGSERIAL PRIMARY KEY,
            patent     TEXT NOT NULL,
            event_code TEXT NOT NULL,
            event_date DATE NOT NULL,
            details    TEXT
        );
        """)
        conn.exec_driver_sql("""
        CREATE INDEX IF NOT EXISTS idx_maint_patent ON maint_events_raw (patent);
        """)
        conn.exec_driver_sql("""
        CREATE INDEX IF NOT EXISTS idx_maint_event_date ON maint_events_raw (event_date);
        """)

        # Derived: inactive_patents (search surface)
        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS inactive_patents (
            patent     TEXT PRIMARY KEY,
            title      TEXT NOT NULL,
            grant_date DATE
        );
        """)
        conn.exec_driver_sql("""
        CREATE INDEX IF NOT EXISTS idx_inactive_patents_grant_date
        ON inactive_patents (grant_date);
        """)
        try:
            conn.exec_driver_sql("""
            CREATE INDEX IF NOT EXISTS idx_inactive_patents_title_trgm
            ON inactive_patents USING GIN (title gin_trgm_ops);
            """)
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
) -> Tuple[List[InactivePatent], int]:
    offset = (page - 1) * per_page
    year_from, year_to = _year_bounds(year_from, year_to)

    with Session(engine) as s:
        cond = InactivePatent.title.ilike(f"%{q}%") if q else text("TRUE")

        if year_from:
            cond = cond & (InactivePatent.grant_date >= func.to_date(f"{year_from}-01-01", "YYYY-MM-DD"))
        if year_to:
            cond = cond & (InactivePatent.grant_date <= func.to_date(f"{year_to}-12-31", "YYYY-MM-DD"))

        if (sort_by or "").lower() == "title":
            order_expr = func.lower(InactivePatent.title)
            if (sort_dir or "").lower() == "asc":
                order_by = [order_expr.asc(), InactivePatent.grant_date.desc().nullslast()]
            else:
                order_by = [order_expr.desc(), InactivePatent.grant_date.desc().nullslast()]
        else:
            if (sort_dir or "").lower() == "asc":
                order_by = [InactivePatent.grant_date.asc().nullsfirst(), func.lower(InactivePatent.title).asc()]
            else:
                order_by = [InactivePatent.grant_date.desc().nullslast(), func.lower(InactivePatent.title).asc()]

        total = s.scalar(select(func.count()).where(cond)) or 0

        rows = s.scalars(
            select(InactivePatent)
            .where(cond)
            .order_by(*order_by)
            .offset(offset)
            .limit(per_page)
        ).all()

        return rows, int(total)


def get_patent(number: str) -> InactivePatent | None:
    with Session(engine) as s:
        return s.get(InactivePatent, number)