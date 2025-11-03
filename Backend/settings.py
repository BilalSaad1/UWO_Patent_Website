from __future__ import annotations
import os
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()  # reads backend/.env if present

class Settings(BaseModel):
    cors_origins: List[str] = Field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    )
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///patents.db")

settings = Settings()