from __future__ import annotations
from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from settings import settings
import db_layer as db

app = FastAPI(title="UWO Patent Website API", version="0.2.0")

explicit = [o.strip() for o in settings.cors_origins if o and o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=explicit,
    allow_origin_regex=r"^https://[a-z0-9-]+\.trycloudflare\.com$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PatentHit(BaseModel):
    patent: str
    title: str
    grant_date: Optional[date] = None

class SearchResponse(BaseModel):
    q: str
    page: int
    per_page: int
    total: int
    results: List[PatentHit]

@app.on_event("startup")
def _startup():
    db.init_db()
    db.seed_if_empty()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/stats")
def stats():
    _, total = db.search_patents(q="", page=1, per_page=1)
    return {"total_inactive_patents": total}

@app.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1, max_length=128),
    page: int = Query(1, ge=1, le=1000),
    per_page: int = Query(20, ge=1, le=100),
    year_from: Optional[int] = Query(None, ge=1900, le=2100),
    year_to:   Optional[int] = Query(None, ge=1900, le=2100),
    sort_by:   str = Query("date", pattern="^(date|title)$"),
    sort_dir:  str = Query("desc", pattern="^(asc|desc)$"),
):
    rows, total = db.search_patents(
        q=q,
        page=page,
        per_page=per_page,
        year_from=year_from,
        year_to=year_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return SearchResponse(
        q=q,
        page=page,
        per_page=per_page,
        total=total,
        results=[PatentHit(patent=r.patent, title=r.title, grant_date=r.grant_date) for r in rows],
    )

@app.get("/patents/{number}", response_model=PatentHit)
def get_patent(number: str):
    r = db.get_patent(number)
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    return PatentHit(patent=r.patent, title=r.title, grant_date=r.grant_date)