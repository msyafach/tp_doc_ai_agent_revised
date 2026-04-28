# TP Local File Generator

AI-powered web application that automates the creation of **Transfer Pricing (TP) Local File** documentation — a mandatory compliance report required by Indonesian tax regulations (PMK-213/2016) for companies conducting affiliated transactions above the threshold.

Traditionally a tax consultant spends **weeks** manually researching, writing, and formatting this document. This application reduces that to **hours** by combining a structured data-entry wizard with an AI agent pipeline that researches, writes, and formats each section automatically — then exports the result as a ready-to-use `.docx` file.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Directory Structure](#directory-structure)
- [User Flow](#user-flow)
- [Login & Authentication Flow](#login--authentication-flow)
- [Document Retrieval: PageIndex Algorithm](#document-retrieval-pageindex-algorithm)
- [AI Agent Pipeline](#ai-agent-pipeline)
- [API Reference](#api-reference)
- [CLAUDE.md — AI Assistant Instructions](#claudemd--ai-assistant-instructions)
- [Graphify — Codebase Knowledge Graph](#graphify--codebase-knowledge-graph)
- [Development Guide](#development-guide)
- [CI/CD Pipeline](#cicd-pipeline)

---

## Architecture Overview

```mermaid
graph LR
    Browser([Browser]) -->|JWT / REST| Backend
    Backend -->|ORM| DB[(PostgreSQL)]
    Backend -->|Enqueue| Redis[(Redis)]
    Redis -->|Dequeue| Worker
    Worker -->|LangGraph| AI([Groq / OpenAI / Tavily])
    Worker --> DB
    Backend -->|Poll task| Browser
```

### Services

| Service    | Image              | Port | Purpose                           |
|------------|--------------------|------|-----------------------------------|
| `db`       | postgres:16-alpine | 5432 | Primary database                  |
| `redis`    | redis:7-alpine     | 6379 | Celery broker & result backend    |
| `backend`  | Python 3.11-slim   | 8000 | Django REST API (Gunicorn)        |
| `worker`   | Python 3.11-slim   | —    | Celery async worker (AI tasks)    |
| `frontend` | Node 20-alpine     | 3000 | React dev server (Vite)           |

### Why this design?

**JSONB state storage** — The TP Local File state is a deeply nested, schema-evolving document. Storing it as a JSONB column avoids schema migrations every time a new field is added, and makes import/export trivial.

**Celery + Redis for async AI tasks** — LLM pipelines take 2–5 minutes. Celery offloads these to background workers while the frontend polls `/api/tasks/{id}/` for live progress.

**Volume-mounted `tp_app/`** — Agent code, templates, and export logic are mounted into both the backend and worker containers. Code edits take effect without rebuilding Docker images during development.

**LangGraph parallel orchestration** — Independent TP sections run in parallel branches, reducing total generation time by ~60% vs. sequential execution.

---

## Tech Stack

### Frontend

| Technology         | Version | Purpose                                       |
|--------------------|---------|-----------------------------------------------|
| React              | 18      | Component-based wizard UI                     |
| TypeScript         | 5       | Type safety across components & API contracts |
| Vite               | 5       | Dev server and production bundler             |
| Tailwind CSS       | 3       | Utility-first styling                         |
| Zustand            | 5       | Global state (wizard data, auth, settings)    |
| React Router DOM   | 6       | Client-side routing                           |
| TanStack Query     | 5       | Server state caching & background refetch     |
| Axios              | 1       | HTTP client for REST API calls                |
| React Dropzone     | 14      | Drag-and-drop file upload                     |
| Radix UI           | latest  | Accessible headless UI primitives             |

### Backend

| Technology                    | Version | Purpose                             |
|-------------------------------|---------|-------------------------------------|
| Python                        | 3.11    | Primary language                    |
| Django                        | 5.0.6   | Web framework, ORM, admin           |
| Django REST Framework         | 3.15.2  | REST API serializers & views        |
| djangorestframework-simplejwt | 5.3.1   | JWT authentication                  |
| Celery                        | 5.4.0   | Async task queue                    |
| Redis / kombu                 | 5.0.8   | Message broker for Celery           |
| psycopg2-binary               | 2.9.9   | PostgreSQL adapter                  |
| Gunicorn                      | 22.0.0  | WSGI production server              |
| WhiteNoise                    | 6.7.0   | Static file serving                 |
| python-docx                   | 1.1.2   | Programmatic DOCX generation        |
| docxtpl                       | 0.18.0  | Jinja2 templating over Word files   |

### AI & Agents (`tp_app/`)

| Technology            | Purpose                                          |
|-----------------------|--------------------------------------------------|
| LangGraph             | Stateful parallel AI agent orchestration         |
| LangChain             | LLM abstraction, prompt management               |
| Groq (default)        | Fast LLM inference (`llama-3.3-70b-versatile`)   |
| OpenAI (optional)     | Alternative LLM provider (GPT-4o etc.)           |
| Tavily                | AI-optimized web search for industry research    |
| PageIndex             | Vectorless hierarchical PDF retrieval            |
| FAISS                 | In-memory vector store (Vector RAG fallback)     |
| sentence-transformers | HuggingFace local embeddings (free)              |
| PyPDF2 / pymupdf      | PDF parsing                                      |
| tiktoken              | Token counting                                   |

---

## Quick Start

### Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Docker & Docker Compose | latest | https://docs.docker.com/get-docker/ |
| Python | ≥ 3.11 | https://www.python.org/downloads/ |
| Node.js | ≥ 20 | https://nodejs.org/ |
| uv | latest | see below |
| Git | latest | https://git-scm.com/ |

Plus at least one API key from each:
- **LLM**: Groq (free tier) or OpenAI
- **Web search**: Tavily

---

### API Keys — How to Get Them

#### Groq (recommended — free tier, no credit card required)

1. Go to [https://console.groq.com](https://console.groq.com)
2. Click **Sign Up** — register with Google or email
3. After login, go to **API Keys** in the left sidebar
4. Click **Create API Key** → give it a name (e.g. `tp-app`)
5. Copy the key — it starts with `gsk_...`
6. Paste it into **Admin Settings** in the app (not `.env`)

> Free tier includes generous rate limits sufficient for development and light production use.

---

#### OpenAI (optional, paid)

1. Go to [https://platform.openai.com](https://platform.openai.com)
2. Click **Sign Up** or **Log In**
3. Go to **API Keys** → [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
4. Click **Create new secret key** → give it a name
5. Copy the key — it starts with `sk-...`
6. Make sure your account has **billing enabled** (add a credit card under Billing)
7. Paste it into **Admin Settings** in the app

> Recommended model: `gpt-4o-mini` for cost efficiency, `gpt-4o` for higher quality.

---

#### Tavily (required for AI research sections)

Tavily is used by the AI agents to search the web for industry analysis, Indonesian regulations, and comparable company data.

1. Go to [https://app.tavily.com](https://app.tavily.com)
2. Click **Sign Up** — register with Google or email
3. After login, your API key is shown on the **dashboard** immediately
4. Copy the key — it starts with `tvly-...`
5. Paste it into **Admin Settings** in the app

> Free tier includes 1,000 searches/month. Each full AI pipeline run uses approximately 5–15 Tavily searches.

---

### Step 1 — Install `uv` (Python package manager)

`uv` is required to manage all Python dependencies in this project. Install it once globally:

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify:
```bash
uv --version
```

---

### Step 2 — Clone the repository

```bash
git clone <repo-url>
cd tp_local_file_generator
```

---

### Step 3 — Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in the required values (see [Environment Variables](#environment-variables) section for reference). At minimum set `SECRET_KEY`, `POSTGRES_PASSWORD`.

---

### Step 4 — Install Python dependencies (tp_app)

`tp_app/` is the AI agent module. Install its dependencies with `uv`:

```bash
cd tp_app
uv sync
cd ..
```

This reads `tp_app/pyproject.toml` and installs everything into an isolated `.venv` inside `tp_app/`.

---

### Step 5 — Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

---

### Step 6 — Build and start all services

```bash
docker compose up --build
```

This builds and starts: `db` (PostgreSQL), `redis`, `backend` (Django), `worker` (Celery), `frontend` (React/Vite).

> First build takes ~3–5 minutes. Subsequent starts with `docker compose up -d` are fast.

---

### Step 7 — Run database migrations & create superuser (first time only)

Wait for the backend to be healthy (watch logs with `docker compose logs -f backend`), then:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

---

### Step 8 — Open the app

| Service        | URL                          |
|----------------|------------------------------|
| Frontend (app) | http://localhost:3000        |
| Django API     | http://localhost:8000/api/   |
| Django Admin   | http://localhost:8000/admin/ |

---

### Step 9 — Configure API keys

Log in as the superuser you just created → **Admin Settings** → enter:
- LLM Provider (Groq or OpenAI)
- LLM API Key
- Tavily API Key

These are stored in the database and shared across all users — no need to put them in `.env`.

---

### Quick reference (after initial setup)

```bash
# Start all services (background)
docker compose up -d

# Stop all services
docker compose down

# Rebuild after code changes
docker compose up -d --build backend worker

# View backend logs
docker compose logs -f backend

# View worker (AI agent) logs
docker compose logs -f worker

# Run Django management commands
docker compose exec backend python manage.py <command>
```

---

## Environment Variables

Create `.env` at the project root (copy from `.env.example`):

```env
# ── Django ─────────────────────────────────────────────────────
SECRET_KEY=change-me-to-a-long-random-string
DEBUG=True
ALLOWED_HOSTS=*

# ── PostgreSQL ─────────────────────────────────────────────────
POSTGRES_DB=tp_db
POSTGRES_USER=tp_user
POSTGRES_PASSWORD=tp_pass

# ── Redis (Celery) ─────────────────────────────────────────────
REDIS_URL=redis://redis:6379/0
```

> **LLM and Tavily API keys are stored in the database**, not in `.env`. Configure them from the Admin Settings page after first login.

---

## Directory Structure

```
tp_local_file_generator/
│
├── frontend/                        React + TypeScript + Vite
│   └── src/
│       ├── pages/                   LandingPage, LoginPage, ProjectDashboard,
│       │                            Step0Upload … Step11ReviewExport
│       ├── components/              Sidebar, SettingsModal, DynamicTable, etc.
│       ├── store/                   Zustand: projectStore, authStore
│       ├── api/                     Axios client (projects, auth, tasks)
│       └── types/                   TypeScript interfaces
│
├── backend/                         Django REST API
│   ├── config/                      settings.py, urls.py, celery.py, wsgi.py
│   └── api/
│       ├── models.py                Project (JSONB), AgentTask, SystemSetting
│       ├── views.py                 All API endpoints
│       ├── tasks.py                 Celery async tasks
│       ├── serializers.py
│       └── services/
│           └── agent_service.py     Django ↔ LangGraph bridge
│
├── tp_app/                          AI agents + DOCX export (volume-mounted)
│   ├── agents/
│   │   ├── orchestrator.py          LangGraph StateGraph (parallel pipeline)
│   │   ├── research_subagent.py     Tavily web research nodes
│   │   ├── analysis_subagent.py     Functional analysis + characterization
│   │   ├── transaction_subagent.py  Comparability, method, PLI justification
│   │   ├── summary_subagent.py      Executive summary, conclusion, P/L overview
│   │   ├── business_subagent.py     Business activities, supply chain
│   │   ├── extraction_agent.py      Document extraction (PageIndex / Vector RAG)
│   │   └── llm_factory.py           LLM provider factory (Groq / OpenAI)
│   ├── export/
│   │   ├── docx_export.py           python-docx builder export
│   │   └── docx_template_export.py  docxtpl Jinja2 template export
│   ├── utils/
│   │   └── document_processor.py   2-tier retrieval strategy
│   └── TP_Local_File_TEMPLATE.docx  Pre-formatted Jinja2 Word template
│
├── graphify-out/                    Codebase knowledge graph (auto-generated)
│   ├── GRAPH_REPORT.md              God nodes + community structure summary
│   └── graph.json                   Full graph data
│
├── .github/workflows/
│   └── ci-cd.yml                   GitHub Actions: test + deploy
│
├── docker-compose.yml
├── .env                            (gitignored — create from .env.example)
├── CLAUDE.md                       AI assistant project instructions
└── README.md
```

---

## User Flow

```mermaid
flowchart TD
    A([🏠 Landing Page]) --> B([🔑 Login])
    B --> C([📋 Project Dashboard])
    C -->|New project| D([📁 Step 0: Upload Documents\noptional — PDF · DOCX · XLSX · TXT])
    C -->|Open existing| S1
    D -->|AI auto-extracts data| S1

    S1([Step 1: Company Identity]) --> S2([Step 2: Ownership & Management])
    S2 --> S3([Step 3: Affiliated Parties])
    S3 --> S4([Step 4: Business Activities])
    S4 --> S5([Step 5: Transactions])
    S5 --> S6([Step 6: Financial Data])
    S6 --> S7([Step 7: Comparable Companies])
    S7 --> S8([Step 8: TP Method & PLI])
    S8 --> S9([Step 9: Non-Financial Events])
    S9 --> S10

    S10([⚡ Step 10: Run AI Agents\n5–10 min · LangGraph parallel pipeline\nReview & edit each section]) --> S11
    S11([📄 Step 11: Export\nDownload TP_Company_FY.docx])
```

---

## Login & Authentication Flow

Authentication uses **JWT (JSON Web Tokens)** via `djangorestframework-simplejwt`.

```mermaid
sequenceDiagram
    participant U as User / Browser
    participant F as Frontend (Zustand authStore)
    participant B as Django Backend
    participant DB as PostgreSQL

    U->>F: Enter username + password
    F->>B: POST /api/auth/login/
    B->>DB: Validate credentials
    DB-->>B: User object
    B-->>F: { access (15min), refresh (1day), user }
    F->>F: Store tokens in memory + localStorage
    F-->>U: Redirect to Project Dashboard

    Note over F,B: Subsequent requests
    F->>B: GET /api/projects/ + Authorization: Bearer {access}
    B-->>F: 200 OK

    Note over F,B: Access token expires after 15 min
    F->>B: Any request → 401 Unauthorized
    F->>B: POST /api/auth/refresh/ { refresh }
    B-->>F: New access token
    F->>B: Retry original request

    Note over F,B: Logout or 15-min inactivity
    F->>B: POST /api/auth/logout/ { refresh }
    B->>DB: Blacklist refresh token
    F->>F: Clear localStorage → redirect to Landing
```

**Token settings:**

| Setting                 | Value      |
|-------------------------|------------|
| Access token lifetime   | 15 minutes |
| Refresh token lifetime  | 1 day      |
| Refresh token rotation  | Enabled    |
| Token blacklisting      | Enabled    |
| Inactivity auto-logout  | 15 minutes |

**Admin vs regular user:**
- Regular users: full access to wizard, project management, and export
- Admin (`is_staff=true`): additionally can manage users and configure global API keys via Admin Settings page

---

## Document Retrieval: PageIndex Algorithm

When a user uploads a prior TP document in Step 0, the system automatically extracts structured data (company name, shareholders, financials, etc.) using a **2-tier retrieval strategy** defined in `tp_app/utils/document_processor.py`.

### Tier selection

```mermaid
flowchart TD
    UP([Uploaded files]) --> Q1{Single PDF?}
    Q1 -->|No - multiple files\nor non-PDF| VR
    Q1 -->|Yes| Q2{Pages < 50\nAND OpenAI key?}
    Q2 -->|No| VR
    Q2 -->|Yes| PI

    PI["🌳 Tier 1: PageIndex\nVectorless hierarchical retrieval\nLLM navigates document tree"]
    VR["🔢 Tier 2: Vector RAG\nFAISS + embeddings\nChunk similarity search"]

    PI --> EX([Structured JSON extraction])
    VR --> EX
```

### Tier 1 — PageIndex (vectorless, for PDFs ≤ 50 pages)

PageIndex organizes the document as a **hierarchical tree** and lets the LLM navigate it like a human reading a table of contents — no vector embeddings needed.

**Phase 1 — Index building** (`page_index_main` from the `pageindex` library):

```mermaid
flowchart LR
    PDF([PDF file]) --> TOC{Has TOC?}
    TOC -->|Yes| PARSE[Parse TOC structure]
    TOC -->|No| GEN[LLM generates structure]
    PARSE --> TREE
    GEN --> TREE

    TREE["🌲 Hierarchical Tree\nRoot → Chapters → Sections → Pages"]
    TREE --> SUM[LLM writes summary\nper node]
    SUM --> IDX([Index ready\ntitle · summary · text per node])
```

**Phase 2 — Query retrieval** (`_query_page_index` in `extraction_agent.py`):

```mermaid
flowchart TD
    Q([Query: 'Extract shareholder info']) --> L0

    L0["Level 0 — Show chapter summaries to LLM\n[0] Company Overview\n[1] Ownership Structure ✓\n[2] Financials\n[3] Transactions"]
    L0 -->|LLM picks relevant branches| L1

    L1["Level 1 — Show sub-section summaries\n[1.0] Share Capital ✓\n[1.1] Shareholders List ✓\n[1.2] Board of Directors"]
    L1 -->|LLM drills down| L2

    L2["Level 2 — Collect full text\nfrom selected leaf nodes"]
    L2 --> TRIM["Trim to 16,000 token budget"]
    TRIM --> EXT["LLM extracts structured JSON\n{ shareholders: [...] }"]
```

This is **true hierarchical traversal**: at each level the LLM only reads short summaries and picks which branches to explore. Full page text is only read for the final selected nodes — mimicking how a human expert skips irrelevant chapters entirely.

**Comparison with traditional RAG:**

| Aspect              | Vector RAG                    | PageIndex                           |
|---------------------|-------------------------------|-------------------------------------|
| Search method       | Embedding cosine similarity   | LLM reasoning over tree structure   |
| Storage needed      | Vector database               | None                                |
| Retrieval style     | One-shot similarity match     | Multi-level hierarchical traversal  |
| Explainability      | Low (distance scores only)    | High (traceable path through tree)  |
| Best for            | Long / unstructured documents | Structured docs with TOC (≤ 50 pg)  |
| Token efficiency    | Fixed k chunks regardless     | Only relevant branches read in full |

### Tier 2 — Vector RAG (for long or non-PDF documents)

```mermaid
flowchart LR
    DOC([Document text]) --> SPLIT["Chunk: 1,000 chars\n150 char overlap"]
    SPLIT --> EMBED["Embed chunks\nHuggingFace all-MiniLM-L6-v2\nor OpenAI text-embedding-3-small"]
    EMBED --> FAISS[(FAISS\nin-memory store)]
    Q2([Query]) --> FAISS
    FAISS -->|Top-8 chunks| LLM["LLM extracts\nstructured JSON"]
```

---

## AI Agent Pipeline

The AI generation pipeline in `tp_app/agents/orchestrator.py` uses **LangGraph StateGraph** for parallel execution.

```mermaid
graph TD
    START([▶ START]) --> INIT[Initialize State]
    INIT --> BA & BB

    subgraph BA["Branch A — Research (Tavily)"]
        A1[industry_global] --> A2[industry_indonesia] --> A3[business_environment]
    end

    subgraph BB["Branch B — Analysis"]
        B1[functional_analysis] --> B2[characterization]
    end

    A3 --> SYNC
    B2 --> SYNC

    SYNC["⟳ SYNC NODE\nJoin Branches A + B"] --> BC & BD & BE

    subgraph BC["Branch C"]
        C1[conclusion]
    end

    subgraph BD["Branch D"]
        D1[pl_overview]
    end

    subgraph BE["Branch E"]
        E1[transaction_summary]
    end

    C1 --> FINAL
    D1 --> FINAL
    E1 --> FINAL

    FINAL[executive_summary] --> END([⏹ END\nFull state ready for export])
```

Branches A and B run **in parallel**. Branches C, D, and E also run **in parallel** after the sync node. This reduces total generation time by ~60% vs. sequential execution.

**Supported LLM providers:**

| Provider | Model                     | Notes                  |
|----------|---------------------------|------------------------|
| Groq     | `llama-3.3-70b-versatile` | Default — fast, free tier |
| OpenAI   | `gpt-4o`, `gpt-4o-mini`   | Higher quality, paid   |

**DOCX export paths:**

| Type       | Query param        | How it works                                      |
|------------|--------------------|---------------------------------------------------|
| Template   | `?type=template`   | docxtpl renders `TP_Local_File_TEMPLATE.docx` with Jinja2 — template editable in Word |
| Builder    | `?type=builder`    | python-docx builds DOCX programmatically          |

---

## API Reference

### Authentication

| Method | Endpoint             | Description                       |
|--------|----------------------|-----------------------------------|
| POST   | `/api/auth/login/`   | Login → returns JWT tokens        |
| POST   | `/api/auth/logout/`  | Logout → blacklist refresh token  |
| POST   | `/api/auth/refresh/` | Refresh access token              |
| GET    | `/api/auth/me/`      | Current authenticated user info   |

### Projects

| Method | Endpoint                                        | Description                       |
|--------|-------------------------------------------------|-----------------------------------|
| GET    | `/api/projects/`                                | List all projects                 |
| POST   | `/api/projects/`                                | Create new project                |
| GET    | `/api/projects/{id}/`                           | Get full project state            |
| PATCH  | `/api/projects/{id}/`                           | Save state updates                |
| DELETE | `/api/projects/{id}/`                           | Delete project                    |
| GET    | `/api/projects/{id}/export-json/`               | Download project as JSON backup   |
| POST   | `/api/projects/{id}/load-json/`                 | Restore from JSON backup          |
| POST   | `/api/projects/{id}/upload-documents/`          | Upload docs → async AI extraction |
| POST   | `/api/projects/{id}/run-agents/`                | Run full AI pipeline (async)      |
| POST   | `/api/projects/{id}/run-single-agent/`          | Regenerate one section (async)    |
| GET    | `/api/projects/{id}/export-docx/?type=template` | Download DOCX (docxtpl)           |
| GET    | `/api/projects/{id}/export-docx/?type=builder`  | Download DOCX (python-docx)       |

### Tasks & Config

| Method | Endpoint           | Description                               |
|--------|--------------------|-------------------------------------------|
| GET    | `/api/tasks/{id}/` | Poll Celery task status + progress log    |
| GET    | `/api/config/`     | TP methods, PLI options, transaction types|

### Admin

| Method    | Endpoint                | Description                      |
|-----------|-------------------------|----------------------------------|
| GET/PATCH | `/api/admin/settings/`  | Global API keys + LLM config     |
| GET/PATCH | `/api/admin/users/`     | User management                  |

---

## CLAUDE.md — AI Assistant Instructions

This project includes `CLAUDE.md` at the root (and `.claude/CLAUDE.md`) that instructs Claude or any AI coding assistant on how to work with this codebase. **Read this file before starting development with an AI assistant.**

Key rules:

| Rule | Reason |
|------|--------|
| Always use `uv` for Python packages | Consistent lockfile, faster than pip |
| Run `docker ps` before debugging | Confirm the right containers are running |
| Use `docker logs <id>` for debugging | Inspect container output |
| Use `docker compose up -d --build` after changes | Rebuild and restart cleanly |
| Always commit after updating code | Prevents lost work |
| Read `graphify-out/GRAPH_REPORT.md` before architecture questions | Graph captures cross-module relationships not visible from single files |
| Run `graphify update .` after modifying Python files | Keep knowledge graph current (AST-only, free) |

---

## Graphify — Codebase Knowledge Graph

`graphify-out/` contains an auto-generated **knowledge graph** of the entire codebase. It is a machine-readable map of every function, class, module, and the relationships between them.

| File | Purpose |
|------|---------|
| `graphify-out/GRAPH_REPORT.md` | Human-readable summary: god nodes, community hubs, key clusters |
| `graphify-out/graph.json` | Full graph data used by the graphify CLI |
| `graphify-out/cache/` | AST extraction cache — speeds up incremental updates |

**Current stats:** 7,400+ nodes · 12,000+ edges · 1,300+ communities

### When to use it

- **Before answering "how does X work?"** — `GRAPH_REPORT.md` shows god nodes (highest-degree nodes everything connects to)
- **Cross-module questions** — use `graphify query` instead of grep; it traverses extracted + inferred edges
- **After code changes** — run `graphify update .` (AST only, no LLM cost, no API key needed)

### Commands

```bash
# Update graph after code changes (free, no LLM)
graphify update .

# Ask a natural-language question about the codebase
graphify query "how does the Celery task communicate with LangGraph?"

# Find the shortest relationship path between two modules
graphify path "document_processor" "extraction_agent"

# Explain a concept using the graph
graphify explain "PageIndex hierarchical traversal"
```

---

## Development Guide

### Docker workflow (recommended)

```bash
# Start everything
docker compose up -d --build

# View logs
docker compose logs -f backend
docker compose logs -f worker

# Rebuild only backend/worker after tp_app or backend changes
docker compose up -d --build backend worker

# Shell into a container
docker compose exec backend bash
docker compose exec worker bash
```

### Running backend locally (no Docker)

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Separate terminal:
celery -A config worker --loglevel=info
```

### Running frontend locally (no Docker)

```bash
cd frontend
npm install
npm run dev
# Set proxy in vite.config.ts → target: http://localhost:8000
```

### Testing AI agents without the UI

```bash
cd tp_app
uv run python -c "
from utils.dummy_data import DUMMY_STATE
from agents.orchestrator import run_agents
result = run_agents(DUMMY_STATE)
print(result.get('executive_summary', ''))
"
```

### Adding a Python dependency to tp_app

```bash
cd tp_app
uv add <package-name>
# If backend also imports it, add to backend/requirements.txt manually
```

### Git workflow

Always work on a feature branch — never push directly to `main`:

```bash
git checkout -b feature/your-feature-name
# make changes
git add <specific files>
git commit -m "feat: short description of what and why"
# Open a Pull Request to main via GitHub
```

---

## CI/CD Pipeline

Defined in `.github/workflows/ci-cd.yml`, triggered on push to `main` or PR to `main`.

```mermaid
flowchart TD
    PUSH([Push / PR to main]) --> TEST

    subgraph TEST["🧪 Test Job (ubuntu-latest)"]
        T1[Install uv] --> T2[Create Python 3.11 venv]
        T2 --> T3[Install backend + tp_app requirements]
        T3 --> T4[pytest tests/ -v --tb=short]
    end

    TEST -->|Tests pass + push to main only| GATE

    GATE["🔒 production environment\napproval required"] --> DEPLOY

    subgraph DEPLOY["🚀 Deploy Job (self-hosted EC2)"]
        D1[Checkout code] --> D2[Write .env from GitHub Secrets]
        D2 --> D3[docker compose up -d --build\n--renew-anon-volumes]
        D3 --> D4[Poll until backend ready\nmanage.py check --deploy]
        D4 --> D5[Verify all containers healthy]
        D5 --> D6[Prune old Docker images]
    end
```

### GitHub Secrets — Setup Guide

CI/CD pipeline menulis `.env` langsung dari GitHub Secrets saat deploy. Berikut cara mengisinya:

#### Langkah 1 — Buka halaman Secrets di GitHub

1. Buka repository di GitHub
2. Klik **Settings** (tab paling kanan)
3. Di sidebar kiri, klik **Secrets and variables** → **Actions**
4. Klik **New repository secret** untuk setiap secret di bawah

---

#### Langkah 2 — Isi semua secrets berikut

| Secret | Contoh nilai | Keterangan |
|--------|-------------|------------|
| `SECRET_KEY` | `s3cr3t-random-50-chars...` | Django secret key — generate dengan perintah di bawah |
| `ALLOWED_HOSTS` | `yourdomain.com,www.yourdomain.com` | Domain server production, pisahkan dengan koma |
| `POSTGRES_DB` | `tp_db` | Nama database PostgreSQL |
| `POSTGRES_USER` | `tp_user` | Username database PostgreSQL |
| `POSTGRES_PASSWORD` | `str0ng-db-p4ssword!` | Password database — gunakan password yang kuat |

**Generate `SECRET_KEY` yang aman:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

#### Langkah 3 — Buat `production` environment dan set protection rule

Pipeline deploy menggunakan environment bernama `production` yang memerlukan approval manual sebelum deploy berjalan.

1. Di GitHub repository, klik **Settings** → **Environments**
2. Klik **New environment** → beri nama `production`
3. Centang **Required reviewers** → tambahkan username reviewer (misal: diri sendiri)
4. Klik **Save protection rules**

> Setiap push ke `main` akan meminta approval dari reviewer sebelum deploy ke EC2 dijalankan.

---

#### Langkah 4 — Pastikan self-hosted runner terdaftar (EC2)

Deploy job berjalan di EC2 via self-hosted runner. Pastikan runner sudah terpasang di server:

1. Di GitHub, klik **Settings** → **Actions** → **Runners**
2. Klik **New self-hosted runner** → pilih OS Linux
3. Ikuti perintah instalasi yang ditampilkan GitHub di dalam EC2:

```bash
# Di dalam EC2 — jalankan perintah yang diberikan GitHub, contoh:
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.x.x.tar.gz -L https://github.com/actions/runner/releases/...
tar xzf ./actions-runner-linux-x64-2.x.x.tar.gz
./config.sh --url https://github.com/<org>/<repo> --token <TOKEN>
sudo ./svc.sh install
sudo ./svc.sh start
```

4. Setelah runner aktif, statusnya berubah menjadi **Idle** di halaman Runners

---

#### Ringkasan secrets yang dibutuhkan

```
Repository → Settings → Secrets and variables → Actions

✅ SECRET_KEY         → django secret key (50 char random)
✅ ALLOWED_HOSTS      → domain production
✅ POSTGRES_DB        → tp_db
✅ POSTGRES_USER      → tp_user
✅ POSTGRES_PASSWORD  → password database

Repository → Settings → Environments

✅ production         → required reviewers aktif
```
