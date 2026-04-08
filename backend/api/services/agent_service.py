"""
Wraps tp_app LangGraph agent orchestration.
"""
from __future__ import annotations
import hashlib
import json
import os
from typing import Any


_IGNORED_STATE_KEYS = {
    "step", "agent_ran", "agent_errors",
    "groq_key_input", "openai_key_input", "tavily_key_input",
    "llm_provider_select", "groq_model_select", "openai_model_select",
    "doc_vectorstore",
    "_skip_nodes",  # runtime-only, never persisted
}

_AGENT_OUTPUT_KEYS = [
    "business_activities_description",
    "industry_analysis_global", "industry_analysis_indonesia",
    "company_location_analysis", "company_location_sources",
    "industry_regulations_text", "industry_regulations_sources",
    "business_environment_overview", "business_environment_sources",
    "conclusion_text", "functional_analysis_narrative",
    "business_characterization_text", "method_selection_justification",
    "pli_selection_rationale", "comparability_analysis_narrative",
    "industry_global_sources", "industry_indonesia_sources",
    "pl_overview_text", "background_transaction", "executive_summary",
    "supply_chain_management",
    "comparable_descriptions",
]

_NODE_LABELS = {
    "business_activities":    "Business activities description generated",
    "supply_chain":           "Supply chain management written",
    "industry_global":        "Global industry research complete",
    "industry_indonesia":     "Indonesian industry research complete",
    "location_analysis":      "Company location analysis complete",
    "industry_regulations":   "Industry regulations research complete",
    "business_env":           "Business environment research complete",
    "functional_analysis":    "Functional analysis generated",
    "characterization":       "Business characterization determined",
    "background_tx":          "Transaction background written",
    "comparability":          "Comparability analysis generated",
    "method_selection":       "TP method justification written",
    "pli_selection":          "PLI rationale written",
    "conclusion":             "Conclusion written",
    "pl_overview":             "P/L overview generated",
    "research_comparables":    "Comparable companies researched",
    "exec_summary":            "Executive summary written",
}

AGENT_KEY_MAP = {
    "industry_analysis_global":     "industry_global",
    "industry_analysis_indonesia":  "industry_indonesia",
    "company_location_analysis":    "location_analysis",
    "industry_regulations_text":    "industry_regulations",
    "business_environment_overview": "business_env",
    "functional_analysis_narrative": "functional_analysis",
    "business_characterization_text": "characterization",
    "comparability_analysis_narrative": "comparability",
    "method_selection_justification": "method_selection",
    "pli_selection_rationale":       "pli_selection",
    "conclusion_text":               "conclusion",
    "executive_summary":             "executive_summary",
    "pl_overview_text":              "pl_overview",
    "background_transaction":        "background_transaction",
    "supply_chain_management":       "supply_chain",
}

# Input fields each node depends on — used for cache invalidation.
# If any of these fields change, the node re-runs.
_NODE_INPUT_FIELDS: dict[str, list[str]] = {
    "business_activities": [
        "company_name", "company_short_name", "fiscal_year", "products",
        "business_strategy", "business_restructuring", "affiliated_parties",
        "transaction_type",
    ],
    "supply_chain": [
        "company_name", "company_short_name", "fiscal_year", "products",
        "affiliated_parties", "transaction_type", "business_activities_description",
    ],
    "industry_global": [
        "company_name", "company_short_name", "fiscal_year",
        "products", "parent_group", "business_activities_description",
    ],
    "industry_indonesia": [
        "company_name", "company_short_name", "fiscal_year",
        "products", "parent_group", "business_activities_description",
        "industry_analysis_global",
    ],
    "location_analysis": [
        "company_name", "company_address", "fiscal_year",
    ],
    "industry_regulations": [
        "company_name", "company_short_name", "fiscal_year",
        "transaction_type", "business_activities_description",
    ],
    "business_env": [
        "company_name", "company_short_name", "fiscal_year",
        "business_activities_description", "industry_analysis_global",
        "industry_analysis_indonesia",
    ],
    "functional_analysis": [
        "company_name", "company_short_name", "fiscal_year", "products",
        "affiliated_parties", "business_activities_description",
        "transaction_type", "shareholders", "management",
    ],
    "characterization": [
        "functional_analysis_narrative", "business_activities_description",
        "transaction_type",
    ],
    "background_tx": [
        "company_name", "company_short_name", "fiscal_year",
        "affiliated_parties", "transaction_type", "transaction_details_text",
        "pricing_policy", "affiliated_transactions", "independent_transactions",
    ],
    "comparability": [
        "company_name", "company_short_name", "fiscal_year",
        "comparable_companies", "selected_method", "selected_pli",
        "transaction_type", "functional_analysis_narrative",
    ],
    "method_selection": [
        "company_name", "fiscal_year", "transaction_type",
        "selected_method", "selected_pli", "functional_analysis_narrative",
        "business_characterization_text",
    ],
    "pli_selection": [
        "selected_method", "selected_pli", "comparable_companies", "fiscal_year",
    ],
    "conclusion": [
        "company_name", "company_short_name", "fiscal_year",
        "selected_method", "selected_pli", "quartile_range", "tested_party_ratio",
        "comparable_companies", "method_selection_justification",
    ],
    "pl_overview": [
        "company_name", "company_short_name", "fiscal_year",
        "financial_data", "financial_data_prior",
    ],
    "research_comparables": [
        "comparable_companies", "fiscal_year",
    ],
    "exec_summary": [
        "company_name", "company_short_name", "fiscal_year",
        "conclusion_text", "method_selection_justification",
        "functional_analysis_narrative", "background_transaction",
    ],
}

# Output key for each node — used to check if a cached result already exists.
_NODE_OUTPUT_KEY: dict[str, str] = {
    "business_activities": "business_activities_description",
    "supply_chain":         "supply_chain_management",
    "industry_global":      "industry_analysis_global",
    "industry_indonesia":   "industry_analysis_indonesia",
    "location_analysis":    "company_location_analysis",
    "industry_regulations": "industry_regulations_text",
    "business_env":         "business_environment_overview",
    "functional_analysis":  "functional_analysis_narrative",
    "characterization":     "business_characterization_text",
    "background_tx":        "background_transaction",
    "comparability":        "comparability_analysis_narrative",
    "method_selection":     "method_selection_justification",
    "pli_selection":        "pli_selection_rationale",
    "conclusion":           "conclusion_text",
    "pl_overview":          "pl_overview_text",
    "research_comparables": "comparable_descriptions",
    "exec_summary":         "executive_summary",
}


def _compute_hash(state: dict, fields: list[str]) -> str:
    """Hash the values of the given fields from state for cache comparison."""
    subset = {k: state.get(k) for k in fields}
    serialized = json.dumps(subset, sort_keys=True, default=str)
    return hashlib.md5(serialized.encode()).hexdigest()


def _build_skip_nodes(state: dict) -> list[str]:
    """
    Return list of node names whose inputs haven't changed and whose output
    already exists — these nodes will be skipped during Run All Agents.
    """
    cache: dict = state.get("_agent_cache", {})
    skip = []
    for node_name, fields in _NODE_INPUT_FIELDS.items():
        output_key = _NODE_OUTPUT_KEY.get(node_name)
        if not output_key:
            continue
        # Only skip if output already exists
        existing_output = state.get(output_key)
        if not existing_output:
            continue
        # Only skip if hash matches
        current_hash = _compute_hash(state, fields)
        if cache.get(node_name) == current_hash:
            skip.append(node_name)
    return skip


def _build_new_cache(state: dict, skip_nodes: list[str]) -> dict:
    """
    Return updated cache dict: keep existing hashes for skipped nodes,
    compute fresh hashes for nodes that actually ran.
    """
    old_cache: dict = state.get("_agent_cache", {})
    new_cache = dict(old_cache)
    for node_name, fields in _NODE_INPUT_FIELDS.items():
        if node_name not in skip_nodes:
            new_cache[node_name] = _compute_hash(state, fields)
    return new_cache


def _set_env(
    provider: str, api_key: str, model: str, tavily_key: str,
    langsmith_api_key: str = "", langsmith_project: str = "",
) -> None:
    os.environ["LLM_PROVIDER"] = provider
    if provider == "groq":
        os.environ["GROQ_API_KEY"] = api_key
        os.environ["GROQ_MODEL"] = model
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("OPENAI_MODEL", None)
    else:
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_MODEL"] = model
        os.environ.pop("GROQ_API_KEY", None)
        os.environ.pop("GROQ_MODEL", None)
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key
    if langsmith_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = langsmith_project or "tp-local-file-generator"
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"


def run_all_agents(
    state: dict[str, Any],
    provider: str, api_key: str, model: str, tavily_key: str,
    langsmith_api_key: str = "", langsmith_project: str = "",
    progress_callback=None,
) -> dict[str, Any]:
    """
    Run the full LangGraph agent pipeline.
    Nodes whose inputs are unchanged and whose output already exists are skipped.
    progress_callback(node_name, label) is called after each node completes.
    Returns the updated state dict.
    """
    _set_env(provider, api_key, model, tavily_key, langsmith_api_key, langsmith_project)
    from agents.orchestrator import stream_agents

    skip_nodes = _build_skip_nodes(state)

    agent_state = {k: v for k, v in state.items() if k not in _IGNORED_STATE_KEYS}
    agent_state["_skip_nodes"] = skip_nodes

    result = None
    for node_name, out_state in stream_agents(agent_state):
        if progress_callback:
            label = _NODE_LABELS.get(node_name, node_name)
            if node_name in skip_nodes:
                label = f"(cached) {label}"
            progress_callback(node_name, label)
        result = out_state

    if result is None:
        return {}

    updates = {k: result[k] for k in _AGENT_OUTPUT_KEYS if k in result and result[k]}
    updates["agent_ran"] = True
    updates["agent_errors"] = result.get("errors", [])
    updates["_agent_cache"] = _build_new_cache(state, skip_nodes)
    return updates


def run_single_agent(
    agent_key: str,
    state: dict[str, Any],
    provider: str, api_key: str, model: str, tavily_key: str,
    langsmith_api_key: str = "", langsmith_project: str = "",
) -> dict[str, Any]:
    """
    Regenerate a single section — always bypasses cache.
    After running, updates the cache hash for this node.
    """
    _set_env(provider, api_key, model, tavily_key, langsmith_api_key, langsmith_project)
    from agents.orchestrator import run_single_agent as _run

    node_name = AGENT_KEY_MAP.get(agent_key, agent_key)
    agent_state = {k: v for k, v in state.items() if k not in _IGNORED_STATE_KEYS}
    result = _run(node_name, agent_state)
    updates = {k: v for k, v in result.items() if k in _AGENT_OUTPUT_KEYS}

    # Update the cache hash for this specific node so the next "Run All" skips it
    old_cache = dict(state.get("_agent_cache", {}))
    fields = _NODE_INPUT_FIELDS.get(node_name, [])
    if fields:
        old_cache[node_name] = _compute_hash(state, fields)
    updates["_agent_cache"] = old_cache

    return updates
