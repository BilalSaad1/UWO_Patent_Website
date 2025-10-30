from dataclasses import dataclass
import os

@dataclass
class _Cfg:
    # Directory where ZIPs and extracted artifacts live
    data_dir: str = os.getenv("DATA_DIR", "data")

CFG = _Cfg()