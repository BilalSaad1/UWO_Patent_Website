from argparse import ArgumentParser
from pathlib import Path
from sqlalchemy import create_engine
import os

from dotenv import load_dotenv
load_dotenv()
from .paths import DOWNLOADS
from .grants import load_grants
from .maintenance import load_maintenance
from .derive import rebuild_inactive

def get_engine():
    url = os.getenv("DATABASE_URL")
    assert url, "DATABASE_URL not set"
    return create_engine(url, future=True)

def cmd_build(args):
    eng = get_engine()
    g_count = load_grants(Path(args.grants_zip), eng)
    m_count = load_maintenance(Path(args.maint_zip), eng)
    i_count = rebuild_inactive(eng)
    print(f"grants: {g_count}, maint: {m_count}, inactive now: {i_count}")

def cmd_latest(args):
    # Convenience if you drop the two weekly ZIPs into data/downloads/
    eng = get_engine()
    zips = sorted(DOWNLOADS.glob("*.zip"))
    grants_zip = next(z for z in zips if "ipg" in z.name.lower() or "ptblxml" in z.name.lower())
    maint_zip  = next(z for z in zips if "maint" in z.name.lower() or "ptmnfee" in z.name.lower())
    g_count = load_grants(grants_zip, eng)
    m_count = load_maintenance(maint_zip, eng)
    i_count = rebuild_inactive(eng)
    print(f"grants: {g_count}, maint: {m_count}, inactive now: {i_count}")

if __name__ == "__main__":
    ap = ArgumentParser("scrapper")
    sp = ap.add_subparsers(dest="cmd", required=True)

    b = sp.add_parser("build", help="ingest specific ZIP files and derive")
    b.add_argument("--grants-zip", required=True)
    b.add_argument("--maint-zip", required=True)
    b.set_defaults(func=cmd_build)

    l = sp.add_parser("latest", help="ingest the two ZIPs present in data/downloads/")
    l.set_defaults(func=cmd_latest)

    args = ap.parse_args()
    args.func(args)