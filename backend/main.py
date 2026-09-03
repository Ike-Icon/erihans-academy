import os
import secrets
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Field as SQLField
from sqlmodel import Session, SQLModel, create_engine, select

BASE_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
raw_url = os.environ.get("DATABASE_URL", "sqlite:///erihans.db")
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)
DATABASE_URL = raw_url

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


# ---------------------------------------------------------------------------
# Admin authentication
# ---------------------------------------------------------------------------
# Protects /api/admin/* routes with a username + password prompt (HTTP Basic
# Auth — the browser shows a native login popup, no extra frontend needed).
# Set these as environment variables before deploying. Locally, sensible
# defaults are used so /api/admin/enrollments still works out of the box —
# but change them (or set real env vars) before this goes anywhere public.
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "adm1npass")

security = HTTPBasic()


def require_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    # secrets.compare_digest avoids leaking timing information about how
    # many characters matched, which a plain "==" comparison would do.
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# ---------------------------------------------------------------------------
# Database tables
# ---------------------------------------------------------------------------
class EnrollmentInquiry(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str
    email: str
    phone: Optional[str] = None
    program: Optional[str] = None
    message: Optional[str] = None
    created_at: datetime = SQLField(default_factory=datetime.utcnow)


class ContactMessage(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str
    email: str
    message: str
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

# One entry per program page under templates/pages/programs/.
PROGRAM_CHOICES = {
    "financial_education",
    "money_management",
    "investment_education",
    "entrepreneurship",
    "wealth_creation",
    "wellness",
    "not_sure",
}


class EnrollmentRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=30)
    program: Optional[str] = Field(default="not_sure")
    message: Optional[str] = Field(default=None, max_length=1000)


class ContactRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    message: str = Field(min_length=1, max_length=2000)


class NewsletterRequest(BaseModel):
    email: EmailStr


class ProgramOut(BaseModel):
    id: str
    name: str
    summary: str
    url: str


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Erihans Wealth & Wellness Academy",
    version="2.0.0",
    description="Backend for the 12-page site: page rendering plus the registration, contact and newsletter forms.",
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# CORS only matters if you ever split the frontend onto a different origin
# than this API (see README). With everything served from this one app,
# requests are same-origin and this middleware is inactive in practice.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup() -> None:
    init_db()


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.get("/")
def page_home(request: Request):
    return templates.TemplateResponse(request, "pages/home.html", {"active": "home"})


@app.get("/about")
def page_about(request: Request):
    return templates.TemplateResponse(request, "pages/about.html", {"active": "about"})


@app.get("/programs/financial-education")
def page_program_financial_education(request: Request):
    return templates.TemplateResponse(
        request, "pages/programs/financial-education.html", {"active": "programs"}
    )


@app.get("/programs/money-management")
def page_program_money_management(request: Request):
    return templates.TemplateResponse(
        request, "pages/programs/money-management.html", {"active": "programs"}
    )


@app.get("/programs/investment-education")
def page_program_investment_education(request: Request):
    return templates.TemplateResponse(
        request, "pages/programs/investment-education.html", {"active": "programs"}
    )


@app.get("/programs/entrepreneurship")
def page_program_entrepreneurship(request: Request):
    return templates.TemplateResponse(
        request, "pages/programs/entrepreneurship.html", {"active": "programs"}
    )


@app.get("/programs/wealth-creation")
def page_program_wealth_creation(request: Request):
    return templates.TemplateResponse(
        request, "pages/programs/wealth-creation.html", {"active": "programs"}
    )


@app.get("/programs/wellness")
def page_program_wellness(request: Request):
    return templates.TemplateResponse(
        request, "pages/programs/wellness.html", {"active": "programs"}
    )


@app.get("/courses")
def page_courses(request: Request):
    return templates.TemplateResponse(request, "pages/courses.html", {"active": "courses"})


@app.get("/events")
def page_events(request: Request):
    return templates.TemplateResponse(request, "pages/events.html", {"active": "events"})


@app.get("/contact")
def page_contact(request: Request):
    return templates.TemplateResponse(request, "pages/contact.html", {"active": "contact"})


@app.get("/register")
def page_register(request: Request):
    return templates.TemplateResponse(request, "pages/register.html", {"active": "register"})


# ---------------------------------------------------------------------------
# API — health check + program listing
# ---------------------------------------------------------------------------

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
            url="/programs/financial-education",
        ),
        ProgramOut(
            id="money_management",
            name="Money management",
            summary="Budget on purpose, pay down debt in order, build an emergency fund.",
            url="/programs/money-management",
        ),
        ProgramOut(
            id="investment_education",
            name="Investment education",
            summary="Invest with a plan that matches your timeline and risk appetite.",
            url="/programs/investment-education",
        ),
        ProgramOut(
            id="entrepreneurship",
            name="Entrepreneurship",
            summary="What it takes to start and run a small business without guessing.",
            url="/programs/entrepreneurship",
        ),
        ProgramOut(
            id="wealth_creation",
            name="Wealth creation",
            summary="Build more than one stream of income and grow what you earn.",
            url="/programs/wealth-creation",
        ),
        ProgramOut(
            id="wellness",
            name="Wellness",
            summary="Manage the stress that comes with money, so progress doesn't cost your health.",
            url="/programs/wellness",
        ),
    ]


# ---------------------------------------------------------------------------
# API — forms
# ---------------------------------------------------------------------------

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


@app.post("/api/contact", status_code=201)
def submit_contact(payload: ContactRequest) -> dict:
    with Session(engine) as session:
        record = ContactMessage(
            name=payload.name.strip(),
            email=str(payload.email),
            message=payload.message.strip(),
        )
        session.add(record)
        session.commit()
        session.refresh(record)

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


# ---------------------------------------------------------------------------
# API — admin (password protected)
# ---------------------------------------------------------------------------

@app.get("/api/admin/enrollments", response_model=list[EnrollmentInquiry])
def list_enrollments(_: str = Depends(require_admin)) -> list[EnrollmentInquiry]:
    """Enrollment inquiries, for admissions staff only."""
    with Session(engine) as session:
        return session.exec(select(EnrollmentInquiry)).all()


@app.get("/api/admin/messages", response_model=list[ContactMessage])
def list_contact_messages(_: str = Depends(require_admin)) -> list[ContactMessage]:
    """Contact form messages, for admissions staff only."""
    with Session(engine) as session:
        return session.exec(select(ContactMessage)).all()


# ---------------------------------------------------------------------------
# Static files (css, js, images) — mounted at /static, NOT at "/", so it
# never competes with the page routes above.
# ---------------------------------------------------------------------------
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
