"""
Analysis Subagent — functional analysis and business characterization nodes.

Nodes:
  - generate_functional_analysis        → functional_analysis_narrative
  - determine_business_characterization → business_characterization_text
"""
from agents.llm_factory import get_llm


# ─── Node: Functional Analysis Narrative ──────────────────────────────────────

def generate_functional_analysis(state: dict) -> dict:
    """Generate functional analysis narrative based on company type and transactions."""
    company_short = state.get("company_short_name", "the Company")
    business_desc = state.get("business_activities_description", "")
    products = state.get("products", [])
    product_names = ", ".join([p.get("name", "") for p in products]) if products else ""
    parent_group = state.get("parent_group", "the Group")
    transaction_type = state.get("transaction_type", "")

    llm = get_llm()
    prompt = f"""You are a transfer pricing analyst writing the Functional Analysis narrative for a TP Local File.

Company: {company_short}
Parent group: {parent_group}
Business description: {business_desc[:800]}
Products: {product_names}
Transaction type being analyzed: {transaction_type}

Based on this information, generate:

1. A SUPPLY CHAIN description (2-3 paragraphs) explaining:
   - How products flow from manufacturer to end customer
   - The role of each entity in the supply chain
   - Where value is created

2. A FUNCTIONAL ANALYSIS TABLE narrative listing functions performed by {company_short} vs the affiliated counterparty. For each function, indicate the level of involvement (Principal/Significant/Limited/None) for each party. Cover these functions:
   - Research & Development
   - Product Design
   - Manufacturing/Production
   - Quality Control
   - Procurement/Purchasing
   - Marketing & Sales
   - Distribution & Logistics
   - After-sales Service
   - Inventory Management
   - Strategic Management
   - Human Resources
   - Finance & Accounting

3. An ASSETS section listing key assets used by {company_short}

4. A RISKS section listing key risks borne by {company_short}

RULES:
- RESPOND IN ENGLISH ONLY. Do NOT switch to Indonesian or any other language.
- Be specific to the company's business activities
- Do NOT invent specific numbers
- Write in formal professional English
- Output the functional analysis table as a structured description
"""
    response = llm.invoke(prompt)
    return {"functional_analysis_narrative": response.content}


# ─── Node: Business Characterization ─────────────────────────────────────────

def determine_business_characterization(state: dict) -> dict:
    """Determine and justify the business characterization based on functional analysis."""
    company_short = state.get("company_short_name", "the Company")
    func_analysis = state.get("functional_analysis_narrative", "")
    business_desc = state.get("business_activities_description", "")

    llm = get_llm()
    prompt = f"""Based on the following functional analysis, determine the business characterization of {company_short}.

Business description: {business_desc[:500]}
Functional analysis: {func_analysis[:2000]}

The possible business characterizations are:
- Distributor (buys and resells without significant value addition)
- Limited Risk Distributor (minimal inventory/market risk, acts on behalf of principal)
- Commission Agent (does not take ownership of goods)
- Contract Manufacturer (manufactures based on principal's specifications)
- Toll Manufacturer (uses principal's raw materials)
- Full-Fledged Manufacturer (full control over manufacturing)
- Service Provider (provides services)
- Limited Risk Service Provider (provides routine services)

Write 2-3 paragraphs:
1. State the determined business characterization
2. Justify it based on functions, assets, and risks
3. Explain the implications for transfer pricing analysis

RULES:
- RESPOND IN ENGLISH ONLY. Do NOT switch to Indonesian or any other language.
- Base the characterization solely on the functional analysis provided
- Be specific and reference the functions/risks
- Professional formal English
"""
    response = llm.invoke(prompt)
    return {"business_characterization_text": response.content}
