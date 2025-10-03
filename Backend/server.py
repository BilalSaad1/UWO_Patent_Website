from __future__ import annotations
from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from settings import settings
import db_layer as db


app = FastAPI(title="UWO Patent Website API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["GET"],
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

@app.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=2, max_length=128),
    page: int = Query(1, ge=1, le=1000),
    per_page: int = Query(20, ge=1, le=100),
):
    rows, total = db.search_patents(q, page, per_page)
    results = [PatentHit(patent=r.patent, title=r.title, grant_date=r.grant_date) for r in rows]
    return SearchResponse(q=q, page=page, per_page=per_page, total=total, results=results)

@app.get("/patents/{number}", response_model=PatentHit)
def get_patent(number: str):
    r = db.get_patent(number)
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    return PatentHit(patent=r.patent, title=r.title, grant_date=r.grant_date)