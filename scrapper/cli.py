from argparse import ArgumentParser
from pathlib import Path
from sqlalchemy import create_engine
import os
import re

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=False)

if not os.getenv("DATABASE_URL"):
    ROOT = Path(__file__).resolve().parents[1]   
    load_dotenv(ROOT / ".env", override=True)
    load_dotenv(ROOT / "backend" / ".env", override=True)

from .paths import DOWNLOADS
from .grants import load_grants
from .maintenance import load_maintenance
from .derive import rebuild_inactive

def get_engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        cwd = os.getcwd()
        raise RuntimeError(
            "DATABASE_URL not set. Tried: cwd/find_dotenv, project .env, backend/.env. "
            f"cwd={cwd}. Consider: `$env:DATABASE_URL=...` or create .env at repo root."
        )
    return create_engine(url, future=True)

def _is_grants_zip(p: Path) -> bool:
    n = p.name.lower()
    return (n.endswith(".zip") and
            ("ipg" in n or "pg" in n or "ptblxml" in n or re.search(r"grant|xml|sgm", n)))

def _is_maint_zip(p: Path) -> bool:
    n = p.name.lower()
    return (n.endswith(".zip") and
            ("maint" in n or "ptmnfee" in n or "maintenance" in n))

def cmd_build(args):
    eng = get_engine()
    g_count = load_grants(Path(args.grants_zip), eng)
    m_count = load_maintenance(Path(args.maint_zip), eng)
    i_count = rebuild_inactive(eng)
    print(f"grants: {g_count:,}, maint: {m_count:,}, inactive now: {i_count:,}")

def cmd_latest(args):
    eng = get_engine()
    zips = sorted(DOWNLOADS.glob("*.zip"))
    grants_zip = next(z for z in zips if "ipg" in z.name.lower() or "ptblxml" in z.name.lower() or "pg" in z.name.lower())
    maint_zip  = next(z for z in zips if "maint" in z.name.lower() or "ptmnfee" in z.name.lower())
    g_count = load_grants(grants_zip, eng)
    m_count = load_maintenance(maint_zip, eng)
    i_count = rebuild_inactive(eng)
    print(f"grants: {g_count:,}, maint: {m_count:,}, inactive now: {i_count:,}")

def cmd_ingest_dir(args):
    """Ingest ALL .zip files in a directory (recursively). Run derive once at the end."""
    eng = get_engine()
    root = Path(args.dir).resolve()
    zips = sorted(root.rglob("*.zip"))
    g_total = m_total = 0

    for z in zips:
        n = z.name
        try:
            if _is_grants_zip(z):
                c = load_grants(z, eng)
                g_total += c
                print(f"[grants] {n}: +{c:,} (total {g_total:,})")
            elif _is_maint_zip(z):
                c = load_maintenance(z, eng)
                m_total += c
                print(f"[maint]  {n}: +{c:,} (total {m_total:,})")
            else:
                continue
        except Exception as e:
            print(f"[skip] {n}: {e}")

    i_count = rebuild_inactive(eng)
    print(f"== DONE == grants: {g_total:,}, maint: {m_total:,}, inactive now: {i_count:,}")

if __name__ == "__main__":
    ap = ArgumentParser("scrapper")
    sp = ap.add_subparsers(dest="cmd", required=True)

    b = sp.add_parser("build", help="ingest specific ZIP files and derive")
    b.add_argument("--grants-zip", required=True)
    b.add_argument("--maint-zip", required=True)
    b.set_defaults(func=cmd_build)

    l = sp.add_parser("latest", help="ingest the two ZIPs present in data/downloads/")
    l.set_defaults(func=cmd_latest)

    d = sp.add_parser("ingest-dir", help="ingest ALL grants/maintenance ZIPs in a directory (recursively)")
    d.add_argument("--dir", required=True)
    d.set_defaults(func=cmd_ingest_dir)

    args = ap.parse_args()
    args.func(args)