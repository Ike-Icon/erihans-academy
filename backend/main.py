"""
Erihans Wealth & Wellness Academy - backend API

Run locally:
    pip install -r requirements.txt
    uvicorn main:app --reload

The frontend (frontend/index.html) posts to these endpoints for the
enrollment form and the newsletter signup. Data is stored in a local
SQLite file (erihans.db), created automatically on first run.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import FastAPI  # type: ignore[import-not-found]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import-not-found]
from fastapi.staticfiles import StaticFiles  # type: ignore[import-not-found]
from pydantic import BaseModel, EmailStr, Field  # type: ignore[import-not-found]
from sqlmodel import Field as SQLField  # type: ignore[import-not-found]
from sqlmodel import Session, SQLModel, create_engine, select  # type: ignore[import-not-found]

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

# Locally this falls back to a SQLite file next to this script.
# In production, set the DATABASE_URL environment variable to a Postgres URL
# (Render and Railway both give you one from their managed Postgres add-on).
# Render's env var comes back as "postgres://..." but SQLAlchemy 2.x wants
# "postgresql://...", hence the swap below.
raw_url = os.environ.get("DATABASE_URL", "sqlite:///erihans.db")
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)
DATABASE_URL = raw_url

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


class EnrollmentInquiry(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str
    email: str
    phone: Optional[str] = None
    program: Optional[str] = None
    message: Optional[str] = None
    created_at: datetime = SQLField(default_factory=datetime.utcnow)


class NewsletterSubscriber(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    email: str = SQLField(unique=True, index=True)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


# ---------------------------------------------------------------------------
# Request/response schemas
# ---------------------------------------------------------------------------

PROGRAM_CHOICES = {
    "financial_education",
    "wealth_creation",
    "money_management",
    "investment_entrepreneurship",
    "wellness",
    "not_sure",
}


class EnrollmentRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=30)
    program: Optional[str] = Field(default="not_sure")
    message: Optional[str] = Field(default=None, max_length=1000)


class NewsletterRequest(BaseModel):
    email: EmailStr


class ProgramOut(BaseModel):
    id: str
    name: str
    summary: str


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Erihans Wealth & Wellness Academy API",
    version="1.0.0",
    description="Backend for the enrollment form, newsletter signup and program listing.",
)

# CORS only matters if the frontend is hosted on a different origin than the
# API (Option 2 in the README). When FastAPI serves the frontend itself
# (Option 1, the recommended setup), requests are same-origin and this
# middleware is inactive in practice. Left in place, with a wildcard, for
# local development convenience — replace "*" with your real domain if you
# do split the frontend and backend across two hosts.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "*",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/programs", response_model=list[ProgramOut])
def list_programs() -> list[ProgramOut]:
    return [
        ProgramOut(
            id="financial_education",
            name="Financial education",
            summary="Understand how money works: interest, inflation, credit and tax.",
        ),
        ProgramOut(
            id="wealth_creation",
            name="Wealth creation",
            summary="Build more than one stream of income and grow what you earn.",
        ),
        ProgramOut(
            id="money_management",
            name="Money management",
            summary="Budget on purpose, pay down debt in order, build an emergency fund.",
        ),
        ProgramOut(
            id="investment_entrepreneurship",
            name="Investment & entrepreneurship",
            summary="Invest with a plan and learn what it takes to run a small business.",
        ),
        ProgramOut(
            id="wellness",
            name="Wellness",
            summary="Manage the stress that comes with money, so progress doesn't cost your health.",
        ),
    ]


@app.post("/api/enroll", status_code=201)
def submit_enrollment(payload: EnrollmentRequest) -> dict:
    program = payload.program if payload.program in PROGRAM_CHOICES else "not_sure"

    with Session(engine) as session:
        record = EnrollmentInquiry(
            name=payload.name.strip(),
            email=str(payload.email),
            phone=payload.phone,
            program=program,
            message=payload.message,
        )
        session.add(record)
        session.commit()
        session.refresh(record)

    # In production: send a confirmation email and notify the admissions team here.
    return {"status": "received", "id": record.id}


@app.post("/api/newsletter", status_code=201)
def subscribe_newsletter(payload: NewsletterRequest) -> dict:
    email = str(payload.email)

    with Session(engine) as session:
        existing = session.exec(
            select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
        ).first()
        if existing:
            return {"status": "already_subscribed"}

        record = NewsletterSubscriber(email=email)
        session.add(record)
        session.commit()

    return {"status": "subscribed"}


@app.get("/api/admin/enrollments", response_model=list[EnrollmentInquiry])
def list_enrollments() -> list[EnrollmentInquiry]:
    """Basic listing endpoint for admissions staff.
    Add authentication before using this outside local development."""
    with Session(engine) as session:
        return session.exec(select(EnrollmentInquiry)).all()


# ---------------------------------------------------------------------------
# Serve the frontend
# ---------------------------------------------------------------------------
# This must be the LAST thing registered on the app: StaticFiles with
# html=True catches every path that isn't matched above (including "/"),
# so any /api/* route defined after this point would be unreachable.
# Resolved relative to this file, not the working directory, so it works
# the same whether you run `uvicorn main:app` from backend/ or from a
# deploy platform that uses a different working directory.
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
