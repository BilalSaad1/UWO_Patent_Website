from dataclasses import dataclass
import os

@dataclass
class _Cfg:
    data_dir: str = os.getenv("DATA_DIR", "data")

CFG = _Cfg()