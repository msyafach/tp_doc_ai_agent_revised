"""
State definitions and configuration for the TP Documentation Agent.
"""
from typing import TypedDict, Optional, Literal
from dataclasses import dataclass, field

# ─── Section categorization ────────────────────────────────────────────────────

SECTION_TYPES = {
    "template": [
        "glossary",
        "statement_letter",
        "tp_regulations",
        "special_relationship",
        "related_tax_laws",
        "tax_administration",
        "tp_methods_overview",
        "tax_audit_process",
        "functional_analysis_methodology",
        "search_criteria_descriptions",
        "references",
    ],
    "manual_input": [
        "company_identity",
        "ownership_structure",
        "management_structure",
        "organization_structure",
        "affiliated_parties_list",
        "business_activities",
        "products_services",
        "business_strategy",
        "business_restructuring",
        "transaction_details",
        "pricing_policy",
        "financial_statements",
        "comparable_companies_data",
        "non_financial_events",
    ],
    "agent_automated": [
        "industry_analysis_global",
        "industry_analysis_indonesia",
        "business_environment",
        "executive_summary",
        "conclusion",
        "functional_analysis_narrative",
        "business_characterization",
        "method_selection_justification",
        "pli_selection_rationale",
        "comparability_analysis_narrative",
    ],
}


# ─── LangGraph State ──────────────────────────────────────────────────────────

class TPDocState(TypedDict, total=False):
    # Company info (manual)
    company_name: str
    company_short_name: str
    company_address: str
    establishment_info: str
    fiscal_year: str
    
    # Ownership & management (manual)
    shareholders: list[dict]  # [{name, shares, capital, percentage}]
    management: list[dict]    # [{position, name}]
    employee_count: str
    
    # Affiliated parties (manual)
    affiliated_parties: list[dict]  # [{name, country, relationship, transaction_type}]
    parent_company: str
    parent_group: str
    
    # Business info (manual)
    business_activities_description: str
    products: list[dict]  # [{name, description}]
    business_strategy: str
    business_restructuring: str
    
    # Transaction info (manual)
    transaction_type: str  # "purchase" | "sale" | "service" | "royalty"
    transaction_counterparties: list[dict]
    transaction_details_text: str
    pricing_policy: str
    
    # Financial data (manual)
    financial_data: dict  # P&L summary {sales, cogs, gross_profit, opex, operating_profit, ...}
    financial_data_prior: dict
    
    # Comparable companies (manual from BvD)
    comparable_companies: list[dict]  # [{name, country, description, ros_data}]
    search_criteria_results: list[dict]  # [{step, criteria, result_count}]
    rejection_matrix: list[dict]
    
    # TP Analysis parameters (manual)
    selected_method: str  # CUP, RPM, CPM, PSM, TNMM
    selected_pli: str     # ROS, GPM, Berry Ratio, etc.
    tested_party: str
    analysis_period: str  # e.g. "2020-2022"
    quartile_range: dict  # {q1, median, q3}
    tested_party_ratio: float
    
    # Non-financial (manual)
    non_financial_events: str
    
    # ─── Agent-generated content ──────────────────────────────────
    industry_analysis_global: str
    industry_analysis_indonesia: str
    business_environment_overview: str
    executive_summary: str
    conclusion_text: str
    functional_analysis_narrative: str
    business_characterization_text: str
    method_selection_justification: str
    pli_selection_rationale: str
    comparability_analysis_narrative: str
    
    # Document upload / extraction
    uploaded_docs_processed: bool
    doc_extraction_result: dict

    # Agent workflow control
    current_step: str
    errors: list[str]
    agent_status: dict  # {section_name: "pending"|"running"|"done"|"error"}


# ─── Business characterization types ──────────────────────────────────────────

BUSINESS_TYPES = [
    "Distributor",
    "Limited Risk Distributor",
    "Commission Agent",
    "Contract Manufacturer",
    "Toll Manufacturer",
    "Full-Fledged Manufacturer",
    "Service Provider",
    "Limited Risk Service Provider",
    "Contract R&D",
    "Full-Fledged R&D",
]

TP_METHODS = ["CUP", "RPM", "CPM", "PSM", "TNMM"]

PLI_OPTIONS = {
    "ROS": "Return on Sales (Operating Profit / Sales)",
    "GPM": "Gross Profit Margin (Gross Profit / Sales)",
    "Berry Ratio": "Berry Ratio (Gross Profit / Operating Expenses)",
    "NCPM": "Net Cost Plus Markup (Operating Profit / Total Costs)",
    "ROA": "Return on Assets (Operating Profit / Total Assets)",
    "ROCE": "Return on Capital Employed",
}

TRANSACTION_TYPES = [
    "Purchase of tangible goods",
    "Sale of tangible goods",
    "Intra-group services",
    "Royalty/License fees",
    "Interest on loans",
    "Management fees",
]
