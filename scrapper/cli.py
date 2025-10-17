from __future__ import annotations
import argparse
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

from backend.settings import settings
from backend.db_layer import Base, InactivePatent

from .paths import ensure_dirs
from . import maintenance as m
from . import grants as g
from .derive import reduce_inactive

def _engine():
    url = settings.database_url
    return create_engine(url, future=True, echo=False)

def cmd_fetch(_):
    ensure_dirs()
    mz = m.fetch_latest_zip()
    gz = g.fetch_latest_zip()
    print(f"Downloaded:\n  {mz}\n  {gz}")

def cmd_build(_):
    paths = ensure_dirs()
    mz = max((p for p in paths["downloads"].glob("ptmnfee2*.zip")), default=None)
    gz = max((p for p in paths["downloads"].glob("ptblxml*.zip")), default=None)
    if not mz or not gz:
        raise SystemExit("Missing downloads. Run: python -m scrapper.cli fetch")
    events = list(m.parse_zip(mz))
    biblio_map = g.to_map(g.parse_zip(gz))
    inactive_rows, total_seen = reduce_inactive(events, biblio_map)
    print(f"Derived {len(inactive_rows)} inactive out of {total_seen} patents with maintenance events.")

    eng = _engine()
    Base.metadata.create_all(eng)
    with Session(eng) as s:
        s.execute(delete(InactivePatent))
        s.bulk_save_objects([
            InactivePatent(patent=row.patent, title=row.title, grant_date=row.grant_date)
            for row in inactive_rows
        ])
        s.commit()
    print("DB updated: inactive_patents replaced.")

def cmd_devseed(_):
    eng = _engine()
    Base.metadata.create_all(eng)
    demos = [
        InactivePatent(patent="US7654321", title="Example Patent Title"),
        InactivePatent(patent="US8000000", title="Polymer nozzle for additive manufacturing"),
        InactivePatent(patent="US9000001", title="Photovoltaic cell encapsulation method"),
    ]
    with Session(eng) as s:
        s.execute(delete(InactivePatent))
        s.bulk_save_objects(demos)
        s.commit()
    print("DB updated with demo rows.")

def main():
    ap = argparse.ArgumentParser(prog="scrapper", description="USPTO inactive-patent scrapper")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("fetch", help="Download latest maintenance + bibliographic ZIPs").set_defaults(func=cmd_fetch)
    sub.add_parser("build", help="Parse and load inactive_patents into DB").set_defaults(func=cmd_build)
    sub.add_parser("dev-seed", help="Write demo rows").set_defaults(func=cmd_devseed)
    args = ap.parse_args()
    if not getattr(args, "cmd", None):
        ap.print_help(); return
    args.func(args)

if __name__ == "__main__":
    main()
from __future__ import annotations
import argparse
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

from backend.settings import settings
from backend.db_layer import Base, InactivePatent

from .paths import ensure_dirs
from . import maintenance as m
from . import grants as g
from .derive import reduce_inactive

def _engine():
    url = settings.database_url
    return create_engine(url, future=True, echo=False)

def cmd_fetch(_):
    ensure_dirs()
    mz = m.fetch_latest_zip()
    gz = g.fetch_latest_zip()
    print(f"Downloaded:\n  {mz}\n  {gz}")

def cmd_build(_):
    paths = ensure_dirs()
    mz = max((p for p in paths["downloads"].glob("ptmnfee2*.zip")), default=None)
    gz = max((p for p in paths["downloads"].glob("ptblxml*.zip")), default=None)
    if not mz or not gz:
        raise SystemExit("Missing downloads. Run: python -m scrapper.cli fetch")
    events = list(m.parse_zip(mz))
    biblio_map = g.to_map(g.parse_zip(gz))
    inactive_rows, total_seen = reduce_inactive(events, biblio_map)
    print(f"Derived {len(inactive_rows)} inactive out of {total_seen} patents with maintenance events.")

    eng = _engine()
    Base.metadata.create_all(eng)
    with Session(eng) as s:
        s.execute(delete(InactivePatent))
        s.bulk_save_objects([
            InactivePatent(patent=row.patent, title=row.title, grant_date=row.grant_date)
            for row in inactive_rows
        ])
        s.commit()
    print("DB updated: inactive_patents replaced.")

def cmd_devseed(_):
    eng = _engine()
    Base.metadata.create_all(eng)
    demos = [
        InactivePatent(patent="US7654321", title="Example Patent Title"),
        InactivePatent(patent="US8000000", title="Polymer nozzle for additive manufacturing"),
        InactivePatent(patent="US9000001", title="Photovoltaic cell encapsulation method"),
    ]
    with Session(eng) as s:
        s.execute(delete(InactivePatent))
        s.bulk_save_objects(demos)
        s.commit()
    print("DB updated with demo rows.")

def main():
    ap = argparse.ArgumentParser(prog="scrapper", description="USPTO inactive-patent scrapper")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("fetch", help="Download latest maintenance + bibliographic ZIPs").set_defaults(func=cmd_fetch)
    sub.add_parser("build", help="Parse and load inactive_patents into DB").set_defaults(func=cmd_build)
    sub.add_parser("dev-seed", help="Write demo rows").set_defaults(func=cmd_devseed)
    args = ap.parse_args()
    if not getattr(args, "cmd", None):
        ap.print_help(); return
    args.func(args)

if __name__ == "__main__":
    main()
