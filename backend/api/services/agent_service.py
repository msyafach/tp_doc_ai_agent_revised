"""
Wraps tp_app LangGraph agent orchestration.
"""
from __future__ import annotations
import os
from typing import Any, Generator


_IGNORED_STATE_KEYS = {
    "step", "agent_ran", "agent_errors",
    "groq_key_input", "openai_key_input", "tavily_key_input",
    "llm_provider_select", "groq_model_select", "openai_model_select",
    "doc_vectorstore",
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


def _set_env(provider: str, api_key: str, model: str, tavily_key: str) -> None:
    os.environ["LLM_PROVIDER"] = provider
    if provider == "groq":
        os.environ["GROQ_API_KEY"] = api_key
        os.environ["GROQ_MODEL"] = model
    else:
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_MODEL"] = model
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key


def run_all_agents(
    state: dict[str, Any],
    provider: str, api_key: str, model: str, tavily_key: str,
    progress_callback=None,
) -> dict[str, Any]:
    """
    Run the full LangGraph agent pipeline.
    progress_callback(node_name, label) is called after each node completes.
    Returns the updated state dict.
    """
    _set_env(provider, api_key, model, tavily_key)
    from agents.orchestrator import stream_agents

    agent_state = {k: v for k, v in state.items() if k not in _IGNORED_STATE_KEYS}

    result = None
    for node_name, out_state in stream_agents(agent_state):
        if progress_callback:
            label = _NODE_LABELS.get(node_name, node_name)
            progress_callback(node_name, label)
        result = out_state

    if result is None:
        return {}

    updates = {k: result[k] for k in _AGENT_OUTPUT_KEYS if k in result and result[k]}
    updates["agent_ran"] = True
    updates["agent_errors"] = result.get("errors", [])
    return updates


def run_single_agent(
    agent_key: str,
    state: dict[str, Any],
    provider: str, api_key: str, model: str, tavily_key: str,
) -> dict[str, Any]:
    """Regenerate a single section."""
    _set_env(provider, api_key, model, tavily_key)
    from agents.orchestrator import run_single_agent as _run

    node_name = AGENT_KEY_MAP.get(agent_key, agent_key)
    agent_state = {k: v for k, v in state.items() if k not in _IGNORED_STATE_KEYS}
    result = _run(node_name, agent_state)
    return {k: v for k, v in result.items() if k in _AGENT_OUTPUT_KEYS}
