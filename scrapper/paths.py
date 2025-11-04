from __future__ import annotations
from pathlib import Path
from .config import CFG

DATA_ROOT: Path = Path(CFG.data_dir).resolve()

DOWNLOADS: Path = DATA_ROOT / "downloads"
EXTRACTED: Path = DATA_ROOT / "extracted"

for p in (DOWNLOADS, EXTRACTED):
    p.mkdir(parents=True, exist_ok=True)