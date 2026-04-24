"""
Summary Subagent - conclusion, P/L overview, transaction synthesis, and executive summary nodes.

Nodes:
  - generate_conclusion -> conclusion_text
  - generate_pl_overview -> pl_overview_text
  - generate_transaction_findings_summary -> transaction_summary_packets
  - generate_executive_summary -> executive_summary
"""
from __future__ import annotations

import json
import re

from agents.llm_factory import invoke_prompt


def generate_conclusion(state: dict) -> dict:
    """Generate the conclusion section."""
    company_short = state.get("company_short_name", "")
    selected_method = state.get("selected_method", "TNMM")
    selected_pli = state.get("selected_pli", "ROS")
    transaction_type = state.get("transaction_type", "")
    quartile = state.get("quartile_range", {})
    tested_ratio = state.get("tested_party_ratio", 0)
    comparable_count = len(state.get("comparable_companies", []))
    analysis_period = state.get("analysis_period", "")
    fiscal_year = state.get("fiscal_year", "")

    q1 = quartile.get("q1", 0)
    median = quartile.get("median", 0)
    q3 = quartile.get("q3", 0)

    prompt = f"""Write the Conclusion section for a Transfer Pricing Local File.

Details:
- Company: {company_short}
- Fiscal Year: {fiscal_year}
- Transaction type: {transaction_type}
- TP Method: {selected_method}
- PLI: {selected_pli}
- Number of comparables: {comparable_count}
- Analysis period: {analysis_period}
- Interquartile range: Q1={q1}%, Median={median}%, Q3={q3}%
- {company_short}'s weighted average {selected_pli}: {tested_ratio}%

Write 3-4 paragraphs summarizing:
1. The method used and why
2. The comparable companies used and search process
3. The interquartile range results
4. The final conclusion on whether the transaction is at arm's length

Use EXACT numbers provided. Do NOT invent any figures.
RESPOND IN ENGLISH ONLY. Do NOT switch to Indonesian or any other language.
Professional formal English, suitable for regulatory documentation.
"""
    return {"conclusion_text": invoke_prompt(prompt)}


def generate_pl_overview(state: dict) -> dict:
    """Generate bullet-point commentary on the P/L table data using the LLM."""
    company_short = state.get("company_short_name", "the Company")
    fiscal_year = state.get("fiscal_year", "2024")
    fd = state.get("financial_data", {})
    fd_prior = state.get("financial_data_prior", {})

    if not fd:
        return {"pl_overview_text": ""}

    fiscal_year_clean = fiscal_year.strip()
    prior_year = str(int(fiscal_year_clean) - 1) if fiscal_year_clean.isdigit() else "Prior Year"

    pl_items = [
        ("Sales / Revenue",               "sales"),
        ("Cost of Goods Sold",            "cogs"),
        ("Gross Profit",                  "gross_profit"),
        ("Gross Profit Margin (%)",       "gross_margin_pct"),
        ("Operating Expenses",            "operating_expenses"),
        ("Operating Profit",              "operating_profit"),
        ("Financial Income / (Expenses)", "financial_income"),
        ("Other Income",                  "other_income"),
        ("Other Expense",                 "other_expense"),
        ("Income Before Tax",             "income_before_tax"),
        ("Income Tax",                    "income_tax"),
        ("Net Income",                    "net_income"),
    ]

    table_lines = [f"{'Account':<35} {'FY ' + fiscal_year:<25} {'FY ' + prior_year:<25}"]
    table_lines.append("-" * 85)
    for label, key in pl_items:
        cur = fd.get(key, "")
        pri = fd_prior.get(key, "")
        if cur or pri:
            table_lines.append(f"{label:<35} {str(cur):<25} {str(pri):<25}")

    table_text = "\n".join(table_lines)

    prompt = f"""You are a transfer pricing analyst writing the "Overview of Profit/Loss" section for {company_short}'s Transfer Pricing Local File.

Below is the company's Profit/Loss data for FY {fiscal_year} and FY {prior_year}:

{table_text}

Based on this data, write a brief overview as BULLET POINTS (use "- " prefix for each bullet). Each bullet should:
- Describe a key observation about a specific P/L line item
- Include the actual figures and percentage change where meaningful
- Use natural, varied language (don't always say "increased by X%")
- Note any significant trends, margin changes, or notable movements

Guidelines:
- Write 4-7 bullet points covering the most important line items
- Focus on items that show significant changes or are strategically important
- If an item has no change or no data, skip it
- Use formal professional English suitable for a regulatory document
- RESPOND IN ENGLISH ONLY
- Use EXACT figures from the table - do NOT invent any numbers
- Start the section with a brief introductory sentence like:
  "The overview of {company_short}'s profit/loss statements for FY {fiscal_year} and FY {prior_year} is as follows:"
  Then list the bullet points.
"""
    text = invoke_prompt(prompt).strip()
    return {"pl_overview_text": text}


def _extract_json_payload(text: str):
    """Extract JSON payload from a model response that may include markdown fences."""
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start_positions = [idx for idx in (cleaned.find("["), cleaned.find("{")) if idx != -1]
    if not start_positions:
        raise ValueError("No JSON payload found in model response.")
    start = min(start_positions)

    for end_char in ("]", "}"):
        end = cleaned.rfind(end_char)
        if end > start:
            snippet = cleaned[start:end + 1]
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                continue

    raise ValueError("Could not parse JSON payload from model response.")


def _fallback_transaction_summary_packet(state: dict) -> list[dict]:
    """Build a deterministic fallback packet if the model fails to emit valid JSON."""
    transaction_type = state.get("transaction_type", "Affiliated Transaction") or "Affiliated Transaction"
    company_short = state.get("company_short_name", "the Company") or "the Company"
    comparable_count = len([c for c in state.get("comparable_companies", []) if c.get("name")])
    selected_method = state.get("selected_method", "TNMM")
    selected_pli = state.get("selected_pli", "ROS")
    quartile = state.get("quartile_range", {})
    tested_ratio = state.get("tested_party_ratio", 0)
    q1 = quartile.get("q1", 0)
    median = quartile.get("median", 0)
    q3 = quartile.get("q3", 0)

    if tested_ratio < q1:
        holding = "below range"
        tax_implication = "A transfer pricing adjustment may be required."
    elif tested_ratio > q3:
        holding = "above range"
        tax_implication = "No transfer pricing issue was indicated for Indonesian taxation."
    else:
        holding = "arm's length"
        tax_implication = "The transaction appears to satisfy the arm's length principle."

    return [{
        "section_title": transaction_type.replace(" of ", " ").title(),
        "tested_transaction": f"{transaction_type.lower()} undertaken by {company_short}",
        "selected_method": selected_method,
        "selected_pli": selected_pli,
        "method_reason": (state.get("method_selection_justification", "") or "").strip()[:500],
        "comparable_search_basis": (
            f"{comparable_count} comparable companies were identified using the documented search criteria."
            if comparable_count else
            "Comparable search details were documented in the analysis."
        ),
        "comparable_count": comparable_count,
        "range_result": (
            f"Q1 {q1:.2f}%, median {median:.2f}%, Q3 {q3:.2f}%, tested party {tested_ratio:.2f}%."
        ),
        "holding": holding,
        "tax_implication": tax_implication,
    }]


def generate_transaction_findings_summary(state: dict) -> dict:
    """Generate structured transaction summary packets for executive summary drafting."""
    company_short = state.get("company_short_name", "the Company")
    transaction_type = state.get("transaction_type", "")
    selected_method = state.get("selected_method", "TNMM")
    selected_pli = state.get("selected_pli", "ROS")
    quartile = state.get("quartile_range", {})
    tested_ratio = state.get("tested_party_ratio", 0)
    comparable_count = len([c for c in state.get("comparable_companies", []) if c.get("name")])

    prompt = f"""You are preparing structured executive-summary synthesis for a Transfer Pricing Local File.

Return JSON ONLY. Do not add markdown fences. Do not add explanation.

Create a JSON array with one object summarizing the tested affiliated transaction using the exact schema below:
[
  {{
    "section_title": "Purchase Transaction",
    "tested_transaction": "purchase of heavy equipment from affiliated parties",
    "selected_method": "TNMM",
    "selected_pli": "ROS",
    "method_reason": "why the method is appropriate",
    "comparable_search_basis": "how comparable companies were identified",
    "comparable_count": 6,
    "range_result": "Q1/Q3/median/tested-party result in one sentence",
    "holding": "arm's length / above range / below range",
    "tax_implication": "no TP issue / adjustment may be required"
  }}
]

Facts:
- Company: {company_short}
- Transaction type: {transaction_type}
- Selected method: {selected_method}
- Selected PLI: {selected_pli}
- Comparable count: {comparable_count}
- Quartile range: Q1={quartile.get("q1", 0)}%, Median={quartile.get("median", 0)}%, Q3={quartile.get("q3", 0)}%
- Tested party ratio: {tested_ratio}%

Source material:
- Background transaction: {state.get("background_transaction", "")[:1800]}
- Business characterization: {state.get("business_characterization_text", "")[:1200]}
- Comparability analysis: {state.get("comparability_analysis_narrative", "")[:1800]}
- Method selection justification: {state.get("method_selection_justification", "")[:1800]}
- PLI selection rationale: {state.get("pli_selection_rationale", "")[:1200]}
- Conclusion text: {state.get("conclusion_text", "")[:1800]}

Rules:
- Preserve the transaction type and quantitative result exactly.
- Keep each field concise and decision-oriented.
- "section_title" must be suitable as a subsection heading inside an executive summary.
- "holding" must be one of: "arm's length", "above range", "below range".
- JSON only.
"""
    raw = invoke_prompt(prompt).strip()
    try:
        parsed = _extract_json_payload(raw)
        packets = parsed if isinstance(parsed, list) else [parsed]
        packets = [pkt for pkt in packets if isinstance(pkt, dict)]
        if not packets:
            raise ValueError("No valid packet objects returned.")
        return {"transaction_summary_packets": packets}
    except Exception:
        return {"transaction_summary_packets": _fallback_transaction_summary_packet(state)}


def generate_executive_summary(state: dict) -> dict:
    """Generate the executive summary from transaction summary packets."""
    company_name = state.get("company_name", "")
    company_short = state.get("company_short_name", "")
    fiscal_year = state.get("fiscal_year", "")
    company_address = state.get("company_address", "")
    parent_group = state.get("parent_group", "")
    products = state.get("products", [])
    product_names = ", ".join([p.get("name", "") for p in products]) if products else ""
    business_char = state.get("business_characterization_text", "")
    analysis_period = state.get("analysis_period", "")
    packets = state.get("transaction_summary_packets") or _fallback_transaction_summary_packet(state)
    packets_json = json.dumps(packets, indent=2)

    prompt = f"""Write the Executive Summary for a Transfer Pricing Local File document.

Details:
- Company: {company_name} ("{company_short}")
- Fiscal Year: {fiscal_year}
- Address: {company_address}
- Parent group: {parent_group}
- Products: {product_names}
- Business characterization (from functional analysis): {business_char[:300]}
- Analysis period: {analysis_period}
- Transaction summary packets:
{packets_json}

Write THREE sections:

1. PURPOSE OF REPORT (1 paragraph):
   State this is a Local File prepared as compliance with PMK-172 Year 2023.

2. SUMMARY OF CONCLUSION:
   - Begin with 1 short paragraph on company background and the scope of the tested transaction.
   - Then, for each transaction summary packet, write a clearly labeled subsection using the packet's "section_title".
   - Under each subsection, write a compact but decision-oriented narrative that reads like a holding memo:
     transaction tested, selected method and why, comparable search basis, benchmark result, and tax implication.
   - This part should feel like a synthesis of the whole TP analysis, not a generic recap.

3. SCOPE OF REPORT (1 paragraph + bullet list):
   - Sources used (meetings, financial data, regulations, OECD TPG, third-party databases)

RULES:
- RESPOND IN ENGLISH ONLY. Do NOT switch to Indonesian or any other language.
- Use packet contents and exact numbers provided. Do NOT change any figures.
- Professional formal English.
- Clearly label each section.
- Do not collapse the transaction findings into one generic paragraph.
"""
    return {"executive_summary": invoke_prompt(prompt)}
