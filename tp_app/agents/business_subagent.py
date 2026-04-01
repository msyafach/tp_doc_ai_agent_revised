"""
Business Subagent — generates the Business Activities & Operational Aspects narrative.

Nodes:
  - generate_business_activities → business_activities_description
  - generate_supply_chain        → supply_chain_management
"""
from agents.llm_factory import get_llm


def generate_business_activities(state: dict) -> dict:
    """
    Generate the Business Activities & Operational Aspects narrative.
    Skips if the field is already filled (manual input or PDF extraction).
    """
    existing = state.get("business_activities_description", "").strip()
    if existing:
        return {"business_activities_description": existing}

    company_name  = state.get("company_name", "the company")
    company_short = state.get("company_short_name", "")
    products      = state.get("products", [])
    product_names = ", ".join([p.get("name", "") for p in products]) if products else ""
    parent_co     = state.get("parent_company", "")
    parent_group  = state.get("parent_group", "")
    fiscal_year   = state.get("fiscal_year", "2024")
    biz_strategy  = state.get("business_strategy", "")[:300]
    mgmt          = state.get("management", [])

    mgmt_text = "; ".join(
        f"{m.get('position', '')} – {m.get('name', '')}"
        for m in mgmt[:8] if m.get("name")
    ) or "not specified"

    llm = get_llm()
    prompt = f"""You are a transfer pricing analyst writing the "Business Activities and Operational Aspects" section of a Transfer Pricing Local File for an Indonesian company.

Company details:
- Full name: {company_name}
- Short name: {company_short or company_name}
- Parent company: {parent_co or 'not specified'}
- Ultimate group: {parent_group or 'not specified'}
- Products / services: {product_names or 'not specified'}
- Business strategy hint: {biz_strategy or 'not provided'}
- Key management: {mgmt_text}
- Fiscal year: {fiscal_year}

Write 2–3 concise paragraphs (no headings, no bullet points) covering:
1. What the company does (main business activities, products/services traded or manufactured)
2. How it operates (distribution model, customer base, supply chain, relationship with group)
3. Any notable operational aspects (manufacturing vs. distribution, after-sales, value chain position)

Use formal transfer pricing documentation language. Refer to the company by its short name ({company_short or company_name}).
Do NOT include markdown, headers, or bullet points — write plain flowing paragraphs only."""

    response = llm.invoke(prompt)
    text = response.content.strip() if hasattr(response, "content") else str(response).strip()
    return {"business_activities_description": text}


# ─── Node: Supply Chain Management ───────────────────────────────────────────

def generate_supply_chain(state: dict) -> dict:
    """Generate the Supply Chain Management narrative based on form inputs."""
    company_short  = state.get("company_short_name", "the Company")
    company_name   = state.get("company_name", "the company")
    parent_co      = state.get("parent_company", "")
    parent_group   = state.get("parent_group", "")
    products       = state.get("products", [])
    product_names  = ", ".join([p.get("name", "") for p in products]) if products else ""
    transaction_type = state.get("transaction_type", "")
    counterparties = state.get("transaction_counterparties", [])
    counterparty_names = ", ".join(
        [c.get("name", "") for c in counterparties if c.get("name")]
    ) if counterparties else parent_co
    fiscal_year    = state.get("fiscal_year", "2024")
    biz_activities = state.get("business_activities_description", "")[:400]

    llm = get_llm()
    prompt = f"""You are a transfer pricing analyst writing the "Supply Chain Management" section for a Transfer Pricing Local File of an Indonesian company.

Company details:
- Company: {company_name} ("{company_short}")
- Parent company / group: {parent_co or parent_group or 'not specified'}
- Products / services: {product_names or 'not specified'}
- Transaction type with affiliates: {transaction_type or 'not specified'}
- Affiliated suppliers / counterparties: {counterparty_names or 'not specified'}
- Fiscal year: {fiscal_year}
- Business activities summary: {biz_activities or 'not provided'}

Write a narrative describing {company_short}'s supply chain in 4–6 bullet points covering the stages:
1. Product Development — who develops the products and where
2. Material Procurement / Manufacturing — who manufactures or sources the goods
3. Distribution — {company_short}'s role as distributor / seller in Indonesia
4. After-Sales Services — any after-sales or support activities performed by {company_short}

Rules:
- Use bullet points with "- " prefix for each stage
- Be specific: name the parent company / group members where relevant
- Use formal transfer pricing language
- RESPOND IN ENGLISH ONLY
- Do NOT invent figures or names not provided above
- Keep each bullet concise (2–3 sentences)"""

    response = llm.invoke(prompt)
    text = response.content.strip() if hasattr(response, "content") else str(response).strip()
    return {"supply_chain_management": text}
