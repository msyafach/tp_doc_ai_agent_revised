"""
Summary Subagent — conclusion, P/L overview, and executive summary nodes.

Nodes:
  - generate_conclusion       → conclusion_text
  - generate_pl_overview      → pl_overview_text
  - generate_executive_summary → executive_summary
"""
from agents.llm_factory import invoke_prompt


# ─── Node: Conclusion ────────────────────────────────────────────────────────

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


# ─── Node: Profit/Loss Overview ───────────────────────────────────────────────

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
- Use EXACT figures from the table — do NOT invent any numbers
- Start the section with a brief introductory sentence like:
  "The overview of {company_short}'s profit/loss statements for FY {fiscal_year} and FY {prior_year} is as follows:"
  Then list the bullet points.
"""
    text = invoke_prompt(prompt).strip()
    return {"pl_overview_text": text}


# ─── Node: Executive Summary ─────────────────────────────────────────────────

def generate_executive_summary(state: dict) -> dict:
    """Generate the executive summary based on all completed analysis."""
    company_name = state.get("company_name", "")
    company_short = state.get("company_short_name", "")
    fiscal_year = state.get("fiscal_year", "")
    company_address = state.get("company_address", "")
    parent_group = state.get("parent_group", "")
    products = state.get("products", [])
    product_names = ", ".join([p.get("name", "") for p in products]) if products else ""
    business_char = state.get("business_characterization_text", "")
    selected_method = state.get("selected_method", "TNMM")
    selected_pli = state.get("selected_pli", "ROS")
    transaction_type = state.get("transaction_type", "")
    quartile = state.get("quartile_range", {})
    tested_ratio = state.get("tested_party_ratio", 0)
    comparable_count = len(state.get("comparable_companies", []))
    analysis_period = state.get("analysis_period", "")

    q1 = quartile.get("q1", 0)
    median = quartile.get("median", 0)
    q3 = quartile.get("q3", 0)

    if tested_ratio >= q1:
        if tested_ratio >= q3:
            conclusion = (
                "above the interquartile range of comparable companies. Thus, it can be concluded "
                "that the affiliated transaction performed better than the comparable companies and "
                "there were no transfer pricing issues for taxation in Indonesia"
            )
        else:
            conclusion = (
                "within the interquartile range of comparable companies. Thus, it can be concluded "
                "that the affiliated transaction is at arm's length and there were no transfer pricing "
                "issues for taxation in Indonesia"
            )
    else:
        conclusion = (
            "below the interquartile range of comparable companies. This indicates a potential "
            "transfer pricing adjustment may be required"
        )

    prompt = f"""Write the Executive Summary for a Transfer Pricing Local File document.

Details:
- Company: {company_name} ("{company_short}")
- Fiscal Year: {fiscal_year}
- Address: {company_address}
- Parent group: {parent_group}
- Products: {product_names}
- Business characterization (from functional analysis): {business_char[:300]}
- Transaction type analyzed: {transaction_type}
- TP Method: {selected_method}
- PLI: {selected_pli}
- Number of comparable companies: {comparable_count}
- Analysis period: {analysis_period}
- Interquartile range: Q1 = {q1}%, Median = {median}%, Q3 = {q3}%
- Tested party's weighted average {selected_pli}: {tested_ratio}%
- Conclusion: {conclusion}

Write THREE sections:

1. PURPOSE OF REPORT (1 paragraph):
   State this is a Local File prepared as compliance with PMK-172 Year 2023.

2. SUMMARY OF CONCLUSION (3-4 paragraphs):
   - Company background and business
   - Analysis approach (method, PLI, comparable source)
   - Number of comparable companies and how they were found
   - Interquartile range results and conclusion

3. SCOPE OF REPORT (1 paragraph + bullet list):
   - Sources used (meetings, financial data, regulations, OECD TPG, third-party databases)

RULES:
- RESPOND IN ENGLISH ONLY. Do NOT switch to Indonesian or any other language.
- Use exact numbers provided. Do NOT change any figures.
- Professional formal English
- Clearly label each section
"""
    return {"executive_summary": invoke_prompt(prompt)}
