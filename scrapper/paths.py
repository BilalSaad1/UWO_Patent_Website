from __future__ import annotations
import os
from pathlib import Path
from .config import CFG

def ensure_dirs() -> dict[str, Path]:
    root = Path(CFG.data_dir)
    dl = root / "downloads"
    x = root / "extracted"
    os.makedirs(dl, exist_ok=True)
    os.makedirs(x, exist_ok=True)
    return {"root": root, "downloads": dl, "extracted": x}
