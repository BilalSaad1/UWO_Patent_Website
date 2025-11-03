from __future__ import annotations
from datetime import date
from typing import List, Tuple, Optional

import os
from sqlalchemy import (
    create_engine, String, Date, select, func, text
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# --- DB engine ---
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://uwo_patents:cumbersome@127.0.0.1:5432/patents",
)
engine = create_engine(DATABASE_URL, future=True, echo=False)


# --- ORM base / models ---
class Base(DeclarativeBase):
    pass


class InactivePatent(Base):
    __tablename__ = "inactive_patents"
    patent: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    grant_date: Mapped[date | None] = mapped_column(Date)


# --- init / seed (no-op except extensions) ---
def init_db() -> None:
    # Ensure pg_trgm exists for fuzzy/ILIKE index usage (safe to run every start).
    with engine.begin() as conn:
        try:
            conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        except Exception:
            # If not Postgres or extension not allowed, ignore silently.
            pass


def seed_if_empty() -> None:
    return


# --- helpers ---
def _year_bounds(
    year_from: Optional[int],
    year_to: Optional[int],
) -> tuple[Optional[int], Optional[int]]:
    """Normalize/swap year bounds if needed."""
    if year_from and year_to and year_from > year_to:
        year_from, year_to = year_to, year_from
    return year_from, year_to


# --- main search API used by FastAPI ---
def search_patents(
    q: str,
    page: int = 1,
    per_page: int = 20,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    sort_by: str = "date",   # "date" | "title"
    sort_dir: str = "desc",  # "asc" | "desc"
) -> Tuple[List[InactivePatent], int]:
    """
    Title keyword search over inactive_patents with optional year range and sorting.
    Returns (rows, total).
    """
    offset = (page - 1) * per_page
    year_from, year_to = _year_bounds(year_from, year_to)

    with Session(engine) as s:
        # WHERE title ILIKE '%q%'
        cond = InactivePatent.title.ilike(f"%{q}%")

        # Year filters operate on grant_date (inclusive range)
        if year_from:
            cond = cond & (InactivePatent.grant_date >= func.to_date(f"{year_from}-01-01", "YYYY-MM-DD"))
        if year_to:
            cond = cond & (InactivePatent.grant_date <= func.to_date(f"{year_to}-12-31", "YYYY-MM-DD"))

        # ORDER BY
        if (sort_by or "").lower() == "title":
            # Case-insensitive title sort; grant_date as tiebreaker
            order_expr = func.lower(InactivePatent.title)
            if (sort_dir or "").lower() == "asc":
                order_by = [order_expr.asc(), InactivePatent.grant_date.desc().nullslast()]
            else:
                order_by = [order_expr.desc(), InactivePatent.grant_date.desc().nullslast()]
        else:
            # Default: by grant_date, then title
            if (sort_dir or "").lower() == "asc":
                order_by = [InactivePatent.grant_date.asc().nullsfirst(), func.lower(InactivePatent.title).asc()]
            else:
                order_by = [InactivePatent.grant_date.desc().nullslast(), func.lower(InactivePatent.title).asc()]

        # TOTAL
        total = s.scalar(select(func.count()).where(cond)) or 0

        # PAGE
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