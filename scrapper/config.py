from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    # Where to save downloads/extracted files (kept out of git)
    data_dir: str = os.getenv("SCRAP_DATA_DIR", "data")

    # Preferred: direct ZIP URLs (bulletproof)
    maint_zip_url: str | None = os.getenv("MAINT_ZIP_URL") or None
    biblio_zip_url: str | None = os.getenv("BIBLIO_ZIP_URL") or None

    # Fallback: ODP product IDs (we'll try to discover the latest ZIP link)
    maint_product_id: str = os.getenv("MAINT_PRODUCT_ID", "ptmnfee2")
    biblio_product_id: str = os.getenv("BIBLIO_PRODUCT_ID", "ptblxml")
    odp_from: str | None = os.getenv("ODP_FROM_DATE") or None   # YYYY-MM-DD
    odp_to: str | None = os.getenv("ODP_TO_DATE") or None       # YYYY-MM-DD

CFG = Config()