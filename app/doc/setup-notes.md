# SupportIQ — Setup & Learning Notes

> A personal study guide for this project: how it was set up, what every package does, how the code works, and how to explain it in an interview.

**Stack:** Python 3.14 · FastAPI · Uvicorn · Pydantic v2 · SQLAlchemy 2.0 · SQLite · Alembic

---

## Table of Contents

1. [What is this project?](#1-what-is-this-project)
2. [Setup from scratch (step by step)](#2-setup-from-scratch-step-by-step)
3. [Packages — what and why](#3-packages--what-and-why)
4. [Folder structure — what goes where](#4-folder-structure--what-goes-where)
5. [How a request flows through the app](#5-how-a-request-flows-through-the-app)
6. [Core concepts explained with our code](#6-core-concepts-explained-with-our-code)
7. [Database migrations with Alembic](#7-database-migrations-with-alembic)
8. [Environment variables & config](#8-environment-variables--config)
9. [Common errors & fixes](#9-common-errors--fixes)
10. [Interview questions & answers](#10-interview-questions--answers)
11. [Command cheat sheet](#11-command-cheat-sheet)

---

## 1. What is this project?

**SupportIQ** is a REST API for customer support tickets. A customer submits a ticket (subject + message), it is stored in a database, and later an AI layer will analyze it (category, sentiment, priority, summary).

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/health` | GET | Check the server is alive |
| `/api/v1/tickets` | POST | Create a new ticket |

> **Interview line:** "It's a layered FastAPI backend: routes handle HTTP, services hold business logic, SQLAlchemy models map to database tables, and Pydantic schemas validate input and shape output."

---

## 2. Setup from scratch (step by step)

### Step 1 — Check Python is installed

```powershell
python --version
```

### Step 2 — Create the project folder and a virtual environment

```powershell
mkdir SupportIQ
cd SupportIQ
python -m venv .venv
```

**What is a virtual environment?**
An isolated folder (`.venv/`) with its own Python and its own installed packages.

**Why use it?**
- Project A may need FastAPI 0.100, project B needs 0.162 — each venv keeps its own versions.
- Your global Python stays clean.
- `requirements.txt` can be generated from exactly what this project uses.

### Step 3 — Activate the virtual environment

```powershell
# Windows PowerShell
.venv\Scripts\activate

# Git Bash / Linux / macOS
source .venv/Scripts/activate     # Git Bash on Windows
source .venv/bin/activate         # Linux / macOS
```

You know it worked when you see `(.venv)` at the start of your terminal line.

> If PowerShell says *"running scripts is disabled"*, run once:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### Step 4 — Install packages

```powershell
pip install "fastapi[standard]" sqlalchemy alembic pydantic-settings pymysql
```

`fastapi[standard]` = FastAPI **plus** a recommended bundle of extras (Uvicorn server, CLI, email validation, form parsing, etc.). The `[...]` part is called an **extra**.

### Step 5 — Save the package list

```powershell
pip freeze > requirements.txt
```

Anyone can now recreate the exact same environment with:

```powershell
pip install -r requirements.txt
```

> ⚠️ **Windows gotcha:** In Windows PowerShell 5.1, `>` saves the file as **UTF-16**. Git then treats it as a binary file (no readable diffs). Safer command:
> `pip freeze | Out-File -Encoding utf8 requirements.txt`

### Step 6 — Create `.gitignore`

```
.venv/
__pycache__/
*.py[cod]
.env
supportiq.db
```

**Why?** Never commit: the virtual environment (huge, machine-specific), Python cache files, secrets (`.env`), or the local database file.

### Step 7 — Run the server

```powershell
python -m uvicorn app.main:app --reload
```

| Part | Meaning |
|---|---|
| `python -m uvicorn` | Run Uvicorn using the venv's Python (avoids "command not found") |
| `app.main` | The module: `app/main.py` |
| `:app` | The variable inside that file: `app = FastAPI(...)` |
| `--reload` | Restart automatically when code changes (**development only**) |

Alternative using the FastAPI CLI: `fastapi dev app/main.py`

### Step 8 — Open the auto-generated docs

| URL | What it is |
|---|---|
| http://127.0.0.1:8000/docs | **Swagger UI** — interactive; try endpoints from the browser |
| http://127.0.0.1:8000/redoc | **ReDoc** — clean read-only documentation |
| http://127.0.0.1:8000/openapi.json | The raw **OpenAPI** schema both are built from |

FastAPI generates these **automatically** from your routes, type hints and Pydantic models.

---

## 3. Packages — what and why

`requirements.txt` has ~60 packages, but you only **chose** a few. The rest were installed automatically because those packages depend on them.

### 3.1 Packages you use directly ⭐

| Package | What it is | Why we need it |
|---|---|---|
| **fastapi** | The web framework | Define routes, validation, dependency injection, auto docs |
| **uvicorn** | ASGI web server | Actually runs the app and listens for HTTP requests. FastAPI is just code; Uvicorn serves it |
| **pydantic** | Data validation library | Validates request bodies (`TicketCreate`) and shapes responses (`TicketResponse`) |
| **pydantic-settings** | Settings from env vars | Load config (`DATABASE_URL`, etc.) from `.env` into a typed class |
| **SQLAlchemy** | ORM + SQL toolkit | Talk to the database using Python classes instead of raw SQL |
| **alembic** | Migration tool (by SQLAlchemy's author) | Version-control the database schema (add columns, tables safely) |
| **python-dotenv** | Reads `.env` files | Loads environment variables from a file during development |
| **PyMySQL** | MySQL driver (pure Python) | Lets SQLAlchemy connect to MySQL later. Not used yet — we use SQLite now |

### 3.2 FastAPI's foundations (installed with FastAPI)

| Package | Role |
|---|---|
| **starlette** | The lightweight ASGI toolkit FastAPI is built on (routing, requests, responses, middleware) |
| **pydantic_core** | Pydantic's validation engine, written in Rust — that's why Pydantic v2 is fast |
| **annotated-types**, **typing-inspection**, **typing_extensions**, **annotated-doc** | Helpers for reading Python type hints at runtime |
| **anyio** | Async compatibility layer (runs on asyncio) |
| **opentelemetry-api** | Tracing/observability hooks used by FastAPI internally |

> **Interview line:** "FastAPI = Starlette (web part) + Pydantic (data part) + type hints."

### 3.3 Extras from `fastapi[standard]`

| Package | Role |
|---|---|
| **fastapi-cli** | The `fastapi dev` / `fastapi run` commands |
| **httpx** | Async HTTP client — used by FastAPI's `TestClient` for testing |
| **email-validator** (+ **dnspython**) | Needed for Pydantic's `EmailStr` type |
| **python-multipart** | Needed to receive form data and file uploads |
| **Jinja2** (+ **MarkupSafe**) | HTML templating, if you ever return HTML pages |
| **httptools** | Fast HTTP parser used by Uvicorn |
| **watchfiles** | Detects file changes for `--reload` |
| **websockets** | WebSocket support in Uvicorn |
| **PyYAML** | Lets Uvicorn read YAML logging config |
| **h11** | Pure-Python HTTP/1.1 implementation used by Uvicorn |
| **fastapi-cloud-cli** | Deploy to FastAPI Cloud (`fastapi deploy`) |

### 3.4 Indirect dependencies (you never import these)

| Group | Packages | Pulled in by |
|---|---|---|
| CLI look & feel | `typer`, `click`, `rich`, `rich-toolkit`, `Pygments`, `markdown-it-py`, `mdurl`, `colorama`, `shellingham` | fastapi-cli |
| Cloud deploy helpers | `sentry-sdk`, `rignore`, `fastar`, `agent-detector`, `detect-installer` | fastapi-cloud-cli |
| Telemetry | `opentelemetry-*`, `protobuf`, `googleapis-common-protos` | OpenTelemetry exporter |
| HTTP plumbing | `httpcore`, `httpx2`, `httpcore2`, `requests`, `urllib3`, `certifi`, `idna`, `charset-normalizer`, `truststore` | httpx / requests |
| Alembic templating | `Mako` | alembic |

> **Tip:** Run `pip show <package>` and look at the **Required-by** line to see why something is installed.

---

## 4. Folder structure — what goes where

```
SupportIQ/
├── app/
│   ├── main.py              # Creates the FastAPI app, plugs in routers
│   ├── core/
│   │   ├── config.py        # Settings (loaded from .env)
│   │   └── logging.py       # Logging setup
│   ├── db/
│   │   ├── base.py          # SQLAlchemy Base class
│   │   ├── session.py       # Engine, SessionLocal, get_db()
│   │   └── database.py      # (current code — engine/session/Base together)
│   ├── api/
│   │   ├── router.py        # Combines all routers into one
│   │   └── routes/
│   │       ├── health.py    # GET /health
│   │       └── tickets.py   # (current) POST /tickets
│   ├── tickets/             # Feature module: everything about tickets
│   │   ├── router.py        # HTTP endpoints
│   │   ├── schemas.py       # Pydantic models (request/response)
│   │   ├── models.py        # SQLAlchemy model (database table)
│   │   ├── service.py       # Business logic
│   │   └── repository.py    # Database queries
│   ├── models/ schemas/ services/   # (current code, to be moved into tickets/)
│   ├── ai/                  # Future AI analysis logic
│   └── doc/                 # These notes
├── migrations/              # Alembic migration files
├── tests/                   # Automated tests
├── .env / .env.example      # Secrets / template of required variables
├── alembic.ini              # Alembic configuration
└── requirements.txt         # Pinned package versions
```

### The layers (most important idea)

| Layer | File | Job | Knows about |
|---|---|---|---|
| **Router** | `router.py` | Receive HTTP request, return HTTP response | HTTP, status codes |
| **Schema** | `schemas.py` | Validate input, define output shape | Data rules |
| **Service** | `service.py` | Business rules ("can this ticket be closed?") | Logic, not HTTP |
| **Repository** | `repository.py` | Run database queries | Database only |
| **Model** | `models.py` | Describe the database table | Table columns |

**Why split like this? (Separation of Concerns)**
- Each file has **one job** → easier to read and find bugs.
- You can **test** business logic without starting a web server.
- Switching SQLite → MySQL only touches the db/repository layer.
- New developers know exactly where to look.

**Feature-based (`tickets/`) vs layer-based (`models/`, `schemas/`, `services/`)**
- *Layer-based:* all models together, all schemas together. Fine for small apps.
- *Feature-based:* everything for "tickets" in one folder. Scales better as features grow — this is where the project is heading.

---

## 5. How a request flows through the app

Example: `POST /api/v1/tickets` with `{"subject": "Login issue", "message": "I cannot log in since today"}`

```
Client (browser / Postman)
   │  HTTP POST + JSON
   ▼
Uvicorn (ASGI server)  ── receives raw HTTP, passes to FastAPI
   ▼
FastAPI routing        ── matches /api/v1/tickets + POST → submit_ticket()
   ▼
Pydantic (TicketCreate)── validates JSON. Invalid? → 422 error, stops here
   ▼
Depends(get_db)        ── opens a database session
   ▼
Service: create_ticket ── builds Ticket object, add → commit → refresh
   ▼
SQLAlchemy → SQLite    ── INSERT INTO tickets ...
   ▼
response_model         ── TicketResponse filters/serializes the result
   ▼
get_db() finally block ── closes the session
   ▼
Client receives 201 Created + JSON
```

---

## 6. Core concepts explained with our code

### 6.1 Creating the app — `app/main.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)   # runs on STARTUP
    yield
    # code after yield runs on SHUTDOWN

app = FastAPI(title="SupportIQ", version="0.1.0", lifespan=lifespan)

app.include_router(health.router, prefix="/api/v1")
app.include_router(tickets.router, prefix="/api/v1")
```

- **`lifespan`** — startup/shutdown logic in one function. Replaces the older `@app.on_event("startup")`, which is deprecated.
- **`create_all`** — creates tables that **don't exist yet**. It will **not** add new columns to an existing table → that's why we need Alembic.
- **`include_router` + `prefix`** — attach a group of routes; every route gets `/api/v1` in front.
- **Why `/api/v1`?** **API versioning.** Later you can release `/api/v2` without breaking old clients.
- **Why `from app.models.ticket import Ticket` in main.py?** The model must be imported so it registers itself on `Base.metadata`; otherwise `create_all` doesn't know the table exists.

### 6.2 Routers — `APIRouter`

```python
router = APIRouter(tags=["Tickets"])

@router.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def submit_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    return create_ticket(db, ticket)
```

| Piece | Meaning |
|---|---|
| `APIRouter` | A mini-app: group related routes in their own file |
| `tags=["Tickets"]` | Groups endpoints under a heading in Swagger `/docs` |
| `ticket: TicketCreate` | FastAPI reads the JSON **body** and validates it with Pydantic |
| `response_model` | Output is filtered & validated through this schema (hides extra fields) |
| `status_code=201` | "Created" — the correct code for successful POST that creates something |

**How does FastAPI know where a parameter comes from?**
- Declared in the path (`/tickets/{ticket_id}`) → **path parameter**
- Simple type (`int`, `str`) not in path → **query parameter** (`?skip=0`)
- Pydantic model → **request body**
- `Depends(...)` → **dependency**

### 6.3 Pydantic schemas — `app/schemas/ticket.py`

```python
class TicketCreate(BaseModel):                         # INPUT
    model_config = ConfigDict(str_strip_whitespace=True)
    subject: str = Field(min_length=3, max_length=150)
    message: str = Field(min_length=10, max_length=5000)

class TicketResponse(BaseModel):                       # OUTPUT
    model_config = ConfigDict(from_attributes=True)
    id: str
    subject: str
    message: str
    status: str
    created_at: datetime
```

- **Why two schemas?** Input and output are different. The client must **not** send `id`, `status`, or `created_at` — the server sets those.
- **`Field(min_length=..., max_length=...)`** — validation rules. Break them → automatic **422 Unprocessable Entity** with a clear error message.
- **`str_strip_whitespace=True`** — `"  hello  "` becomes `"hello"` before validation.
- **`from_attributes=True`** — lets Pydantic read data from an object's attributes (our SQLAlchemy `Ticket`), not only from a dict. In Pydantic v1 this was called `orm_mode = True`.

### 6.4 SQLAlchemy model — `app/models/ticket.py`

```python
class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    subject: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="received", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
```

- **ORM** = Object Relational Mapper: one class = one table, one object = one row.
- **`Mapped[...]` + `mapped_column()`** — the modern **SQLAlchemy 2.0** style; type hints work with your editor.
- **Why UUID instead of 1, 2, 3?** IDs can't be guessed (`/tickets/2` → try `/tickets/3`), and they're unique across servers/databases.
- **Why `default=lambda: ...` and not `default=datetime.now(...)`?** A lambda runs **for every new row**. Without it, the time would be calculated **once** when the file loads, and every ticket would get the same timestamp.
- **Why UTC?** Servers and users are in different time zones. Store UTC, convert for display.

**Model vs Schema — the #1 beginner confusion**

| | SQLAlchemy Model | Pydantic Schema |
|---|---|---|
| Represents | A database table | API input/output data |
| Used for | Saving / querying data | Validating / serializing data |
| Lives in | `models/` | `schemas/` |

### 6.5 Database session & dependency injection — `app/db/database.py`

```python
DATABASE_URL = "sqlite:///./supportiq.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db          # give the session to the endpoint
    finally:
        db.close()        # ALWAYS close it, even if an error happened
```

| Piece | Meaning |
|---|---|
| **Engine** | Manages the connection(s) to the database. Created **once** for the whole app |
| **SessionLocal** | A factory that creates a new **session** (one "conversation" with the DB) |
| **Session** | Tracks objects you add/change, then `commit()` saves them in one transaction |
| **Base** | Parent class for all models; holds `Base.metadata` (the list of tables) |
| `check_same_thread=False` | SQLite normally allows a connection only in the thread that created it. FastAPI runs normal `def` endpoints in a thread pool, so we turn this check off. **SQLite only.** |
| `autoflush=False` | Don't send pending changes to the DB automatically before every query — we control it |

**Dependency Injection (`Depends`)**
`db: Session = Depends(get_db)` tells FastAPI: *"before calling this endpoint, run `get_db()` and pass me what it yields."*
- A **new session per request** → requests don't interfere with each other.
- Code after `yield` runs **after the response** → session always closed, no connection leaks.
- In tests you can **swap** `get_db` for a test database: `app.dependency_overrides[get_db] = fake_get_db`.

### 6.6 Service — `app/services/ticket_service.py`

```python
def create_ticket(db: Session, ticket_data: TicketCreate) -> Ticket:
    ticket = Ticket(subject=ticket_data.subject, message=ticket_data.message)
    db.add(ticket)      # 1. stage the new row
    db.commit()         # 2. save permanently (transaction)
    db.refresh(ticket)  # 3. reload from DB to get generated values (id, created_at)
    return ticket
```

### 6.7 `def` vs `async def` in FastAPI

| Use | When |
|---|---|
| `async def` | Your code uses `await` (async DB driver, `httpx.AsyncClient`, etc.) |
| `def` | Your code uses **blocking** libraries — like our **sync SQLAlchemy** session |

FastAPI runs plain `def` endpoints in a **thread pool**, so they don't block the server. Calling blocking code **inside** `async def` **does** block everything — a classic mistake.

That's why `health_check` is `async def` (no I/O) and `submit_ticket` is `def` (sync DB).

### 6.8 HTTP status codes you should know

| Code | Name | When |
|---|---|---|
| 200 | OK | Successful GET / PATCH |
| 201 | Created | Successful POST that created something |
| 204 | No Content | Successful DELETE (no body) |
| 400 | Bad Request | Generic client error |
| 401 | Unauthorized | Not logged in |
| 403 | Forbidden | Logged in, but not allowed |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation failed (FastAPI default) |
| 500 | Internal Server Error | Bug on the server |

---

## 7. Database migrations with Alembic

**Problem:** `create_all()` only creates **new** tables. If you add a `priority` column to `Ticket`, the existing table **won't** change.

**Solution:** **Alembic** = "Git for your database schema". Each change is a migration file with `upgrade()` and `downgrade()`.

```powershell
alembic init migrations                                # one-time setup
alembic revision --autogenerate -m "add priority"      # generate a migration from model changes
alembic upgrade head                                   # apply all pending migrations
alembic downgrade -1                                   # undo the last migration
alembic current                                        # which version is the DB at?
alembic history                                        # list all migrations
alembic stamp head                                     # mark an existing DB as up-to-date
```

After `alembic init`, edit `migrations/env.py`:
```python
from app.db.database import Base
from app.models.ticket import Ticket   # import every model
target_metadata = Base.metadata
```

> Once Alembic is in use, remove `create_all()` from `lifespan` — let migrations own the schema.

---

## 8. Environment variables & config

**Never hard-code** secrets or environment-specific values (database URL, API keys) in code.

`.env` (secret, **not** committed):
```
DATABASE_URL=sqlite:///./supportiq.db
DEBUG=true
```

`.env.example` (committed — shows teammates which variables are needed, with no real values):
```
DATABASE_URL=
DEBUG=false
```

`app/core/config.py` with **pydantic-settings**:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    APP_NAME: str = "SupportIQ"
    DATABASE_URL: str = "sqlite:///./supportiq.db"
    DEBUG: bool = False

settings = Settings()
```

Usage: `from app.core.config import settings` → `settings.DATABASE_URL`.
**Bonus:** values are type-checked — `DEBUG=yes` becomes `True`, `DEBUG=banana` raises an error at startup.

---

## 9. Common errors & fixes

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'fastapi'` | venv not activated | `.venv\Scripts\activate` |
| `ModuleNotFoundError: No module named 'app'` | Running from the wrong folder | Run from the project root `SupportIQ/` |
| `running scripts is disabled on this system` | PowerShell execution policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `[Errno 10048] address already in use` | Port 8000 busy | Stop the other server or use `--port 8001` |
| `422 Unprocessable Entity` | Request body failed validation | Read the `detail` field in the response |
| `sqlite3.OperationalError: no such column` | Model changed, table didn't | Use Alembic migration (or delete `supportiq.db` in dev only) |
| `SQLite objects created in a thread can only be used in that same thread` | Missing `check_same_thread` | Add `connect_args={"check_same_thread": False}` |
| `requirements.txt` shows as binary in Git | Saved as UTF-16 by PowerShell | Re-save as UTF-8 |

---

## 10. Interview questions & answers

### FastAPI basics

**Q: What is FastAPI and why choose it?**
A modern Python web framework for building APIs. It is **fast** (built on Starlette + ASGI), gives **automatic validation** through Pydantic and type hints, **auto-generates docs** (Swagger/ReDoc), and supports **async** natively. Less code, fewer bugs, great editor support.

**Q: FastAPI vs Flask vs Django?**
| | FastAPI | Flask | Django |
|---|---|---|---|
| Type | API-focused, async | Minimal micro-framework | Full-stack "batteries included" |
| Validation | Built-in (Pydantic) | Manual / extensions | Forms / DRF serializers |
| Async | Native | Limited | Partial |
| Auto docs | Yes | No | Via DRF + extensions |
| Best for | APIs, microservices, ML serving | Small apps, flexibility | Large apps with admin, ORM, auth |

**Q: What is ASGI? How is it different from WSGI?**
Both are standards for how a Python web server talks to a Python web app.
**WSGI** (Flask, classic Django) is synchronous — one request per worker at a time.
**ASGI** is asynchronous — one worker can handle many requests concurrently while waiting on I/O, and supports WebSockets. FastAPI is ASGI; Uvicorn is an ASGI server.

**Q: Why do we need Uvicorn?**
FastAPI is only the application. Uvicorn is the **server** that opens a port, accepts HTTP connections, and passes requests to FastAPI. In production you often run multiple Uvicorn workers (e.g. `uvicorn app.main:app --workers 4`, or behind Gunicorn/Nginx).

**Q: What is Pydantic?**
A data validation library using Python type hints. It converts and validates incoming data, and gives clear errors. FastAPI uses it for request bodies, responses and settings. Pydantic v2's core is written in Rust, so it is very fast.

**Q: What happens if a request body is invalid?**
FastAPI automatically returns **422 Unprocessable Entity** with details about which field failed and why. The endpoint function is never called.

**Q: What is `response_model` used for?**
It validates and **filters** the output. Even if the returned object has extra fields (e.g. a password hash), only fields in the response schema are sent. It also documents the response in `/docs`.

**Q: What is dependency injection in FastAPI?**
Using `Depends()` to declare things an endpoint needs (DB session, current user, settings). FastAPI creates them, passes them in, and cleans up afterwards (for `yield` dependencies). Benefits: reusable, testable (override in tests), less repeated code.

**Q: Path vs query vs body parameters?**
Path: `/tickets/{id}` — identifies a resource. Query: `/tickets?status=open` — filtering, pagination. Body: JSON payload — data to create/update.

**Q: `def` or `async def`?**
`async def` when the code awaits async I/O. `def` when using blocking libraries — FastAPI runs it in a thread pool. Never call blocking code inside `async def`.

**Q: What is `lifespan`?**
A function that runs code on startup (before `yield`) and shutdown (after `yield`) — e.g. create DB connections, load an ML model, close resources. It replaces the deprecated `on_event` handlers.

**Q: What is `APIRouter`?**
A way to split routes across multiple files/modules, then attach them to the main app with `include_router`, optionally with a prefix and tags.

### Database / SQLAlchemy

**Q: What is an ORM? Pros and cons?**
Maps database tables to Python classes. **Pros:** less raw SQL, safer against SQL injection (parameters are escaped), database-independent code. **Cons:** can hide slow queries (e.g. the N+1 problem), and complex queries are sometimes easier in raw SQL.

**Q: Engine vs Session?**
The **engine** manages connections and is created once per app. A **session** is a short-lived unit of work — one per request — that tracks changes and commits them in a transaction.

**Q: What do `add`, `commit`, `refresh` do?**
`add` stages the object; `commit` writes it to the DB permanently; `refresh` reloads it from the DB to get values generated there (IDs, defaults).

**Q: What is a transaction?**
A group of DB operations that succeed or fail **together** (all-or-nothing). If something fails, `rollback()` undoes it. Follows **ACID**: Atomicity, Consistency, Isolation, Durability.

**Q: Why do we need migrations (Alembic)?**
Databases in production hold real data, so you can't drop and recreate tables. Migrations apply schema changes step by step, in order, version-controlled, and reversible.

**Q: SQLite vs MySQL/PostgreSQL?**
SQLite is a single file with no server — perfect for learning, prototyping, tests. MySQL/PostgreSQL are client-server databases for production: many concurrent users, better concurrency, users/permissions, scaling.

**Q: Why UUIDs as primary keys?**
Not guessable, globally unique, can be generated without asking the database. Trade-off: bigger than integers and slightly slower for indexes.

### Project & architecture

**Q: Explain your project's architecture.**
"A layered FastAPI app: **routers** handle HTTP, **Pydantic schemas** validate input/output, a **service layer** holds business logic, a **repository layer** handles DB queries, and **SQLAlchemy models** map to tables. Config comes from environment variables via pydantic-settings, and Alembic manages schema migrations. Routes are versioned under `/api/v1`."

**Q: Why separate schemas from models?**
They change for different reasons. The table may have internal fields (password hash, internal notes) that must never be exposed; the API may accept fewer fields than the table has. Separation keeps the API contract stable and secure.

**Q: Why use a virtual environment and `requirements.txt`?**
Isolation (each project its own versions) and reproducibility (anyone can install exactly the same versions with `pip install -r requirements.txt`).

**Q: Why keep secrets in `.env` and not in code?**
Code goes to Git, which many people (or the public) can see. Secrets in env vars can differ per environment (dev/staging/prod) and are never committed. `.env.example` documents which variables are needed.

**Q: Why version the API (`/api/v1`)?**
To make breaking changes in `/api/v2` without breaking existing clients still using v1.

**Q: How would you test this API?**
With `pytest` and FastAPI's `TestClient` (built on httpx). Override `get_db` with a test database so tests don't touch real data:
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### REST basics

**Q: What is REST?**
An architectural style for APIs: resources identified by URLs (`/tickets/123`), standard HTTP methods for actions, stateless requests (each request carries everything needed), and usually JSON responses.

**Q: CRUD ↔ HTTP methods?**
| CRUD | Method | Example |
|---|---|---|
| Create | POST | `POST /tickets` |
| Read | GET | `GET /tickets`, `GET /tickets/{id}` |
| Update | PUT (replace whole) / PATCH (partial) | `PATCH /tickets/{id}` |
| Delete | DELETE | `DELETE /tickets/{id}` |

**Q: PUT vs PATCH?**
PUT replaces the whole resource (send all fields). PATCH updates only the fields you send.

**Q: What does idempotent mean?**
Calling it many times has the same effect as calling it once. GET, PUT and DELETE are idempotent; POST is not (each call creates a new ticket).

---

## 11. Command cheat sheet

```powershell
# Virtual environment
python -m venv .venv                  # create
.venv\Scripts\activate                # activate (PowerShell)
deactivate                            # leave

# Packages
pip install "fastapi[standard]"       # install
pip install -r requirements.txt       # install everything from file
pip freeze | Out-File -Encoding utf8 requirements.txt   # save list (UTF-8)
pip list                              # list installed
pip show fastapi                      # details + "Required-by"

# Run the server
python -m uvicorn app.main:app --reload          # dev
python -m uvicorn app.main:app --port 8001       # different port
fastapi dev app/main.py                          # FastAPI CLI (dev)
fastapi run app/main.py                          # FastAPI CLI (production mode)

# Alembic
alembic revision --autogenerate -m "message"
alembic upgrade head
alembic downgrade -1

# Tests
pip install pytest
pytest -v

# Git
git status
git checkout -b feature/name
git add .
git commit -m "message"
```

---

*Keep updating this file as you learn something new — writing it in your own words is the best interview preparation.* ✍️
