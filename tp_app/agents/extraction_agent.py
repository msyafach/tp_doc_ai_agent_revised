"""
extraction_agent.py
===================
Dispatches to the correct extraction strategy based on RetrievalContext.strategy:

  "page_index"  → PageIndex tree traversal via LLM reasoning
  "vector_rag"  → LangChain RetrievalQA over FAISS vectorstore

Both paths return the same structured dict of form fields.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Optional

from langchain.prompts import PromptTemplate

# ── Make the cloned PageIndex importable ──────────────────────────────────────
_PI_ROOT = Path(__file__).resolve().parent.parent / "PageIndex"
if str(_PI_ROOT) not in sys.path:
    sys.path.insert(0, str(_PI_ROOT))


# ══════════════════════════════════════════════════════════════════════════════
# Shared JSON extraction prompt
# ══════════════════════════════════════════════════════════════════════════════

EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are an expert analyst extracting structured data from corporate documents \
for a Transfer Pricing Local File. Use ONLY the information found in the provided context.

Context from the company's documents:
{context}

Task:
{question}

STRICT RULES:
- Return ONLY valid JSON. No markdown fences, no explanation text.
- If information is not found in the context, use null for strings, [] for arrays, {{}} for objects.
- Do not invent or guess data — only extract what is explicitly mentioned.
- For monetary values, preserve the original currency and number (e.g., "IDR 10,000,000,000").
- For lists (shareholders, management, etc.), return an array of objects matching the schema.

JSON output:""",
)


# ══════════════════════════════════════════════════════════════════════════════
# Extraction queries (shared between both tiers)
# ══════════════════════════════════════════════════════════════════════════════

EXTRACTION_QUERIES = {
    "company_identity": """
Extract company identity information. Return JSON:
{
  "company_name": "<full legal name>",
  "company_short_name": "<abbreviation or trade name>",
  "company_address": "<registered address>",
  "establishment_info": "<deed number, date, notary, ministry approval>",
  "fiscal_year": "<fiscal year, e.g. 2024>",
  "parent_company": "<direct parent company name>",
  "parent_group": "<ultimate parent group name>"
}""",

    "shareholders": """
Extract all shareholders/owners. Return JSON array:
[{"name": "<name>", "shares": "<number of shares>", "capital": "<capital amount with currency>", "percentage": "<ownership %>"}]
Include all shareholders found in the document.""",

    "management": """
Extract all management and board members. Return JSON array:
[{"position": "<title>", "name": "<full name>"}]
Include commissioners, directors, and key management.""",

    "employee_count": """
Extract the total number of employees. Return JSON:
{"employee_count": "<number or description, e.g. '150 permanent employees'>"}""",

    "affiliated_parties": """
Extract all affiliated/related parties. Return JSON array:
[{"name": "<company name>", "country": "<country>", "relationship": "<relationship type>", "transaction_type": "<type of transaction>"}]""",

    "business_activities": """
Extract business activities. Return JSON:
{
  "business_activities_description": "<full description of business activities>",
  "business_strategy": "<business strategy description>",
  "business_restructuring": "<any business restructuring events>"
}""",

    "products": """
Extract products or services offered. Return JSON array:
[{"name": "<product/service name>", "description": "<brief description>"}]""",

    "transaction_details": """
Extract intercompany transaction details. Return JSON:
{
  "transaction_details_text": "<description of the affiliated transactions>",
  "pricing_policy": "<transfer pricing policy or arm's length justification>"
}""",

    "financial_data": """
Extract current-year Profit & Loss financial data. Return JSON:
{
  "sales": "<revenue amount>",
  "cogs": "<cost of goods sold>",
  "gross_profit": "<gross profit>",
  "selling_expenses": "<selling expenses>",
  "ga_expenses": "<general & administrative expenses>",
  "opex": "<total operating expenses>",
  "operating_profit": "<operating profit/EBIT>",
  "interest_income": "<interest income>",
  "interest_expense": "<interest expense>",
  "other_income": "<other income>",
  "ebt": "<earnings before tax>",
  "net_profit": "<net profit after tax>"
}""",

    "financial_data_prior": """
Extract PRIOR-YEAR Profit & Loss financial data (the year before the current fiscal year). Return JSON:
{
  "sales": "<revenue amount>",
  "cogs": "<cost of goods sold>",
  "gross_profit": "<gross profit>",
  "selling_expenses": "<selling expenses>",
  "ga_expenses": "<general & administrative expenses>",
  "opex": "<total operating expenses>",
  "operating_profit": "<operating profit/EBIT>",
  "interest_income": "<interest income>",
  "interest_expense": "<interest expense>",
  "other_income": "<other income>",
  "ebt": "<earnings before tax>",
  "net_profit": "<net profit after tax>"
}""",
}


# ══════════════════════════════════════════════════════════════════════════════
# Utility
# ══════════════════════════════════════════════════════════════════════════════

def _parse_json(raw: str) -> Any:
    """Strip markdown fences and parse JSON. Returns None on failure."""
    if not raw:
        return None
    raw = re.sub(r"```(?:json)?", "", raw, flags=re.IGNORECASE).strip().rstrip("`").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract the first {...} or [...]
        m = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", raw)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
    return None


# ══════════════════════════════════════════════════════════════════════════════
# Tier 1: PageIndex extraction
# ══════════════════════════════════════════════════════════════════════════════

def _collect_node_texts(node, parts: list[str], max_nodes: int = 20) -> None:
    """DFS over the PageIndex tree collecting leaf node 'text' values."""
    if not isinstance(node, dict) or len(parts) >= max_nodes:
        return
    if node.get("text"):
        parts.append(node["text"])
    for child in node.get("nodes", []):
        _collect_node_texts(child, parts, max_nodes)


def _query_page_index(tree: dict, question: str, llm, k_nodes: int = 6) -> Any:
    """
    Strategy:
      1. Flatten tree into a concise summary (title + summary per node).
      2. Ask LLM which nodes are relevant.
      3. Retrieve the 'text' of those nodes and run extraction.
    """
    from pageindex.utils import structure_to_list

    structure = tree.get("structure", tree)
    if isinstance(structure, list):
        all_nodes = []
        for item in structure:
            all_nodes.extend(structure_to_list(item))
    else:
        all_nodes = structure_to_list(structure)

    # Build a lightweight index of nodes
    index_lines = []
    for i, n in enumerate(all_nodes):
        summary = n.get("summary") or n.get("title", "")
        index_lines.append(f"[{i}] {n.get('title','?')} — {summary[:120]}")

    index_text = "\n".join(index_lines)

    # Ask LLM which node indices are most relevant
    selection_prompt = (
        f"You are given a document index. Select up to {k_nodes} most relevant node numbers "
        f"(0-indexed) for answering this question:\n\n"
        f"Question: {question}\n\n"
        f"Document index:\n{index_text}\n\n"
        f"Return ONLY a JSON array of integers, e.g. [0, 3, 7]. No other text."
    )
    raw_selection = llm.invoke(selection_prompt).content
    selected_indices = _parse_json(raw_selection) or []
    if not isinstance(selected_indices, list):
        selected_indices = list(range(min(k_nodes, len(all_nodes))))

    # Collect text from selected nodes
    context_parts = []
    for idx in selected_indices:
        if isinstance(idx, int) and 0 <= idx < len(all_nodes):
            text = all_nodes[idx].get("text", "")
            if text:
                context_parts.append(text)

    if not context_parts:
        # Fallback: use top nodes
        for n in all_nodes[:k_nodes]:
            t = n.get("text", "")
            if t:
                context_parts.append(t)

    context = "\n\n".join(context_parts[:k_nodes])

    prompt_text = EXTRACTION_PROMPT.format(context=context, question=question)
    response = llm.invoke(prompt_text).content
    return _parse_json(response)


# ══════════════════════════════════════════════════════════════════════════════
# Tier 2: Vector RAG extraction
# ══════════════════════════════════════════════════════════════════════════════

def _query_vector_rag(vectorstore, question: str, llm, k: int = 8) -> Any:
    from langchain.chains import RetrievalQA

    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": EXTRACTION_PROMPT},
        return_source_documents=False,
    )
    response = chain.invoke({"query": question})
    raw = response.get("result", "") if isinstance(response, dict) else str(response)
    return _parse_json(raw)


# ══════════════════════════════════════════════════════════════════════════════
# Main public API
# ══════════════════════════════════════════════════════════════════════════════

def extract_form_fields(context, llm) -> dict:
    """
    Run extraction for all form field groups.

    `context` must be a RetrievalContext from document_processor.process_uploaded_files().
    `llm`     must be a LangChain chat model (ChatGroq / ChatOpenAI).

    Returns a flat dict mapping session-state keys → extracted values.
    """
    strategy = context.strategy

    def _query(question: str) -> Any:
        if strategy == "page_index":
            return _query_page_index(context.page_index_tree, question, llm)
        else:
            return _query_vector_rag(context.vectorstore, question, llm)

    result: dict = {}

    # ── Company identity ───────────────────────────────────────────────────────
    r = _query(EXTRACTION_QUERIES["company_identity"])
    if isinstance(r, dict):
        result.update({
            k: r.get(k) for k in
            ["company_name", "company_short_name", "company_address",
             "establishment_info", "fiscal_year", "parent_company", "parent_group"]
        })

    # ── Shareholders ───────────────────────────────────────────────────────────
    r = _query(EXTRACTION_QUERIES["shareholders"])
    if isinstance(r, list):
        result["shareholders"] = r

    # ── Management ────────────────────────────────────────────────────────────
    r = _query(EXTRACTION_QUERIES["management"])
    if isinstance(r, list):
        result["management"] = r

    # ── Employee count ────────────────────────────────────────────────────────
    r = _query(EXTRACTION_QUERIES["employee_count"])
    if isinstance(r, dict):
        result["employee_count"] = r.get("employee_count")

    # ── Affiliated parties ────────────────────────────────────────────────────
    r = _query(EXTRACTION_QUERIES["affiliated_parties"])
    if isinstance(r, list):
        result["affiliated_parties"] = r

    # ── Business activities ───────────────────────────────────────────────────
    r = _query(EXTRACTION_QUERIES["business_activities"])
    if isinstance(r, dict):
        result.update({
            k: r.get(k) for k in
            ["business_activities_description", "business_strategy", "business_restructuring"]
        })

    # ── Products ──────────────────────────────────────────────────────────────
    r = _query(EXTRACTION_QUERIES["products"])
    if isinstance(r, list):
        result["products"] = r

    # ── Transaction details ───────────────────────────────────────────────────
    r = _query(EXTRACTION_QUERIES["transaction_details"])
    if isinstance(r, dict):
        result.update({
            k: r.get(k) for k in ["transaction_details_text", "pricing_policy"]
        })

    # ── Financial data (current year) ─────────────────────────────────────────
    r = _query(EXTRACTION_QUERIES["financial_data"])
    if isinstance(r, dict):
        result["financial_data"] = r

    # ── Financial data (prior year) ───────────────────────────────────────────
    r = _query(EXTRACTION_QUERIES["financial_data_prior"])
    if isinstance(r, dict):
        result["financial_data_prior"] = r

    return result


def get_extraction_summary(extraction: dict) -> dict:
    """Returns a human-readable summary of what was found vs. not found."""

    def _status(val) -> str:
        if val is None or val == "" or val == [] or val == {}:
            return "❌ Not found"
        if isinstance(val, list):
            return f"✅ {len(val)} item(s)"
        return f"✅ Found"

    return {
        "Company Name":            _status(extraction.get("company_name")),
        "Company Address":         _status(extraction.get("company_address")),
        "Fiscal Year":             _status(extraction.get("fiscal_year")),
        "Parent Company":          _status(extraction.get("parent_company")),
        "Shareholders":            _status(extraction.get("shareholders")),
        "Management":              _status(extraction.get("management")),
        "Employee Count":          _status(extraction.get("employee_count")),
        "Affiliated Parties":      _status(extraction.get("affiliated_parties")),
        "Business Activities":     _status(extraction.get("business_activities_description")),
        "Products / Services":     _status(extraction.get("products")),
        "Transaction Details":     _status(extraction.get("transaction_details_text")),
        "Financial Data (current)":_status(extraction.get("financial_data")),
        "Financial Data (prior)":  _status(extraction.get("financial_data_prior")),
    }
