from __future__ import annotations
from datetime import date
from typing import List, Tuple
from sqlalchemy import create_engine, String, Date, select, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://uwo_patents:cumbersome@127.0.0.1:5432/patents")
engine = create_engine(DATABASE_URL, future=True, echo=False)

class Base(DeclarativeBase): pass

class InactivePatent(Base):
    __tablename__ = "inactive_patents"
    patent: Mapped[str] = mapped_column(String, primary_key=True)
    title:  Mapped[str] = mapped_column(String, nullable=False)
    grant_date: Mapped[date | None] = mapped_column(Date)

def init_db() -> None:
    # Tables created via SQL migration; nothing to do here.
    with engine.begin() as conn:
        conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

def seed_if_empty() -> None:
    # No seed; we’ll rely on real data
    return

def search_patents(q: str, page: int = 1, per_page: int = 20) -> Tuple[List[InactivePatent], int]:
    offset = (page - 1) * per_page
    with Session(engine) as s:
        # Use ILIKE + trigram index; later we can try similarity()
        cond = InactivePatent.title.ilike(f"%{q}%")
        total = s.scalar(select(func.count()).where(cond)) or 0
        rows = s.scalars(
            select(InactivePatent)
            .where(cond)
            .order_by(InactivePatent.grant_date.desc().nullslast())
            .offset(offset)
            .limit(per_page)
        ).all()
        return rows, total

def get_patent(number: str) -> InactivePatent | None:
    with Session(engine) as s:
        return s.get(InactivePatent, number)