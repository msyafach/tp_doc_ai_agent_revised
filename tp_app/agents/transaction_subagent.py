"""
Transaction Subagent — background, comparability, method selection, and PLI nodes.

Nodes:
  - generate_background_transaction  → background_transaction
  - generate_comparability_narrative → comparability_analysis_narrative
  - generate_method_justification    → method_selection_justification
  - generate_pli_rationale           → pli_selection_rationale
"""
from agents.llm_factory import invoke_prompt


# ─── Node: Background of Transaction to Affiliated Party ──────────────────────

def generate_background_transaction(state: dict) -> dict:
    """
    Generate a clean narrative for section 4.1.2.1 — Background of Transaction
    to Affiliated Party. Outputs plain prose paragraphs; no labels, no bullets,
    no markdown symbols.
    """
    company_short    = state.get("company_short_name", "the Company")
    company_name     = state.get("company_name", company_short)
    parent_co        = state.get("parent_company", "its parent company")
    parent_group     = state.get("parent_group", "the Group")
    fiscal_year      = state.get("fiscal_year", "2024")
    transaction_type = state.get("transaction_type", "")
    business_desc    = state.get("business_activities_description", "")[:600]
    affiliated       = state.get("affiliated_transactions", [])

    aff_lines = []
    for a in affiliated[:5]:
        name = a.get("name", "")
        txn  = a.get("transaction_type", "")
        val  = a.get("value", "")
        if name:
            aff_lines.append(f"- {name}: {txn} of {val}" if txn or val else f"- {name}")
    aff_context = "\n".join(aff_lines) or "not specified"

    prompt = f"""You are a transfer pricing analyst writing section 4.1.2.1 "Background of Transaction to Affiliated Party" for a Transfer Pricing Local File under Indonesian regulation PMK-172/2023.

Company: {company_name} ({company_short})
Parent company: {parent_co}
Business group: {parent_group}
Fiscal year: {fiscal_year}
Primary transaction type: {transaction_type}
Business description: {business_desc}
Affiliated transactions conducted:
{aff_context}

Write 2–3 concise paragraphs explaining the background and commercial rationale for why {company_short} conducts transactions with its affiliated parties. Cover:
1. The economic and business rationale for the affiliated transactions (group integration, efficiency, cost internalization, economies of scale)
2. The nature of the transactions and the relationship with the affiliated counterparties
3. How these transactions support {company_short}'s business operations

STRICT RULES:
- Write ONLY plain flowing prose paragraphs — NO bullet points, NO numbered lists
- Do NOT use any labels or prefixes such as "Procurement/Purchasing:", "Marketing & Sales:", etc.
- Do NOT use markdown symbols (**, *, #, __, etc.)
- Do NOT include section headings or subheadings
- Refer to the company by its short name ({company_short})
- Use formal, professional English
- Each paragraph should be a complete, coherent thought
"""
    text = invoke_prompt(prompt).strip()
    return {"background_transaction": text}


# ─── Node: Comparability Analysis Narrative ───────────────────────────────────

def generate_comparability_narrative(state: dict) -> dict:
    """Generate the comparability analysis narrative section."""
    company_short = state.get("company_short_name", "")
    transaction_type = state.get("transaction_type", "")
    products = state.get("products", [])
    product_names = ", ".join([p.get("name", "") for p in products]) if products else ""

    prompt = f"""Write the Comparability Analysis section for a Transfer Pricing Local File.

Company: {company_short}
Transaction type: {transaction_type}
Products: {product_names}

Write 3-4 paragraphs covering:
1. The five comparability factors as per PMK-172 and OECD TPG:
   a. Characteristics of property/services
   b. Functional analysis (functions, assets, risks)
   c. Contractual terms
   d. Economic circumstances / market conditions
   e. Business strategies
2. How these factors were applied in the current analysis
3. The approach to finding comparable data (internal vs external comparables)
4. The use of Bureau Van Dijk TP Catalyst Database

Professional formal English, no headers within the text.
RESPOND IN ENGLISH ONLY. Do NOT switch to Indonesian or any other language.
"""
    return {"comparability_analysis_narrative": invoke_prompt(prompt)}


# ─── Node: Method Selection Justification ─────────────────────────────────────

def generate_method_justification(state: dict) -> dict:
    """Generate justification for why each method was selected or rejected."""
    company_short = state.get("company_short_name", "the Company")
    selected_method = state.get("selected_method", "TNMM")
    transaction_type = state.get("transaction_type", "")
    business_char = state.get("business_characterization_text", "")
    selected_pli = state.get("selected_pli", "ROS")

    prompt = f"""You are a transfer pricing analyst writing the Transfer Pricing Method Selection section.

Company: {company_short}
Transaction type: {transaction_type}
Business characterization: {business_char[:500]}
Selected method: {selected_method}
Selected PLI: {selected_pli}

For EACH of the five TP methods (CUP, RPM, CPM, PSM, TNMM), write a paragraph explaining:
- Whether it was selected or rejected for this transaction
- The specific reasons for selection or rejection based on the company's characteristics

Then write a separate section on:
- Why {selected_pli} was chosen as the Profit Level Indicator
- Why other PLIs were less suitable

Format each method with its name as a clear label.

RULES:
- RESPOND IN ENGLISH ONLY. Do NOT switch to Indonesian or any other language.
- The selected method ({selected_method}) should have the strongest justification
- Reference specific aspects of the functional analysis/business characterization
- Follow PMK-172 and OECD TPG guidance
- Professional formal English
"""
    return {"method_selection_justification": invoke_prompt(prompt)}


# ─── Node: PLI Selection Rationale ───────────────────────────────────────────

def generate_pli_rationale(state: dict) -> dict:
    """Generate rationale for PLI selection."""
    company_short = state.get("company_short_name", "the Company")
    selected_method = state.get("selected_method", "TNMM")
    selected_pli = state.get("selected_pli", "ROS")
    transaction_type = state.get("transaction_type", "")

    pli_explanations = {
        "ROS": "Return on Sales (ROS) measures operating profit as a percentage of net sales revenue",
        "GPM": "Gross Profit Margin (GPM) measures gross profit as a percentage of net sales revenue",
        "Berry Ratio": "Berry Ratio measures gross profit relative to operating expenses",
        "NCPM": "Net Cost Plus Markup (NCPM) measures operating profit as a percentage of total costs",
        "ROA": "Return on Assets (ROA) measures operating profit relative to total assets employed",
        "ROCE": "Return on Capital Employed (ROCE) measures operating profit relative to capital employed",
    }

    prompt = f"""Write a 2-3 paragraph justification for selecting {selected_pli} ({pli_explanations.get(selected_pli, '')}) as the Profit Level Indicator for the transfer pricing analysis of {company_short}.

Context:
- TP method: {selected_method}
- Transaction type: {transaction_type}

Cover:
1. Why {selected_pli} is appropriate for this type of company and transaction
2. Why other PLIs are less suitable
3. Reference to OECD guidelines or PMK-172

Professional formal English, no headers.
RESPOND IN ENGLISH ONLY. Do NOT switch to Indonesian or any other language.
"""
    return {"pli_selection_rationale": invoke_prompt(prompt)}
