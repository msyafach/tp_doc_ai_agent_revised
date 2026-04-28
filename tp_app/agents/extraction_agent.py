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
from pathlib import Path
from typing import Any, Optional

from langchain.prompts import PromptTemplate


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

_MAX_CONTEXT_TOKENS = 16_000   # safe ceiling for Groq / OpenAI LLMs


def _select_nodes(nodes: list[dict], question: str, llm, k: int) -> list[int]:
    """Ask LLM to pick up to k relevant node indices from the current level."""
    index_lines = [
        f"[{i}] {n.get('title', '?')} — {(n.get('summary') or n.get('title', ''))[:120]}"
        for i, n in enumerate(nodes)
    ]
    prompt = (
        f"Select up to {k} most relevant section numbers for this question:\n"
        f"Question: {question}\n\n"
        f"Sections:\n" + "\n".join(index_lines) + "\n\n"
        f"Return ONLY a JSON array of integers, e.g. [0, 2, 5]."
    )
    indices = _parse_json(llm.invoke(prompt).content)
    if not isinstance(indices, list):
        return list(range(min(k, len(nodes))))
    return [i for i in indices if isinstance(i, int) and 0 <= i < len(nodes)]


def _traverse(nodes: list[dict], question: str, llm, k: int, depth: int = 0) -> list[dict]:
    """
    Hierarchical traversal: at each level ask LLM which nodes are relevant,
    then recurse into their children. Stops at depth 2 or when nodes are leaves.
    """
    if not nodes:
        return []

    selected = [nodes[i] for i in _select_nodes(nodes, question, llm, k)]

    if depth >= 2:
        return selected

    result: list[dict] = []
    for node in selected:
        children = node.get("nodes", [])
        if children:
            result.extend(_traverse(children, question, llm, k, depth + 1))
        else:
            result.append(node)
    return result[:k]


def _trim_context(parts: list[str], max_tokens: int = _MAX_CONTEXT_TOKENS) -> str:
    """Join context parts, truncating to stay within token budget."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        out: list[str] = []
        total = 0
        for part in parts:
            encoded = enc.encode(part)
            if total + len(encoded) > max_tokens:
                remaining = max_tokens - total
                if remaining > 100:
                    out.append(enc.decode(encoded[:remaining]) + "\n[truncated]")
                break
            out.append(part)
            total += len(encoded)
        return "\n\n".join(out)
    except Exception:
        return "\n\n".join(parts)[: max_tokens * 4]


def _query_page_index(tree: dict, question: str, llm, k_nodes: int = 6) -> Any:
    """
    True hierarchical PageIndex retrieval:
    1. Select top-level branches relevant to the question.
    2. Recurse into children of selected branches (max 2 levels).
    3. Collect leaf text, trim to token budget, then run extraction.
    """
    structure = tree.get("structure", tree)
    if not isinstance(structure, list):
        structure = [structure]

    leaf_nodes = _traverse(structure, question, llm, k=k_nodes)
    context_parts = [n.get("text", "") for n in leaf_nodes if n.get("text")]

    # Fallback: flat scan of the top nodes if traversal yielded nothing
    if not context_parts:
        from pageindex.utils import structure_to_list
        all_nodes: list[dict] = []
        for item in structure:
            all_nodes.extend(structure_to_list(item))
        context_parts = [n.get("text", "") for n in all_nodes[:k_nodes] if n.get("text")]

    context = _trim_context(context_parts)
    return _parse_json(llm.invoke(EXTRACTION_PROMPT.format(context=context, question=question)).content)


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
