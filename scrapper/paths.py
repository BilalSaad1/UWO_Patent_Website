from __future__ import annotations
from pathlib import Path
from .config import CFG

# Base data directory (default "data/", can be overridden via CFG)
DATA_ROOT: Path = Path(CFG.data_dir).resolve()

# Subfolders
DOWNLOADS: Path = DATA_ROOT / "downloads"
EXTRACTED: Path = DATA_ROOT / "extracted"

# Ensure they exist
for p in (DOWNLOADS, EXTRACTED):
    p.mkdir(parents=True, exist_ok=True)