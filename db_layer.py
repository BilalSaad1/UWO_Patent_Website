from __future__ import annotations
from datetime import date
from typing import List, Tuple

from sqlalchemy import create_engine, String, Date, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from settings import settings

DATABASE_URL = settings.database_url
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, future=True, echo=False, connect_args=connect_args)

class Base(DeclarativeBase):
    pass

class InactivePatent(Base):
    __tablename__ = "inactive_patents"
    patent: Mapped[str] = mapped_column(String, primary_key=True)
    title:  Mapped[str] = mapped_column(String, nullable=False)
    grant_date: Mapped[date | None] = mapped_column(Date, nullable=True)

def init_db() -> None:
    Base.metadata.create_all(engine)

def seed_if_empty() -> None:
    with Session(engine) as s:
        count = s.scalar(select(func.count()).select_from(InactivePatent)) or 0
        if count == 0:
            s.add_all([
                InactivePatent(patent="US7654321", title="Example Patent Title", grant_date=date(2010, 6, 1)),
                InactivePatent(patent="US8000000", title="Polymer nozzle for additive manufacturing", grant_date=date(2011, 8, 16)),
                InactivePatent(patent="US9000001", title="Photovoltaic cell encapsulation method", grant_date=date(2015, 4, 14)),
            ])
            s.commit()

def search_patents(q: str, page: int = 1, per_page: int = 20) -> Tuple[List[InactivePatent], int]:
    offset = (page - 1) * per_page
    with Session(engine) as s:
        total = s.scalar(select(func.count()).where(InactivePatent.title.ilike(f"%{q}%"))) or 0
        rows = s.scalars(
            select(InactivePatent)
            .where(InactivePatent.title.ilike(f"%{q}%"))
            .order_by(InactivePatent.grant_date.desc().nullslast())
            .offset(offset)
            .limit(per_page)
        ).all()
        return rows, total

def get_patent(number: str) -> InactivePatent | None:
    with Session(engine) as s:
        return s.get(InactivePatent, number)