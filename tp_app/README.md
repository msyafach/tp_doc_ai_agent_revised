# Transfer Pricing Local File Generator

An AI-powered Transfer Pricing documentation generator compliant with **PMK-172 Year 2023** (Indonesian regulations). Built with **Streamlit**, **LangGraph**, **LangChain**, and **python-docx**.

## LLM Providers

| Provider | Models | Best For |
|----------|--------|----------|
| **Groq** (default) | `llama-3.3-70b-versatile`, `deepseek-r1-distill-llama-70b`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768` | Fast inference, free tier available |
| **OpenAI** | `gpt-4o-mini`, `gpt-4o`, `gpt-4.1-mini`, `gpt-4.1-nano` | Highest quality output |

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Streamlit UI                        │
│  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Company  │ │Financial│ │Comparable│ │  Review  │ │
│  │  Input   │ │  Data   │ │Companies │ │ & Export │ │
│  └────┬─────┘ └────┬────┘ └────┬─────┘ └────┬─────┘ │
│       │            │           │             │        │
│  ┌────▼────────────▼───────────▼─────────────▼────┐  │
│  │           LangGraph Orchestrator                │  │
│  │  ┌──────────────────────────────────────────┐  │  │
│  │  │ Phase 0: Business Activities (LLM)        │  │  │
│  │  │  → Business Activities Description        │  │  │
│  │  ├──────────────────────────────────────────┤  │  │
│  │  │ Phase 1: Research (Tavily Web Search)     │  │  │
│  │  │  → Global Industry Analysis               │  │  │
│  │  │  → Indonesian Industry Analysis            │  │  │
│  │  │  → Business Environment                    │  │  │
│  │  ├──────────────────────────────────────────┤  │  │
│  │  │ Phase 2: Analysis (LLM)                   │  │  │
│  │  │  → Functional Analysis                     │  │  │
│  │  │  → Business Characterization               │  │  │
│  │  ├──────────────────────────────────────────┤  │  │
│  │  │ Phase 3: Transactions & Method (LLM)      │  │  │
│  │  │  → Background of Affiliated Transactions   │  │  │
│  │  │  → Comparability Analysis                  │  │  │
│  │  │  → Method Justification                    │  │  │
│  │  │  → PLI Rationale                           │  │  │
│  │  ├──────────────────────────────────────────┤  │  │
│  │  │ Phase 4: Summary (LLM)                    │  │  │
│  │  │  → Conclusion                              │  │  │
│  │  │  → P/L Overview                            │  │  │
│  │  │  → Executive Summary                       │  │  │
│  │  └──────────────────────────────────────────┘  │  │
│  └────────────────────┬───────────────────────────┘  │
│                       │                               │
│  ┌────────────────────▼───────────────────────────┐  │
│  │           python-docx Export Engine              │  │
│  │  Template Sections + Manual Data + AI Content   │  │
│  │  → Professional DOCX Document                   │  │
│  └─────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

## Section Classification

| Category | Sections | How it works |
|----------|----------|-------------|
| 🟢 **Template** | Glossary, Statement Letter, TP Regulations (Ch.2), TP Method Descriptions, Search Criteria Descriptions, Supply Chain (4.2.1), Functional Analysis Table (4.2.2), Transaction Scheme (4.1.2.2), References | Standard regulatory/boilerplate text auto-populated from template. Identical structure across all companies; user fills in company-specific fields via placeholders. |
| 🔵 **Manual Input** | Company Identity, Ownership (with source), Management (with source), Affiliated Parties, Business Activities, Products, Affiliated Transactions Table (Table 4.1), Independent Transactions Table (Table 4.2), Pricing Policy, Financial Data (P&L, current + prior year), Comparable Companies (from BvD), TP Analysis Parameters, Non-Financial Events | User provides company-specific data through the UI wizard forms. |
| 🤖 **AI Agent** | Business Activities Description, Global Industry Analysis, Indonesian Industry Analysis, Business Environment, Functional Analysis Narrative, Business Characterization, Background of Affiliated Transactions (4.1.2.1), Comparability Analysis, Method Selection Justification, PLI Rationale, P/L Overview, Conclusion, Executive Summary | AI agents generate content via web research (Tavily) and LLM analysis (Groq/OpenAI). |

## Setup

### 1. Install dependencies

```bash
# Using uv (recommended)
uv sync
```

### 2. Set API keys (choose one LLM provider)

```bash
# Option A: Groq (recommended — fast & free tier)
export GROQ_API_KEY="gsk_..."
export TAVILY_API_KEY="tvly-..."

# Option B: OpenAI
export OPENAI_API_KEY="sk-..."
export TAVILY_API_KEY="tvly-..."
```

Or enter them in the sidebar of the Streamlit app. You can switch between providers at runtime.

### 3. Run the application

```bash
cd tp_app
uv run streamlit run app.py
```

## Usage Workflow

1. **Steps 0-8**: Fill in company-specific data through the wizard forms
2. **Step 9**: Run AI agents to auto-generate research and analysis sections
3. **Step 9**: Review and edit any AI-generated content in the UI
4. **Step 10**: Export the complete document as .docx

## Key Features

- **No Hallucination Guard**: AI agents only use verified web search results and user-provided data. No invented statistics.
- **Editable AI Output**: All AI-generated sections can be reviewed and manually edited before export.
- **Regenerate Individual Sections**: Each AI section can be regenerated independently.
- **Save/Load Projects**: Export and import project data as JSON.
- **PMK-172 Compliant**: Document structure follows Indonesian TP regulation requirements.
- **Hybrid Rendering**: Template-only sections (boilerplate, regulatory tables) are preserved from the master DOCX template; AI and manual sections are injected via `_overwrite_section_bodies`.
- **Document Upload**: Upload existing TP documents (PDF/DOCX) to auto-extract field values via RAG.

## Document Structure (PMK-172)

1. **Glossary & Abbreviations** — Template
2. **Statement Letter** — Template
3. **Executive Summary** — AI Generated (Purpose, Conclusion Summary, Scope)
4. **Transfer Pricing Regulations** — Template (Indonesian TP law framework)
5. **Identity & Business Activities**
   - Company identity, shareholders, management — Manual Input
   - Business activities, products — AI + Manual
   - Business environment — AI (web research)
6. **Affiliated Transactions & Functional Analysis**
   - Transaction tables (Table 4.1, 4.2) — Manual Input
   - Transaction scheme (4.1.2.2) — Template (manually fillable in Word)
   - Background of affiliated transactions (4.1.2.1) — AI Generated
   - Supply chain description (4.2.1) — Template
   - Functional analysis table (4.2.2) — Template (boilerplate + company vars)
   - Business characterization — AI Generated
7. **Application of Arm's Length Principle**
   - Industry analysis (global + Indonesia) — AI (web research)
   - Comparability analysis — AI Generated
   - Method selection & PLI rationale — AI Generated
   - Conclusion — AI Generated
8. **Financial Information** — Manual Input (P&L data, current + prior year)
   - P/L Overview narrative — AI Generated
9. **Non-Financial Events** — Manual Input
10. **References** — Template
11. **Appendices** — Template (Organization structure, affiliated parties, comparable companies, financial statements, rejection matrix)

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI, session state, all form steps |
| `agents/orchestrator.py` | LangGraph workflow builder and state definition |
| `agents/nodes.py` | All AI agent node functions + LLM factory |
| `agents/extraction_agent.py` | Document upload extraction (PageIndex / Vector RAG) |
| `export/docx_template_export.py` | DOCX rendering via docxtpl + post-processing |
| `config.py` | `TPDocState` TypedDict, enums |
| `templates/sections.py` | Static regulatory boilerplate text |
| `utils/document_processor.py` | 2-tier PDF/DOCX processing pipeline |
| `TP_Local_File_TEMPLATE.docx` | Master Word template with Jinja2 placeholders |
