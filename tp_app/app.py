"""
Transfer Pricing Local File Documentation Generator
====================================================
Streamlit application with LangGraph agent orchestration.

Sections are categorized as:
  🟢 TEMPLATE   - Standard regulatory text (auto-populated)
  🔵 MANUAL     - User must input company-specific data
  🤖 AUTOMATED  - AI agent generates content via web research + LLM
"""
import streamlit as st
import json
import os
import tempfile
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TP Local File Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Imports ──────────────────────────────────────────────────────────────────
from agent_config import (
    BUSINESS_TYPES, TP_METHODS, PLI_OPTIONS, TRANSACTION_TYPES,
)
from templates.sections import GLOSSARY, REFERENCES


# ─── Session state initialization ─────────────────────────────────────────────
def init_state():
    defaults = {
        "step": 0,
        # Document upload
        "uploaded_docs_processed": False,
        "doc_extraction_result": {},
        "doc_vectorstore": None,
        "company_name": "",
        "company_short_name": "",
        "company_address": "",
        "establishment_info": "",
        "fiscal_year": "2024",
        "shareholders": [{"name": "", "shares": "", "capital": "", "percentage": ""}],
        "shareholders_source": "",
        "management": [{"position": "", "name": ""}],
        "management_source": "",
        "employee_count": "",
        "affiliated_parties": [{"name": "", "country": "", "relationship": "", "transaction_type": ""}],
        "parent_company": "",
        "parent_group": "",
        "brand_name": "",  # product/trade brand (e.g. "SANY"); defaults to company_short if empty
        "business_activities_description": "",
        "products": [{"name": "", "description": ""}],
        "business_strategy": "",
        "business_restructuring": "",
        "transaction_type": "Purchase of tangible goods",
        "transaction_counterparties": [],
        "transaction_details_text": "",
        "pricing_policy": "",
        "affiliated_transactions": [{"name": "", "country": "", "affiliation_type": "", "transaction_type": "", "type_of_product": "", "amount_idr": "", "quantity": "", "price_per_unit": ""}],
        "independent_transactions": [{"name": "", "country": "", "transaction_type": "", "value": ""}],
        "financial_data": {},
        "financial_data_prior": {},
        "comparable_companies": [{"name": "", "country": "", "description": "", "ros_data": ""}],
        "search_criteria_results": [],
        "rejection_matrix": [{"name": "", "limited_financial_statement": False, "negative_margin": False,
                               "consolidated_financial_statement": False, "different_main_activity": False,
                               "non_comparable_line_of_business": False, "limited_information_website": False,
                               "accepted": False}],
        "selected_method": "TNMM",
        "selected_pli": "ROS",
        "tested_party": "",
        "analysis_period": "2020-2022",
        "quartile_range": {"q1": 0.0, "median": 0.0, "q3": 0.0},
        "tested_party_ratio": 0.0,
        "non_financial_events": "",
        # Org structure (Appendix 1)
        "org_structure_description": "",
        "org_structure_departments": [{"name": "", "head": "", "employees": ""}],
        # Agent outputs
        "industry_analysis_global": "",
        "industry_analysis_indonesia": "",
        "company_location_analysis": "",
        "company_location_sources": [],
        "industry_regulations_text": "",
        "industry_regulations_sources": [],
        "business_environment_overview": "",
        "business_environment_sources": [],
        "executive_summary": "",
        "conclusion_text": "",
        "background_transaction": "",
        "functional_analysis_narrative": "",
        "business_characterization_text": "",
        "method_selection_justification": "",
        "pli_selection_rationale": "",
        "comparability_analysis_narrative": "",
        "agent_ran": False,
        "agent_errors": [],
        # New AI-generated outputs
        "supply_chain_management": "",
        "comparable_descriptions": {},
        # Comparability Analysis table (Table 5.1) — manual input
        "comparability_factors": [
            {"factor": "Contract Terms and Conditions", "description": ""},
            {"factor": "Product Characteristics",       "description": ""},
            {"factor": "Functional Analysis",           "description": ""},
            {"factor": "Business Strategy",             "description": ""},
            {"factor": "Economic Conditions",           "description": ""},
        ],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─── Helper functions ─────────────────────────────────────────────────────────

def add_dynamic_rows(key, template, label="Add Row"):
    """Helper for dynamic list inputs."""
    if st.button(f"➕ {label}", key=f"add_{key}"):
        st.session_state[key].append(template.copy())
    
    to_remove = None
    for i, item in enumerate(st.session_state[key]):
        cols = st.columns([*[1]*len(template), 0.3])
        for j, (field, default) in enumerate(template.items()):
            item[field] = cols[j].text_input(
                field.replace("_", " ").title(),
                value=item.get(field, default),
                key=f"{key}_{i}_{field}",
                label_visibility="visible" if i == 0 else "collapsed",
            )
        if cols[-1].button("🗑️", key=f"rm_{key}_{i}") and len(st.session_state[key]) > 1:
            to_remove = i
    
    if to_remove is not None:
        st.session_state[key].pop(to_remove)
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

STEPS = [
    "📎 Upload Documents",
    "🏢 Company Identity",
    "👥 Ownership & Management",
    "🤝 Affiliated Parties",
    "📦 Business Activities",
    "💰 Transactions",
    "📊 Financial Data",
    "🔍 Comparable Companies",
    "⚙️ TP Analysis Parameters",
    "📝 Non-Financial Events",
    "🤖 Run AI Agents",
    "✅ Review & Export",
]

with st.sidebar:
    st.title("📄 TP Local File Generator")
    st.caption("PMK-172 Year 2023 Compliant")
    
    st.divider()
    st.subheader("Navigation")
    _nav_step = st.session_state.step
    st.progress(_nav_step / (len(STEPS) - 1), text=f"Step {_nav_step + 1} of {len(STEPS)}")

    for i, step_name in enumerate(STEPS):
        is_current = st.session_state.step == i
        if st.button(
            step_name,
            key=f"nav_{i}",
            use_container_width=True,
            type="primary" if is_current else "secondary",
        ):
            st.session_state.step = i
            st.rerun()
    
    st.divider()
    st.subheader("🔑 API Keys & LLM")
    
    llm_provider = st.selectbox(
        "LLM Provider",
        ["groq", "openai"],
        index=0,
        key="llm_provider_select",
        help="Groq = fast (Llama 3.3 70B), OpenAI = high quality (GPT-4o)",
    )
    os.environ["LLM_PROVIDER"] = llm_provider
    
    if llm_provider == "groq":
        groq_key = st.text_input("Groq API Key *", type="password",
                                  value=os.environ.get("GROQ_API_KEY", ""),
                                  key="groq_key_input")
        groq_model = st.selectbox(
            "Groq Model",
            ["llama-3.3-70b-versatile", "deepseek-r1-distill-llama-70b",
             "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            index=0,
            key="groq_model_select",
        )
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key
        os.environ["GROQ_MODEL"] = groq_model
    else:
        openai_key = st.text_input("OpenAI API Key *", type="password",
                                    value=os.environ.get("OPENAI_API_KEY", ""),
                                    key="openai_key_input")
        openai_model = st.selectbox(
            "OpenAI Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1-nano"],
            index=0,
            key="openai_model_select",
        )
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        os.environ["OPENAI_MODEL"] = openai_model
    
    st.divider()
    tavily_key = st.text_input("Tavily API Key *", type="password",
                                value=os.environ.get("TAVILY_API_KEY", ""),
                                key="tavily_key_input",
                                help="Required for industry analysis web research")
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key
    
    st.divider()
    st.caption("Legend:")
    st.markdown("🟢 **Template** - Auto-filled regulatory text")
    st.markdown("🔵 **Manual** - You must provide this data")
    st.markdown("🤖 **AI Agent** - Auto-generated by AI")

    st.divider()
    st.subheader("💾 Save Project")
    _save_data = {k: v for k, v in st.session_state.items()
                  if not k.startswith("_") and k not in [
                      "groq_key_input", "openai_key_input", "tavily_key_input",
                      "llm_provider_select", "groq_model_select", "openai_model_select"]}
    _fy = st.session_state.get("fiscal_year", "")
    _co = st.session_state.get("company_short_name", "project")
    st.download_button(
        "⬇️ Save Project JSON",
        data=json.dumps(_save_data, indent=2, default=str),
        file_name=f"tp_project_{_co}_FY{_fy}.json",
        mime="application/json",
        use_container_width=True,
        help="Download your current progress as a JSON file to continue later",
    )

    st.divider()
    st.subheader("🧪 Testing")
    if st.button("🧪 Fill Dummy Data", use_container_width=True, help="Auto-fill all form fields with realistic test data"):
        from utils.dummy_data import DUMMY_DATA
        for k, v in DUMMY_DATA.items():
            st.session_state[k] = v
        st.toast("✅ Dummy data loaded!", icon="🧪")
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

current_step = st.session_state.step

# ─── Step 0: Upload Documents ─────────────────────────────────────────────────
if current_step == 0:
    st.header("📎 Upload Documents")
    st.info(
        "📂 **Optional Step** — Upload your company documents (Annual Report, prior TP doc, "
        "financial statements, etc.) and let the AI automatically extract and pre-fill the form fields. "
        "All uploads are processed locally and stored only in your session."
    )

    MAX_MB = 20
    ACCEPTED_TYPES = ["pdf", "docx", "xlsx", "txt"]

    uploaded_files = st.file_uploader(
        f"Upload documents (max {MAX_MB} MB each)",
        type=ACCEPTED_TYPES,
        accept_multiple_files=True,
        help=f"Supported: {', '.join(t.upper() for t in ACCEPTED_TYPES)}. Max size: {MAX_MB} MB per file.",
    )

    # ── File size validation ──────────────────────────────────────────────────
    valid_uploads = []
    if uploaded_files:
        for uf in uploaded_files:
            size_mb = uf.size / (1024 * 1024)
            if size_mb > MAX_MB:
                st.error(
                    f"❌ **{uf.name}** is {size_mb:.1f} MB — exceeds the {MAX_MB} MB limit. "
                    f"Please compress or split the file."
                )
            else:
                valid_uploads.append(uf)
                st.success(f"✅ **{uf.name}** ({size_mb:.1f} MB) — ready")

    # ── Process button ────────────────────────────────────────────────────────
    st.divider()
    col_btn, col_status = st.columns([1, 2])

    with col_btn:
        can_process = len(valid_uploads) > 0
        process_clicked = st.button(
            "🔍 Process & Extract",
            type="primary",
            use_container_width=True,
            disabled=not can_process,
            help="Load documents, embed them, and run the AI extraction agent.",
        )

    with col_status:
        if st.session_state.uploaded_docs_processed:
            st.success("✅ Documents processed — extraction complete!")
        elif not valid_uploads:
            st.caption("Upload at least one valid file to proceed.")

    if process_clicked and valid_uploads:
        with st.status("Processing documents...", expanded=True) as proc_status:
            try:
                from utils.document_processor import process_uploaded_files
                from agents.extraction_agent import extract_form_fields
                from agents.nodes import get_llm

                st.write("📄 Analysing documents...")
                doc_context, load_errors = process_uploaded_files(valid_uploads)

                for err in load_errors:
                    st.warning(f"⚠️ {err}")

                if doc_context is None:
                    proc_status.update(
                        label="❌ No content could be extracted.", state="error"
                    )
                else:
                    # Show which strategy was selected
                    if doc_context.strategy == "page_index":
                        st.info(
                            f"🌳 **Strategy: PageIndex** — "
                            f"{doc_context.page_count} pages detected (< 20). "
                            f"Using hierarchical tree retrieval for precise extraction."
                        )
                    else:
                        pg_info = f" ({doc_context.page_count} pages)" if doc_context.page_count else ""
                        st.info(
                            f"🔍 **Strategy: Vector RAG** — "
                            f"Document(s){pg_info}. "
                            f"Using FAISS similarity search for extraction."
                        )

                    st.write("🧠 Running AI extraction agent...")
                    llm = get_llm()
                    extraction = extract_form_fields(doc_context, llm)

                    st.session_state.doc_context = doc_context
                    st.session_state.doc_extraction_result = extraction
                    st.session_state.uploaded_docs_processed = True

                    proc_status.update(
                        label="✅ Extraction complete! Review the results below.",
                        state="complete",
                    )
                    st.rerun()

            except Exception as exc:
                import traceback
                proc_status.update(label=f"❌ Error: {exc}", state="error")
                st.error(f"Processing failed: {exc}")
                st.code(traceback.format_exc())

    # ── Extraction review panel ───────────────────────────────────────────────
    if st.session_state.uploaded_docs_processed and st.session_state.doc_extraction_result:
        st.divider()
        st.subheader("📋 Extraction Results — Review & Accept")
        st.caption(
            "Review the values extracted from your documents. "
            "Accept individual sections or click **Accept All** to pre-fill all form fields at once."
        )

        extraction = st.session_state.doc_extraction_result

        # ─── Summary table ─────────────────────────────────────────────────
        from agents.extraction_agent import get_extraction_summary
        summary = get_extraction_summary(extraction)

        with st.expander("📊 Extraction Summary", expanded=True):
            cols = st.columns(2)
            items = list(summary.items())
            mid = (len(items) + 1) // 2
            for i, (label, status) in enumerate(items):
                cols[0 if i < mid else 1].markdown(f"**{label}:** {status}")

        # ─── Section-by-section review ─────────────────────────────────────

        def _accept_section(keys: list):
            """Copy extracted values for given keys into session state."""
            for k in keys:
                if k in extraction and extraction[k] not in [None, "", [], {}]:
                    st.session_state[k] = extraction[k]

        def _preview_value(val):
            """Return a human-readable preview of an extracted value."""
            if val is None:
                return "*Not found in documents*"
            if isinstance(val, list):
                return f"{len(val)} item(s): " + ", ".join(
                    str(list(v.values())[0]) for v in val[:3] if isinstance(v, dict) and v
                )
            if isinstance(val, dict):
                return ", ".join(f"{k}: {v}" for k, v in list(val.items())[:4] if v)
            return str(val)[:300]

        # Company Identity
        with st.expander("🏢 Company Identity", expanded=False):
            id_keys = ["company_name", "company_short_name", "company_address",
                       "establishment_info", "fiscal_year", "parent_company", "parent_group"]
            for k in id_keys:
                val = extraction.get(k)
                st.markdown(f"**{k.replace('_', ' ').title()}:** {_preview_value(val)}")
            if st.button("✅ Accept Company Identity", key="accept_company_id"):
                _accept_section(id_keys)
                st.toast("✅ Company Identity accepted!", icon="✅")

        # Shareholders
        with st.expander("👥 Shareholders", expanded=False):
            val = extraction.get("shareholders")
            if val:
                for sh in val:
                    st.markdown(f"- **{sh.get('name','')}** — {sh.get('percentage','')} "
                                f"| Shares: {sh.get('shares','')} | Capital: {sh.get('capital','')}")
            else:
                st.caption("Not found in documents.")
            if st.button("✅ Accept Shareholders", key="accept_shareholders"):
                _accept_section(["shareholders"])
                st.toast("✅ Shareholders accepted!", icon="✅")

        # Management
        with st.expander("🎯 Management / Board", expanded=False):
            val = extraction.get("management")
            if val:
                for m in val:
                    st.markdown(f"- **{m.get('position','')}:** {m.get('name','')}")
            else:
                st.caption("Not found in documents.")
            if st.button("✅ Accept Management", key="accept_management"):
                _accept_section(["management", "employee_count"])
                st.toast("✅ Management accepted!", icon="✅")

        # Affiliated Parties
        with st.expander("🤝 Affiliated Parties", expanded=False):
            val = extraction.get("affiliated_parties")
            if val:
                for ap in val:
                    st.markdown(f"- **{ap.get('name','')}** ({ap.get('country','')}) — "
                                f"{ap.get('relationship','')} | {ap.get('transaction_type','')}")
            else:
                st.caption("Not found in documents.")
            if st.button("✅ Accept Affiliated Parties", key="accept_affiliated"):
                _accept_section(["affiliated_parties"])
                st.toast("✅ Affiliated Parties accepted!", icon="✅")

        # Business Activities
        with st.expander("📦 Business Activities", expanded=False):
            for k in ["business_activities_description", "business_strategy", "business_restructuring"]:
                val = extraction.get(k)
                st.markdown(f"**{k.replace('_',' ').title()}:**")
                st.caption(_preview_value(val))
            if st.button("✅ Accept Business Activities", key="accept_biz"):
                _accept_section(["business_activities_description", "business_strategy",
                                 "business_restructuring"])
                st.toast("✅ Business Activities accepted!", icon="✅")

        # Products
        with st.expander("🛒 Products / Services", expanded=False):
            val = extraction.get("products")
            if val:
                for p in val:
                    st.markdown(f"- **{p.get('name','')}:** {p.get('description','')}")
            else:
                st.caption("Not found in documents.")
            if st.button("✅ Accept Products", key="accept_products"):
                _accept_section(["products"])
                st.toast("✅ Products accepted!", icon="✅")

        # Transaction Details
        with st.expander("💰 Transaction Details", expanded=False):
            for k in ["transaction_details_text", "pricing_policy"]:
                val = extraction.get(k)
                st.markdown(f"**{k.replace('_',' ').title()}:**")
                st.caption(_preview_value(val))
            if st.button("✅ Accept Transaction Details", key="accept_txn"):
                _accept_section(["transaction_details_text", "pricing_policy"])
                st.toast("✅ Transaction Details accepted!", icon="✅")

        # Financial Data
        with st.expander("📊 Financial Data", expanded=False):
            fin = extraction.get("financial_data", {})
            fin_prior = extraction.get("financial_data_prior", {})
            fy = extraction.get("fiscal_year", st.session_state.fiscal_year)
            if fin:
                st.markdown(f"**Current Year ({fy}):**")
                st.json(fin)
            if fin_prior:
                st.markdown("**Prior Year:**")
                st.json(fin_prior)
            if not fin and not fin_prior:
                st.caption("Not found in documents.")
            if st.button("✅ Accept Financial Data", key="accept_fin"):
                _accept_section(["financial_data", "financial_data_prior"])
                st.toast("✅ Financial Data accepted!", icon="✅")

        # ─── Accept All button ─────────────────────────────────────────────
        st.divider()
        col_all1, col_all2 = st.columns([1, 2])
        with col_all1:
            if st.button("✅ Accept All Extracted Data", type="primary",
                         use_container_width=True, key="accept_all"):
                all_keys = [
                    "company_name", "company_short_name", "company_address",
                    "establishment_info", "fiscal_year", "parent_company", "parent_group",
                    "shareholders", "management", "employee_count",
                    "affiliated_parties",
                    "business_activities_description", "business_strategy", "business_restructuring",
                    "products",
                    "transaction_details_text", "pricing_policy",
                    "financial_data", "financial_data_prior",
                ]
                _accept_section(all_keys)
                st.success("✅ All extracted data accepted and applied to the form!")
                st.rerun()
        with col_all2:
            st.caption(
                "Accepting data here pre-fills the corresponding form fields. "
                "You can still edit any field manually in its dedicated step."
            )

        st.divider()
        if st.button("🗑️ Clear Extraction & Re-upload", key="clear_extraction"):
            st.session_state.uploaded_docs_processed = False
            st.session_state.doc_extraction_result = {}
            st.session_state.doc_vectorstore = None
            st.rerun()


# ─── Step 1: Company Identity ─────────────────────────────────────────────────
elif current_step == 1:
    st.header("🏢 Company Identity")
    st.info("🔵 **Manual Input** — Enter company identification details")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.company_name = st.text_input(
            "Full Company Name *", 
            value=st.session_state.company_name,
            placeholder="e.g., PT Sany Perkasa"
        )
        st.session_state.company_short_name = st.text_input(
            "Short Name / Abbreviation *",
            value=st.session_state.company_short_name,
            placeholder="e.g., PT SP"
        )
        st.session_state.fiscal_year = st.text_input(
            "Fiscal Year *",
            value=st.session_state.fiscal_year,
            placeholder="e.g., 2024"
        )
    with col2:
        st.session_state.company_address = st.text_area(
            "Company Address *",
            value=st.session_state.company_address,
            placeholder="e.g., Jalan Griya Utama, Rukun Puri Mutiara Blok A 67-68, Sunter Agung, North Jakarta"
        )
        st.session_state.establishment_info = st.text_area(
            "Establishment Information",
            value=st.session_state.establishment_info,
            placeholder="Deed number, date, notary, Ministry approval details..."
        )
    
    st.session_state.parent_company = st.text_input(
        "Direct Parent Company",
        value=st.session_state.parent_company,
        placeholder="e.g., Sany Southeast Asia Pte, Ltd"
    )
    st.session_state.parent_group = st.text_input(
        "Ultimate Parent Group",
        value=st.session_state.parent_group,
        placeholder="e.g., Sany Group"
    )
    st.session_state.brand_name = st.text_input(
        "Product / Trade Brand Name",
        value=st.session_state.get("brand_name", ""),
        placeholder="e.g., SANY (leave blank to use company short name)",
        help="The brand name used for products/services, if different from the company name",
    )


# ─── Step 2: Ownership & Management ──────────────────────────────────────────
elif current_step == 2:
    st.header("👥 Ownership & Management Structure")
    st.info("🔵 **Manual Input** — Enter shareholder and management details")
    
    st.subheader("Shareholders")
    add_dynamic_rows(
        "shareholders",
        {"name": "", "shares": "", "capital": "", "percentage": ""},
        "Add Shareholder"
    )
    st.session_state.shareholders_source = st.text_input(
        "Source (shareholders table)",
        value=st.session_state.shareholders_source,
        placeholder="e.g. Source: Management SMI, 31 December 2024",
    )

    st.divider()
    st.subheader("Management / Board of Directors")
    add_dynamic_rows(
        "management",
        {"position": "", "name": ""},
        "Add Management"
    )
    st.session_state.management_source = st.text_input(
        "Source (management table)",
        value=st.session_state.management_source,
        placeholder="e.g. Source: Management SMI, 31 December 2024",
    )
    
    st.divider()
    st.session_state.employee_count = st.text_input(
        "Total Permanent Employees",
        value=st.session_state.employee_count,
        placeholder="e.g., 1,034"
    )


# ─── Step 3: Affiliated Parties ───────────────────────────────────────────────
elif current_step == 3:
    st.header("🤝 Affiliated Parties")
    st.info("🔵 **Manual Input** — List all related party entities")
    
    add_dynamic_rows(
        "affiliated_parties",
        {"name": "", "country": "", "relationship": "", "transaction_type": ""},
        "Add Affiliated Party"
    )


# ─── Step 4: Business Activities ─────────────────────────────────────────────
elif current_step == 4:
    st.header("📦 Business Activities & Products")
    st.info("🔵 **Manual Input** — Describe the company's business")
    
    st.session_state.business_activities_description = st.text_area(
        "Business Activities Description *",
        value=st.session_state.business_activities_description,
        height=200,
        placeholder="Describe the company's main business activities, operational aspects, industry sector..."
    )
    
    # ── Organization Structure (Appendix 1) ───────────────────────────────────
    st.divider()
    st.subheader("🏗️ Organization Structure (Appendix 1)")
    st.caption("This will appear as Appendix 1 in the generated document.")

    st.session_state.org_structure_description = st.text_area(
        "Description",
        value=st.session_state.org_structure_description,
        height=100,
        placeholder="Briefly describe the organizational structure (e.g., 'The company is organised into 5 divisions...')"
    )

    st.markdown("**Departments / Units**")
    if "org_structure_departments" not in st.session_state:
        st.session_state.org_structure_departments = [{"name": "", "head": "", "employees": ""}]

    if st.button("➕ Add Department", key="add_org_dept"):
        st.session_state.org_structure_departments.append({"name": "", "head": "", "employees": ""})

    dept_to_remove = None
    for i, dept in enumerate(st.session_state.org_structure_departments):
        dc1, dc2, dc3, dc4 = st.columns([2.5, 2.5, 1.5, 0.5])
        dept["name"] = dc1.text_input(
            "Dept / Unit Name", value=dept.get("name", ""),
            key=f"org_dept_{i}_name",
            label_visibility="visible" if i == 0 else "collapsed"
        )
        dept["head"] = dc2.text_input(
            "Head / PIC", value=dept.get("head", ""),
            key=f"org_dept_{i}_head",
            label_visibility="visible" if i == 0 else "collapsed"
        )
        dept["employees"] = dc3.text_input(
            "# Employees", value=dept.get("employees", ""),
            key=f"org_dept_{i}_emp",
            label_visibility="visible" if i == 0 else "collapsed"
        )
        if dc4.button("🗑️", key=f"rm_org_dept_{i}") and len(st.session_state.org_structure_departments) > 1:
            dept_to_remove = i

    if dept_to_remove is not None:
        st.session_state.org_structure_departments.pop(dept_to_remove)
        st.rerun()

    st.markdown("**Org Chart Image** (optional)")
    if "org_structure_image" not in st.session_state:
        st.session_state.org_structure_image = None

    org_img_uploaded = st.file_uploader(
        "Upload org chart (PNG / JPG / PDF)",
        type=["png", "jpg", "jpeg"],
        key="org_chart_uploader",
        help="Upload an org chart image to embed in Appendix 1"
    )
    if org_img_uploaded is not None:
        st.session_state.org_structure_image = org_img_uploaded.read()

    if st.session_state.org_structure_image:
        st.image(st.session_state.org_structure_image, caption="Org Chart Preview", use_container_width=True)
        if st.button("🗑️ Remove Org Chart", key="rm_org_chart"):
            st.session_state.org_structure_image = None
            st.rerun()
    
    st.divider()
    st.subheader("Products / Services")

    # Ensure product_images dict
    if "product_images" not in st.session_state:
        st.session_state.product_images = {}

    if st.button("➕ Add Product", key="add_products"):
        st.session_state.products.append({"name": "", "description": ""})

    to_remove = None
    for i, item in enumerate(st.session_state.products):
        st.markdown(f"**Product {i+1}**")
        c1, c2, c3 = st.columns([2, 2, 1])
        item["name"] = c1.text_input(
            "Product Name", value=item.get("name", ""),
            key=f"products_{i}_name", label_visibility="visible" if i == 0 else "collapsed"
        )
        item["description"] = c2.text_input(
            "Description", value=item.get("description", ""),
            key=f"products_{i}_description", label_visibility="visible" if i == 0 else "collapsed"
        )
        uploaded = c3.file_uploader(
            "Image", type=["png", "jpg", "jpeg"],
            key=f"products_{i}_img",
            label_visibility="visible" if i == 0 else "collapsed",
        )
        if uploaded is not None:
            st.session_state.product_images[i] = uploaded.read()

        # Show preview + delete
        img_cols = st.columns([4, 1])
        if i in st.session_state.product_images:
            img_cols[0].image(st.session_state.product_images[i], width=150,
                              caption=item.get("name", f"Product {i+1}"))
        if img_cols[1].button("🗑️", key=f"rm_products_{i}") and len(st.session_state.products) > 1:
            to_remove = i

    if to_remove is not None:
        st.session_state.products.pop(to_remove)
        # Re-index product_images
        new_images = {}
        for k, v in st.session_state.product_images.items():
            if k < to_remove:
                new_images[k] = v
            elif k > to_remove:
                new_images[k - 1] = v
        st.session_state.product_images = new_images
        st.rerun()
    
    st.divider()
    st.session_state.business_strategy = st.text_area(
        "Business Strategy",
        value=st.session_state.business_strategy,
        height=150,
        placeholder="Describe the company's business strategy..."
    )
    
    st.session_state.business_restructuring = st.text_area(
        "Business Restructuring / Transfer of Intangible Assets",
        value=st.session_state.business_restructuring,
        placeholder="Leave blank if no restructuring occurred in the fiscal year"
    )

    st.divider()
    st.subheader("Business Characteristics (Section 4.2.3)")
    st.info(
        "🔵 **Manual Input** — Jelaskan karakteristik bisnis perusahaan (mis. Contract Manufacturer, "
        "Distributor, dll.) berdasarkan hasil analisis fungsional. Teks ini akan langsung muncul "
        "di bagian **4.2.3 Business Characteristics** pada dokumen DOCX yang di-export."
    )
    st.session_state.business_characterization_text = st.text_area(
        "Business Characterization Text",
        value=st.session_state.get("business_characterization_text", ""),
        height=250,
        placeholder=(
            "Contoh: Based on the functional analysis provided, the determined business "
            "characterization of PT [Company Name] is a Contract Manufacturer. "
            "This characterization is justified by the fact that [Company Short Name] operates "
            "as a contract manufacturer, producing goods to the technical specifications and "
            "designs provided by its parent company..."
        ),
        key="biz_char_manual",
    )


# ─── Step 5: Transactions ────────────────────────────────────────────────────
elif current_step == 5:
    st.header("💰 Transaction Details")
    st.info("🔵 **Manual Input** — Describe affiliated transactions")
    
    st.session_state.transaction_type = st.selectbox(
        "Primary Transaction Type *",
        TRANSACTION_TYPES,
        index=TRANSACTION_TYPES.index(st.session_state.transaction_type) if st.session_state.transaction_type in TRANSACTION_TYPES else 0,
    )
    
    st.session_state.transaction_details_text = st.text_area(
        "Transaction Details *",
        value=st.session_state.transaction_details_text,
        height=200,
        placeholder="Describe the affiliated transactions in detail: what goods/services, volumes, values, counterparties..."
    )
    
    st.session_state.pricing_policy = st.text_area(
        "Pricing Policy *",
        value=st.session_state.pricing_policy,
        height=150,
        placeholder="Describe how prices are determined for affiliated transactions..."
    )

    st.divider()
    st.subheader("Table 4.1 & Appendix 7 — Affiliated Transactions")
    st.caption("Affiliated Party | Jurisdiction | Form of Affiliation | Type of Transaction | Type of Product | Amount (IDR) | Quantity | Price Per Unit (IDR)")

    _at_list = st.session_state.affiliated_transactions
    _AT_COLS = [
        ("name",             "Affiliated Party"),
        ("country",          "Jurisdiction"),
        ("affiliation_type", "Form of Affiliation"),
        ("transaction_type", "Type of Transaction"),
        ("type_of_product",  "Type of Product"),
        ("amount_idr",       "Amount (IDR)"),
        ("quantity",         "Quantity"),
        ("price_per_unit",   "Price Per Unit (IDR)"),
    ]

    # Header
    _at_header_cols = st.columns([3, 2, 3, 3, 3, 2, 2, 2, 1])
    _at_labels = [lbl for _, lbl in _AT_COLS] + [""]
    for _col, _lbl in zip(_at_header_cols, _at_labels):
        _col.markdown(f"**{_lbl}**")

    for _i, _row in enumerate(_at_list):
        _cols = st.columns([3, 2, 3, 3, 3, 2, 2, 2, 1])
        for _col, (_key, _lbl) in zip(_cols[:8], _AT_COLS):
            _row[_key] = _col.text_input(
                _lbl, value=_row.get(_key, ""),
                key=f"at_{_i}_{_key}", label_visibility="collapsed"
            )
        if _cols[8].button("🗑", key=f"at_del_{_i}") and len(_at_list) > 1:
            _at_list.pop(_i)
            st.rerun()

    st.session_state.affiliated_transactions = _at_list
    if st.button("➕ Add Affiliated Transaction"):
        _at_list.append({"name": "", "country": "", "affiliation_type": "", "transaction_type": "",
                         "type_of_product": "", "amount_idr": "", "quantity": "", "price_per_unit": ""})
        st.rerun()

    st.divider()
    st.subheader("Table 4.2 — Independent Transactions")
    st.caption("Independent Party | Location | Transaction Type | Amount (in IDR)")
    add_dynamic_rows(
        "independent_transactions",
        {"name": "", "country": "", "transaction_type": "", "value": ""},
        "Add Independent Transaction"
    )


# ─── Step 6: Financial Data ──────────────────────────────────────────────────
elif current_step == 6:
    st.header("📊 Financial Data")
    st.info("🔵 **Manual Input** — Enter Profit & Loss data")
    
    fy = st.session_state.fiscal_year
    
    pl_items = [
        ("sales", "Sales / Revenue"),
        ("cogs", "Cost of Goods Sold"),
        ("gross_profit", "Gross Profit"),
        ("gross_margin_pct", "Gross Profit Margin (%)"),
        ("operating_expenses", "Operating Expenses"),
        ("operating_profit", "Operating Profit"),
        ("financial_income", "Financial Income / (Expenses)"),
        ("other_income", "Other Income"),
        ("other_expense", "Other Expense"),
        ("income_before_tax", "Income Before Tax"),
        ("income_tax", "Income Tax"),
        ("net_income", "Net Income"),
    ]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"FY {fy}")
        for key, label in pl_items:
            st.session_state.financial_data[key] = st.text_input(
                label,
                value=st.session_state.financial_data.get(key, ""),
                key=f"fin_{key}",
            )

    with col2:
        try:
            prior_fy = str(int(fy.strip()) - 1)
        except (ValueError, AttributeError):
            prior_fy = "Prior Year"
        st.subheader(f"FY {prior_fy}")
        for key, label in pl_items:
            st.session_state.financial_data_prior[key] = st.text_input(
                label,
                value=st.session_state.financial_data_prior.get(key, ""),
                key=f"fin_prior_{key}",
            )


# ─── Step 7: Comparable Companies ────────────────────────────────────────────
elif current_step == 7:
    st.header("🔍 Comparable Companies")
    st.info("🔵 **Manual Input** — Enter data from Bureau Van Dijk TP Catalyst Database")

    # ── Table 5.1: Comparability Analysis Factors ────────────────────────────
    st.subheader("Table 5.1 — Comparability Analysis Factors")
    st.caption("Describe each comparability factor's relevance for the affiliated-party transactions being analyzed")

    _company_short = st.session_state.get("company_short_name", "Company")
    _fiscal_year   = st.session_state.get("fiscal_year", "")
    st.markdown(
        f"**Table 5.1 Comparability Analysis of {_company_short} "
        f"Affiliated Transactions FY {_fiscal_year}**"
    )

    if st.button("➕ Add Comparability Factor", key="add_comp_factor"):
        st.session_state.comparability_factors.append({"factor": "", "description": ""})

    _cf_to_remove = None
    for _fi, _cr in enumerate(st.session_state.comparability_factors):
        col_no, col_fac, col_desc, col_del = st.columns([0.15, 1.2, 3.2, 0.15])
        col_no.markdown(
            f"<div style='padding-top:32px;text-align:center;font-weight:bold'>{_fi + 1}</div>",
            unsafe_allow_html=True,
        )
        _cr["factor"] = col_fac.text_input(
            "Comparability Factor",
            value=_cr.get("factor", ""),
            key=f"cf_factor_{_fi}",
            label_visibility="visible" if _fi == 0 else "collapsed",
        )
        _cr["description"] = col_desc.text_area(
            "Description",
            value=_cr.get("description", ""),
            key=f"cf_desc_{_fi}",
            height=80,
            label_visibility="visible" if _fi == 0 else "collapsed",
        )
        if col_del.button(
            "🗑️", key=f"rm_cf_{_fi}", help="Remove row",
            disabled=len(st.session_state.comparability_factors) <= 1,
        ):
            _cf_to_remove = _fi
    if _cf_to_remove is not None:
        st.session_state.comparability_factors.pop(_cf_to_remove)
        st.rerun()

    st.divider()

    st.subheader("Search Criteria Results")
    st.caption("Enter the step-by-step search funnel from your BvD database search")

    
    if not st.session_state.search_criteria_results:
        st.session_state.search_criteria_results = [
            {"step": "1", "criteria": "All companies in scope", "result_count": ""},
            {"step": "2", "criteria": "Status: Active", "result_count": ""},
            {"step": "3", "criteria": "Geographic region", "result_count": ""},
            {"step": "4", "criteria": "Independence indicator: A+, A, A-", "result_count": ""},
            {"step": "5", "criteria": "Years with available accounts", "result_count": ""},
            {"step": "6", "criteria": "Industry classification (SIC/NACE/NAICS)", "result_count": ""},
            {"step": "7", "criteria": "Companies with overview information", "result_count": ""},
        ]
    
    for i, sc in enumerate(st.session_state.search_criteria_results):
        cols = st.columns([0.5, 3, 1])
        sc["step"] = cols[0].text_input("Step", value=sc["step"], key=f"sc_step_{i}",
                                        label_visibility="visible" if i == 0 else "collapsed")
        sc["criteria"] = cols[1].text_input("Criteria", value=sc["criteria"], key=f"sc_crit_{i}",
                                            label_visibility="visible" if i == 0 else "collapsed")
        sc["result_count"] = cols[2].text_input("Result", value=sc["result_count"], key=f"sc_res_{i}",
                                                 label_visibility="visible" if i == 0 else "collapsed")
    
    st.divider()
    st.subheader("Selected Comparable Companies (after manual selection)")
    if st.button("➕ Add Comparable Company", key="add_comparable_companies"):
        st.session_state.comparable_companies.append(
            {"name": "", "country": "", "description": "", "ros_data": ""}
        )
    _comp_to_remove = None
    for _ci, _comp in enumerate(st.session_state.comparable_companies):
        _cc1, _cc2, _cc3, _cc4, _cc5 = st.columns([2, 1.2, 2, 1.5, 0.4])
        _comp["name"] = _cc1.text_input(
            "Company Name", value=_comp.get("name", ""), key=f"comp_{_ci}_name",
            label_visibility="visible" if _ci == 0 else "collapsed",
        )
        _comp["country"] = _cc2.text_input(
            "Country", value=_comp.get("country", ""), key=f"comp_{_ci}_country",
            label_visibility="visible" if _ci == 0 else "collapsed",
        )
        _comp["description"] = _cc3.text_input(
            "Business Description", value=_comp.get("description", ""), key=f"comp_{_ci}_desc",
            label_visibility="visible" if _ci == 0 else "collapsed",
        )
        _comp["ros_data"] = _cc4.text_input(
            "ROS / Margin Data (%)", value=_comp.get("ros_data", ""), key=f"comp_{_ci}_ros",
            label_visibility="visible" if _ci == 0 else "collapsed",
        )
        if _cc5.button("🗑️", key=f"rm_comp_{_ci}") and len(st.session_state.comparable_companies) > 1:
            _comp_to_remove = _ci
    if _comp_to_remove is not None:
        st.session_state.comparable_companies.pop(_comp_to_remove)
        st.rerun()

    # ── Appendix 5: Rejection Matrix ─────────────────────────────────────────
    st.divider()
    st.subheader("Appendix 5 — Rejection Matrix")
    st.caption(
        "List all companies considered during the search. Tick the column that caused rejection. "
        "Tick **Accepted** for companies included in the final comparable set."
    )

    _RM_COLS = [
        ("limited_financial_statement",    "Limited\nFinancial\nStatement"),
        ("negative_margin",                "Negative\nMargin"),
        ("consolidated_financial_statement","Consolidated\nFinancial\nStatement"),
        ("different_main_activity",        "Different\nMain\nActivity"),
        ("non_comparable_line_of_business","Non-Comparable\nLine of\nBusiness"),
        ("limited_information_website",    "Limited\nInformation\n(Website)"),
        ("accepted",                       "Accepted"),
    ]

    if st.button("➕ Add Company to Rejection Matrix", key="add_rejection_matrix"):
        st.session_state.rejection_matrix.append(
            {"name": "", "limited_financial_statement": False, "negative_margin": False,
             "consolidated_financial_statement": False, "different_main_activity": False,
             "non_comparable_line_of_business": False, "limited_information_website": False,
             "accepted": False}
        )

    # Header row
    _rm_hdr = st.columns([2.5] + [0.7] * len(_RM_COLS) + [0.4])
    _rm_hdr[0].markdown("**Company Name**")
    for _hi, (_, _hlabel) in enumerate(_RM_COLS):
        _rm_hdr[_hi + 1].markdown(
            f"<div style='font-size:11px;text-align:center;'>{_hlabel}</div>",
            unsafe_allow_html=True,
        )

    _rm_to_remove = None
    for _ri, _rm in enumerate(st.session_state.rejection_matrix):
        _rm_cols = st.columns([2.5] + [0.7] * len(_RM_COLS) + [0.4])
        _rm["name"] = _rm_cols[0].text_input(
            "Company", value=_rm.get("name", ""),
            key=f"rm_name_{_ri}", label_visibility="collapsed",
        )
        for _ci, (_field, _label) in enumerate(_RM_COLS):
            _rm[_field] = _rm_cols[_ci + 1].checkbox(
                _label, value=_rm.get(_field, False),
                key=f"rm_{_field}_{_ri}", label_visibility="collapsed",
            )
        if _rm_cols[-1].button("🗑️", key=f"rm_row_{_ri}") and len(st.session_state.rejection_matrix) > 1:
            _rm_to_remove = _ri

    if _rm_to_remove is not None:
        st.session_state.rejection_matrix.pop(_rm_to_remove)
        st.rerun()


# ─── Step 8: TP Analysis Parameters ──────────────────────────────────────────
elif current_step == 8:
    st.header("⚙️ Transfer Pricing Analysis Parameters")
    st.info("🔵 **Manual Input** — Set analysis parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.selected_method = st.selectbox(
            "Selected TP Method *",
            TP_METHODS,
            index=TP_METHODS.index(st.session_state.selected_method),
        )
        st.session_state.selected_pli = st.selectbox(
            "Selected PLI *",
            list(PLI_OPTIONS.keys()),
            index=list(PLI_OPTIONS.keys()).index(st.session_state.selected_pli),
            format_func=lambda x: f"{x} - {PLI_OPTIONS[x]}",
        )
        st.session_state.tested_party = st.text_input(
            "Tested Party *",
            value=st.session_state.tested_party or st.session_state.company_short_name,
        )
    
    with col2:
        st.session_state.analysis_period = st.text_input(
            "Analysis Period (comparable years) *",
            value=st.session_state.analysis_period,
            placeholder="e.g., 2020-2022"
        )
        st.session_state.tested_party_ratio = st.number_input(
            f"Tested Party Weighted Average {st.session_state.selected_pli} (%)",
            value=float(st.session_state.tested_party_ratio),
            format="%.2f",
        )
    
    st.divider()
    st.subheader("Interquartile Range Results")
    col1, col2, col3 = st.columns(3)
    st.session_state.quartile_range["q1"] = col1.number_input(
        "1st Quartile (%)", value=float(st.session_state.quartile_range.get("q1", 0)), format="%.2f"
    )
    st.session_state.quartile_range["median"] = col2.number_input(
        "Median (%)", value=float(st.session_state.quartile_range.get("median", 0)), format="%.2f"
    )
    st.session_state.quartile_range["q3"] = col3.number_input(
        "3rd Quartile (%)", value=float(st.session_state.quartile_range.get("q3", 0)), format="%.2f"
    )
    
    # Visual indicator
    ratio = st.session_state.tested_party_ratio
    q1 = st.session_state.quartile_range["q1"]
    q3 = st.session_state.quartile_range["q3"]
    median = st.session_state.quartile_range["median"]
    
    if q1 > 0 and ratio > 0:
        if ratio >= q1 and ratio <= q3:
            st.success(f"✅ Tested party ratio ({ratio:.2f}%) is WITHIN the interquartile range ({q1:.2f}% – {q3:.2f}%)")
        elif ratio > q3:
            st.info(f"ℹ️ Tested party ratio ({ratio:.2f}%) is ABOVE the interquartile range ({q1:.2f}% – {q3:.2f}%). Transaction is arm's length but may require additional documentation.")
        else:
            st.warning(f"⚠️ Tested party ratio ({ratio:.2f}%) is BELOW the interquartile range ({q1:.2f}% – {q3:.2f}%). A transfer pricing adjustment may be required.")


# ─── Step 9: Non-Financial Events ────────────────────────────────────────────
elif current_step == 9:
    st.header("📝 Non-Financial Events")
    st.info("🔵 **Manual Input** — Describe any non-financial events affecting pricing")
    
    st.session_state.non_financial_events = st.text_area(
        "Non-Financial Events / Occurrences / Facts",
        value=st.session_state.non_financial_events,
        height=200,
        placeholder="Describe any significant non-financial events that affected pricing or profit levels in the fiscal year. Leave blank if none."
    )


# ─── Step 10: Run AI Agents ──────────────────────────────────────────────────
elif current_step == 10:
    st.header("🤖 AI Agent Generation")
    
    # Validation
    missing = []
    if not st.session_state.company_name:
        missing.append("Company Name")
    if not st.session_state.company_short_name:
        missing.append("Company Short Name")
    if not st.session_state.fiscal_year:
        missing.append("Fiscal Year")
    # Note: business_activities_description is now AI-generated if empty
    
    if missing:
        st.warning(f"⚠️ Please fill in the following required fields first: **{', '.join(missing)}**")
    
    # Check API keys
    provider = os.getenv("LLM_PROVIDER", "groq")
    if provider == "groq":
        has_llm = bool(os.getenv("GROQ_API_KEY"))
        llm_label = f"Groq ({os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')})"
    else:
        has_llm = bool(os.getenv("OPENAI_API_KEY"))
        llm_label = f"OpenAI ({os.getenv('OPENAI_MODEL', 'gpt-4o-mini')})"
    has_tavily = bool(os.getenv("TAVILY_API_KEY"))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("LLM Provider", f"✅ {llm_label}" if has_llm else "❌ Missing API Key")
    with col2:
        st.metric("Tavily API", "✅ Configured" if has_tavily else "❌ Missing")
    
    if not has_llm:
        st.error(f"Please enter your {provider.upper()} API key in the sidebar to use AI agents.")
    
    st.divider()
    
    st.subheader("AI-Generated Sections")
    st.markdown(f"""
    The following sections will be generated by AI agents using **{llm_label}**:

    | Section | Agent | Source |
    |---------|-------|--------|
    | **Business Activities** | 🧠 LLM | Auto-generated if field is empty |
    | **Supply Chain Management** | 🧠 LLM | LLM (from your business inputs) |
    | Global Industry Analysis | 🌐 Web Research | Tavily search + LLM |
    | Indonesian Industry Analysis | 🌐 Web Research | Tavily search + LLM |
    | Company Location & Efficiency | 🌐 Web Research | Tavily search + LLM |
    | Industry Regulations | 🌐 Web Research | Tavily search + LLM |
    | Business Environment | 🌐 Web Research | Tavily search + LLM |
    | Functional Analysis | 🧠 LLM | LLM (from your inputs) |
    | Business Characterization | 🧠 LLM | LLM (from functional analysis) |
    | Comparability Analysis | 🧠 LLM | LLM (from your inputs) |
    | Method Selection Justification | 🧠 LLM | LLM (from characterization) |
    | PLI Selection Rationale | 🧠 LLM | LLM (from method) |
    | **Comparable Company Descriptions** | 🌐 Web Research | Tavily search per company |
    | Conclusion | 🧠 LLM | LLM (from all data) |
    | P/L Overview Commentary | 📊 LLM | LLM (from financial data) |
    | Executive Summary | 🧠 LLM | LLM (from everything) |
    """)
    
    st.divider()
    
    # Labels shown in the status panel as each agent node completes
    _NODE_LABELS = {
        "business_activities":    "🧠 Business activities description generated",
        "supply_chain":           "🧠 Supply chain management overview written",
        "industry_global":        "🌐 Global industry research complete",
        "industry_indonesia":     "🌐 Indonesian industry research complete",
        "location_analysis":      "🌐 Company location & efficiency analysis complete",
        "industry_regulations":   "🌐 Industry regulations research complete",
        "business_env":           "🌐 Business environment research complete",
        "functional_analysis":    "🧠 Functional analysis generated",
        "characterization":       "🧠 Business characterization determined",
        "background_transaction": "🧠 Transaction background written",
        "comparability":          "🧠 Comparability analysis generated",
        "method_selection":       "🧠 TP method justification written",
        "pli_selection":          "🧠 PLI rationale written",
        "research_comparables":   "🌐 Comparable company descriptions researched",
        "conclusion":             "🧠 Conclusion written",
        "pl_overview":            "📊 P/L overview generated",
        "executive_summary":      "🧠 Executive summary written",
    }

    _agent_output_keys = [
        "business_activities_description",
        "industry_analysis_global", "industry_analysis_indonesia",
        "company_location_analysis", "company_location_sources",
        "industry_regulations_text", "industry_regulations_sources",
        "business_environment_overview", "business_environment_sources",
        "conclusion_text", "functional_analysis_narrative",
        "business_characterization_text", "method_selection_justification",
        "pli_selection_rationale", "comparability_analysis_narrative",
        "industry_global_sources", "industry_indonesia_sources",
        "pl_overview_text", "background_transaction",
        "supply_chain_management", "comparable_descriptions",
    ]

    if st.button("🚀 Run All AI Agents", type="primary", use_container_width=True,
                  disabled=not has_llm or bool(missing)):

        agent_state = {k: v for k, v in st.session_state.items()
                       if not k.startswith("_") and k not in ["step", "agent_ran", "agent_errors",
                                                               "groq_key_input", "openai_key_input",
                                                               "tavily_key_input", "llm_provider_select",
                                                               "groq_model_select", "openai_model_select"]}

        with st.status("Running AI agents — please wait...", expanded=True) as status:
            try:
                from agents.orchestrator import stream_agents

                result = None
                for node_name, state in stream_agents(agent_state):
                    label = _NODE_LABELS.get(node_name)
                    if label:
                        st.write(f"✅ {label}")
                    result = state

                if result is None:
                    raise RuntimeError("Agent pipeline returned no output.")

                for key in _agent_output_keys:
                    if key in result and result[key]:
                        st.session_state[key] = result[key]

                st.session_state.agent_ran = True
                st.session_state.agent_errors = result.get("errors", [])
                status.update(label="✅ All agents completed!", state="complete")

            except Exception as e:
                status.update(label=f"❌ Error: {str(e)}", state="error")
                st.error(f"Agent execution failed: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    # Show errors if any
    if st.session_state.agent_errors:
        st.warning("Some agents encountered errors:")
        for err in st.session_state.agent_errors:
            st.code(err)
    
    # Show results for review and editing
    if st.session_state.agent_ran:
        st.divider()
        st.subheader("📝 Review & Edit AI-Generated Content")
        st.caption("You can edit any AI-generated section below before exporting")
        
        sections_to_review = [
            ("supply_chain_management",          "Supply Chain Management"),
            ("industry_analysis_global",         "Global Industry Analysis"),
            ("industry_analysis_indonesia",      "Indonesian Industry Analysis"),
            ("company_location_analysis",        "Efficiency & Excellence Levels of Company Location"),
            ("industry_regulations_text",        "Regulations Affecting the Industry"),
            ("business_environment_overview",    "Business Environment"),
            ("functional_analysis_narrative",    "Functional Analysis"),
            # "business_characterization_text" filled manually in Step 4
            ("comparability_analysis_narrative", "Comparability Analysis"),
            ("method_selection_justification",   "Method Selection Justification"),
            ("pli_selection_rationale",          "PLI Selection Rationale"),
            ("conclusion_text",                  "Conclusion"),
            ("pl_overview_text",                 "Profit/Loss Overview"),
            ("executive_summary",                "Executive Summary"),
        ]

        _agent_regen_map = {
            "supply_chain_management":          "supply_chain",
            "industry_analysis_global":         "industry_global",
            "industry_analysis_indonesia":      "industry_indonesia",
            "company_location_analysis":        "location_analysis",
            "industry_regulations_text":        "industry_regulations",
            "business_environment_overview":    "business_env",
            "functional_analysis_narrative":    "functional_analysis",
            "business_characterization_text":   "characterization",
            "comparability_analysis_narrative": "comparability",
            "method_selection_justification":   "method_selection",
            "pli_selection_rationale":          "pli_selection",
            "conclusion_text":                  "conclusion",
            "executive_summary":                "executive_summary",
            "pl_overview_text":                 "pl_overview",
        }

        for key, label in sections_to_review:
            with st.expander(f"🤖 {label}", expanded=False):
                st.session_state[key] = st.text_area(
                    label,
                    value=st.session_state.get(key, ""),
                    height=300,
                    key=f"edit_{key}",
                    label_visibility="collapsed",
                )
                if st.button("🔄 Regenerate", key=f"regen_{key}"):
                    try:
                        from agents.orchestrator import run_single_agent
                        agent_state = {k: v for k, v in st.session_state.items()
                                       if not k.startswith("_")}
                        result = run_single_agent(_agent_regen_map[key], agent_state)
                        if key in result:
                            st.session_state[key] = result[key]
                            st.rerun()
                    except Exception as e:
                        st.error(f"Regeneration failed: {str(e)}")

        # ── Comparable Company Descriptions (dict) ─────────────────────────
        with st.expander("🌐 Comparable Company Descriptions (Appendix 3)", expanded=False):
            _cc_descs = st.session_state.get("comparable_descriptions", {})
            if not _cc_descs:
                st.caption("Not yet generated. Run AI Agents to populate.")
            else:
                for _cc_name, _cc_desc in _cc_descs.items():
                    st.markdown(f"**{_cc_name}**")
                    _cc_descs[_cc_name] = st.text_area(
                        _cc_name,
                        value=_cc_desc,
                        height=120,
                        key=f"edit_cc_desc_{_cc_name}",
                        label_visibility="collapsed",
                    )
                st.session_state["comparable_descriptions"] = _cc_descs
            if st.button("🔄 Regenerate All Comparable Descriptions", key="regen_comparable_descriptions"):
                try:
                    from agents.orchestrator import run_single_agent
                    agent_state = {k: v for k, v in st.session_state.items()
                                   if not k.startswith("_")}
                    result = run_single_agent("research_comparables", agent_state)
                    if "comparable_descriptions" in result:
                        st.session_state["comparable_descriptions"] = result["comparable_descriptions"]
                        st.rerun()
                except Exception as e:
                    st.error(f"Regeneration failed: {str(e)}")


# ─── Step 11: Review & Export ─────────────────────────────────────────────────
elif current_step == 11:
    st.header("✅ Review & Export Document")
    
    # Completeness check
    st.subheader("📋 Completeness Check")
    
    checks = {
        "Company Identity": bool(st.session_state.company_name and st.session_state.company_short_name),
        "Ownership Structure": bool(st.session_state.shareholders and st.session_state.shareholders[0].get("name")),
        "Management": bool(st.session_state.management and st.session_state.management[0].get("name")),
        "Affiliated Parties": bool(st.session_state.affiliated_parties and st.session_state.affiliated_parties[0].get("name")),
        "Business Activities": bool(st.session_state.business_activities_description),
        "Products": bool(st.session_state.products and st.session_state.products[0].get("name")),
        "Transaction Details": bool(st.session_state.transaction_details_text),
        "Financial Data": bool(st.session_state.financial_data.get("sales")),
        "Comparable Companies": bool(st.session_state.comparable_companies and st.session_state.comparable_companies[0].get("name")),
        "TP Analysis Parameters": bool(st.session_state.quartile_range.get("q1")),
        "AI Agents Run": st.session_state.agent_ran,
    }
    
    cols = st.columns(3)
    for i, (name, ok) in enumerate(checks.items()):
        with cols[i % 3]:
            if ok:
                st.success(f"✅ {name}")
            else:
                st.warning(f"⚠️ {name}")
    
    st.divider()
    
    # Document sections overview
    st.subheader("📑 Document Structure")
    
    section_status = {
        "Cover Page": "🟢 Template",
        "Glossary": "🟢 Template",
        "Statement Letter": "🟢 Template",
        "Ch.1 Executive Summary": "🤖 AI" if st.session_state.executive_summary else "⏳ Pending",
        "Ch.2 TP Regulations": "🟢 Template",
        "Ch.3 Company Identity": "🔵 Manual" if st.session_state.company_name else "⏳ Pending",
        "Ch.3 Business Environment": "🤖 AI" if st.session_state.business_environment_overview else "⏳ Pending",
        "Ch.4 Transactions": "🔵 Manual" if st.session_state.transaction_details_text else "⏳ Pending",
        "Ch.4 Functional Analysis": "🤖 AI" if st.session_state.functional_analysis_narrative else "⏳ Pending",
        "Ch.5 Industry Analysis": "🤖 AI" if st.session_state.industry_analysis_global else "⏳ Pending",
        "Ch.5 Method Selection": "🤖 AI" if st.session_state.method_selection_justification else "⏳ Pending",
        "Ch.5 Conclusion": "🤖 AI" if st.session_state.conclusion_text else "⏳ Pending",
        "Ch.6 Financial Info": "🔵 Manual" if st.session_state.financial_data.get("sales") else "⏳ Pending",
        "Ch.7 Non-Financial Events": "🔵 Manual",
        "References": "🟢 Template",
        "Appendices": "🔵 Manual",
    }
    
    for section, status in section_status.items():
        st.text(f"  {status}  {section}")
    
    st.divider()
    
    # Export
    st.subheader("📥 Export Document")

    export_col1, export_col2 = st.columns(2)

    # ── Button 1: existing python-docx builder ─────────────────────────────────
    with export_col1:
        st.caption("Recommended — builds full document from scratch")
        if st.button("📄 Export Full Document (.docx)", type="primary", use_container_width=True):
            with st.spinner("Generating document..."):
                try:
                    from export.docx_export import generate_tp_document

                    state = {k: v for k, v in st.session_state.items()
                             if not k.startswith("_") and k not in [
                                 "step", "agent_ran", "agent_errors",
                                 "groq_key_input", "openai_key_input",
                                 "tavily_key_input", "llm_provider_select",
                                 "groq_model_select", "openai_model_select"]}

                    _safe_co = st.session_state.company_short_name.replace(" ", "_")
                    output_filename = f"TP_{_safe_co}_FY{st.session_state.fiscal_year}.docx"
                    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
                        output_path = tmp.name

                    st.write("📄 Building document structure...")
                    generate_tp_document(state, output_path)

                    st.write("🔄 Updating TOC page numbers via Word...")
                    from export.docx_export import update_toc_with_word
                    toc_ok, toc_err = update_toc_with_word(output_path)
                    if not toc_ok:
                        st.warning(
                            f"⚠️ Could not auto-update TOC ({toc_err}). "
                            "Open in Word and press **Ctrl+A → F9**."
                        )

                    with open(output_path, "rb") as f:
                        doc_bytes = f.read()
                    try:
                        os.unlink(output_path)
                    except Exception:
                        pass

                    st.success("✅ Document generated successfully!")
                    st.download_button(
                        label="⬇️ Download DOCX",
                        data=doc_bytes,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Export failed: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

    # ── Button 2: Jinja2 template renderer (docxtpl) ───────────────────────────
    with export_col2:
        st.caption("Uses the master Word template with placeholders")
        if st.button("📋 Export from Master Template (.docx)", use_container_width=True):
            with st.spinner("Rendering Jinja2 template..."):
                try:
                    from export.docx_template_export import render_tp_document

                    state = {k: v for k, v in st.session_state.items()
                             if not k.startswith("_") and k not in [
                                 "step", "agent_ran", "agent_errors",
                                 "groq_key_input", "openai_key_input",
                                 "tavily_key_input", "llm_provider_select",
                                 "groq_model_select", "openai_model_select"]}

                    _safe_co = st.session_state.company_short_name.replace(" ", "_")
                    output_filename = f"TP_{_safe_co}_FY{st.session_state.fiscal_year}_template.docx"
                    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
                        output_path = tmp.name

                    render_tp_document(state, output_path)

                    with open(output_path, "rb") as f:
                        doc_bytes = f.read()
                    try:
                        os.unlink(output_path)
                    except Exception:
                        pass

                    st.success("✅ Template rendered successfully!")
                    st.info(
                        "ℹ️ Open in Word and press **Ctrl+A → F9** "
                        "to refresh the Table of Contents page numbers."
                    )
                    st.download_button(
                        label="⬇️ Download Template DOCX",
                        data=doc_bytes,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"Template render failed: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
    st.divider()
    
    # Save/Load state
    st.subheader("💾 Save / Load Project")
    col1, col2 = st.columns(2)
    
    with col1:
        _s11_save = {k: v for k, v in st.session_state.items()
                     if not k.startswith("_") and k not in ["groq_key_input", "openai_key_input",
                                                             "tavily_key_input", "llm_provider_select",
                                                             "groq_model_select", "openai_model_select"]}
        st.download_button(
            "💾 Save Project JSON",
            data=json.dumps(_s11_save, indent=2, default=str),
            file_name=f"tp_project_{st.session_state.company_short_name}_FY{st.session_state.fiscal_year}.json",
            mime="application/json",
            use_container_width=True,
        )
    
    with col2:
        uploaded = st.file_uploader("📂 Load Project JSON", type="json")
        if uploaded:
            try:
                data = json.loads(uploaded.read())
                for k, v in data.items():
                    st.session_state[k] = v
                st.success("✅ Project loaded!")
                st.rerun()
            except Exception as e:
                st.error(f"Load failed: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════════
# NAVIGATION BUTTONS
# ═══════════════════════════════════════════════════════════════════════════════
st.divider()
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    if current_step > 0:
        if st.button("⬅️ Previous", use_container_width=True):
            st.session_state.step -= 1
            st.rerun()

with col3:
    if current_step < len(STEPS) - 1:
        if st.button("Next ➡️", use_container_width=True, type="primary"):
            # Required field validation per step
            _step_errors = []
            if current_step == 1:  # Company Identity
                if not st.session_state.company_name.strip():
                    _step_errors.append("Full Company Name is required")
                if not st.session_state.company_short_name.strip():
                    _step_errors.append("Short Name / Abbreviation is required")
                if not st.session_state.fiscal_year.strip():
                    _step_errors.append("Fiscal Year is required")
            elif current_step == 5:  # Transactions
                if not st.session_state.transaction_details_text.strip():
                    _step_errors.append("Transaction Details are required")
            if _step_errors:
                for _err in _step_errors:
                    st.error(f"⚠️ {_err}")
            else:
                st.session_state.step += 1
                st.rerun()
