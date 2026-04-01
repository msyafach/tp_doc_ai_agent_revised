"""
LangGraph orchestrator for the Transfer Pricing Documentation workflow.

Parallel execution plan
───────────────────────
START
  └─ business_activities
       ├─ [BRANCH A] industry_global → industry_indonesia → business_env ─┐
       │                                                                    ├─ sync_analysis → background_transaction
       └─ [BRANCH B] functional_analysis → characterization ───────────────┘
                                                                              → comparability → method_selection → pli_selection
                                                                                  ├─ [BRANCH C] conclusion ─┐
                                                                                  │                          ├─ executive_summary → END
                                                                                  └─ [BRANCH D] pl_overview ─┘
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

from agents.research_subagent import (
    research_industry_global,
    research_industry_indonesia,
    research_business_environment,
    research_company_location,
    research_industry_regulations,
    research_comparable_companies,
)
from agents.analysis_subagent import (
    generate_functional_analysis,
    determine_business_characterization,
)
from agents.transaction_subagent import (
    generate_background_transaction,
    generate_comparability_narrative,
    generate_method_justification,
    generate_pli_rationale,
)
from agents.summary_subagent import (
    generate_executive_summary,
    generate_conclusion,
    generate_pl_overview,
)
from agents.business_subagent import generate_business_activities, generate_supply_chain


# ─── State definition ─────────────────────────────────────────────────────────

class AgentState(TypedDict, total=False):
    # Input fields
    company_name: str
    company_short_name: str
    company_address: str
    establishment_info: str
    fiscal_year: str
    shareholders: list
    management: list
    employee_count: str
    affiliated_parties: list
    parent_company: str
    parent_group: str
    business_activities_description: str
    products: list
    business_strategy: str
    business_restructuring: str
    transaction_type: str
    transaction_counterparties: list
    transaction_details_text: str
    pricing_policy: str
    financial_data: dict
    financial_data_prior: dict
    comparable_companies: list
    search_criteria_results: list
    rejection_matrix: list
    selected_method: str
    selected_pli: str
    tested_party: str
    analysis_period: str
    quartile_range: dict
    tested_party_ratio: float
    non_financial_events: str
    # Agent outputs
    industry_analysis_global: str
    industry_global_sources: list
    industry_analysis_indonesia: str
    industry_indonesia_sources: list
    company_location_analysis: str
    company_location_sources: list
    industry_regulations_text: str
    industry_regulations_sources: list
    business_environment_overview: str
    business_environment_sources: list
    executive_summary: str
    conclusion_text: str
    functional_analysis_narrative: str
    business_characterization_text: str
    method_selection_justification: str
    pli_selection_rationale: str
    comparability_analysis_narrative: str
    pl_overview_text: str
    background_transaction: str
    supply_chain_management: str
    comparable_descriptions: dict
    # Document upload / extraction
    uploaded_docs_processed: bool
    doc_extraction_result: dict
    # Use Annotated reducers so parallel branches can safely write to these keys
    # without causing INVALID_CONCURRENT_GRAPH_UPDATE errors.
    errors: Annotated[list, operator.add]


# ─── Node wrappers ────────────────────────────────────────────────────────────
# Each wrapper catches exceptions and returns a safe fallback + error entry.

def _node(fn, output_key: str, step_name: str):
    """Factory: wrap a subagent function with error handling.
    NOTE: do NOT write 'current_step' — parallel nodes writing the same
    non-annotated key simultaneously causes INVALID_CONCURRENT_GRAPH_UPDATE.
    """
    def wrapped(state: AgentState) -> dict:
        try:
            return fn(state)
        except Exception as e:
            return {
                output_key: f"[Error generating {step_name}. Please write this section manually.]",
                "errors": [f"{step_name}: {type(e).__name__}"],
            }
    wrapped.__name__ = f"node_{step_name}"
    return wrapped


def node_business_activities(state: AgentState) -> dict:
    try:
        return generate_business_activities(state)
    except Exception as e:
        return {"errors": [f"business_activities: {type(e).__name__}"]}


# ─── Sync (join) nodes ────────────────────────────────────────────────────────
# LangGraph waits for ALL incoming edges before running a node.
# These pass-through nodes act as explicit join barriers.

def node_sync_analysis(state: AgentState) -> dict:
    """Join barrier — waits for research branch AND analysis branch.
    Emits warnings if either upstream branch produced no usable output."""
    warns = []
    if not state.get("business_environment_overview"):
        warns.append("sync_analysis: research branch produced no business_environment_overview")
    if not state.get("business_characterization_text"):
        warns.append("sync_analysis: analysis branch produced no business_characterization_text")
    return {"errors": warns}


def node_sync_summary(state: AgentState) -> dict:
    """Join barrier — waits for conclusion branch AND pl_overview branch.
    Emits warnings if either upstream branch produced no usable output."""
    warns = []
    if not state.get("conclusion_text"):
        warns.append("sync_summary: conclusion branch produced no conclusion_text")
    if not state.get("pl_overview_text"):
        warns.append("sync_summary: pl_overview branch produced no pl_overview_text")
    return {"errors": warns}


# ─── Build the graph ──────────────────────────────────────────────────────────

def build_tp_graph():
    graph = StateGraph(AgentState)

    # ── Register nodes ──────────────────────────────────────────────────────
    graph.add_node("business_activities", node_business_activities)
    graph.add_node("supply_chain", _node(generate_supply_chain, "supply_chain_management", "supply_chain"))

    # Branch A — research (sequential within branch)
    graph.add_node("industry_global",    _node(research_industry_global,    "industry_analysis_global",       "industry_global"))
    graph.add_node("industry_indonesia", _node(research_industry_indonesia,  "industry_analysis_indonesia",    "industry_indonesia"))
    graph.add_node("location_analysis",      _node(research_company_location,      "company_location_analysis",      "location_analysis"))
    graph.add_node("industry_regulations",   _node(research_industry_regulations,  "industry_regulations_text",      "industry_regulations"))
    graph.add_node("business_env",           _node(research_business_environment,  "business_environment_overview",  "business_env"))

    # Branch B — analysis (sequential within branch)
    graph.add_node("functional_analysis", _node(generate_functional_analysis,         "functional_analysis_narrative",   "functional_analysis"))
    graph.add_node("characterization",    _node(determine_business_characterization,  "business_characterization_text",  "characterization"))

    # Join A+B
    graph.add_node("sync_analysis", node_sync_analysis)

    # Sequential: background → comparability → method → PLI
    graph.add_node("background_tx", _node(generate_background_transaction,  "background_transaction",           "background_transaction"))
    graph.add_node("comparability",          _node(generate_comparability_narrative, "comparability_analysis_narrative", "comparability"))
    graph.add_node("method_selection",       _node(generate_method_justification,    "method_selection_justification",   "method_selection"))
    graph.add_node("pli_selection",          _node(generate_pli_rationale,           "pli_selection_rationale",          "pli_selection"))

    # Branch C+D+E — conclusion, P/L overview, comparable research run in parallel
    graph.add_node("conclusion",           _node(generate_conclusion,                "conclusion_text",         "conclusion"))
    graph.add_node("pl_overview",          _node(generate_pl_overview,               "pl_overview_text",        "pl_overview"))
    graph.add_node("research_comparables", _node(research_comparable_companies,      "comparable_descriptions", "research_comparables"))

    # Join C+D+E
    graph.add_node("sync_summary", node_sync_summary)

    # Final node
    graph.add_node("exec_summary", _node(generate_executive_summary, "executive_summary", "executive_summary"))

    # ── Wire edges ──────────────────────────────────────────────────────────
    graph.set_entry_point("business_activities")

    # business_activities → supply_chain (sequential), then fan-out
    graph.add_edge("business_activities", "supply_chain")
    graph.add_edge("supply_chain", "industry_global")      # Branch A start
    graph.add_edge("supply_chain", "functional_analysis")  # Branch B start

    # Branch A (sequential)
    graph.add_edge("industry_global",    "industry_indonesia")
    graph.add_edge("industry_indonesia", "location_analysis")     # new node 1
    graph.add_edge("location_analysis",  "industry_regulations")  # new node 2
    graph.add_edge("industry_regulations","business_env")
    graph.add_edge("business_env",       "sync_analysis")  # A → join

    # Branch B (sequential)
    graph.add_edge("functional_analysis", "characterization")
    graph.add_edge("characterization",    "sync_analysis")  # B → join

    # After join A+B: sequential transaction analysis
    graph.add_edge("sync_analysis",          "background_tx")
    graph.add_edge("background_tx", "comparability")
    graph.add_edge("comparability",          "method_selection")
    graph.add_edge("method_selection",       "pli_selection")

    # Fan-out: conclusion, P/L overview, and comparable research run in parallel
    graph.add_edge("pli_selection", "conclusion")            # Branch C
    graph.add_edge("pli_selection", "pl_overview")           # Branch D
    graph.add_edge("pli_selection", "research_comparables")  # Branch E

    # All three feed into sync_summary join
    graph.add_edge("conclusion",           "sync_summary")
    graph.add_edge("pl_overview",          "sync_summary")
    graph.add_edge("research_comparables", "sync_summary")

    # Final
    graph.add_edge("sync_summary",    "exec_summary")
    graph.add_edge("exec_summary", END)

    return graph.compile()


# ─── Public API ───────────────────────────────────────────────────────────────

def run_agents(state_data: dict, progress_callback=None) -> dict:
    """
    Run the full agent workflow with parallel branches.

    Args:
        state_data: Dictionary with all manual input data
        progress_callback: Optional callback(step_name, status) for UI updates

    Returns:
        Final state with all generated content
    """
    graph = build_tp_graph()
    initial_state = {
        **state_data,
        "errors": [],
    }
    return graph.invoke(initial_state)


def stream_agents(state_data: dict):
    """
    Run agents with real-time streaming.

    Yields (node_name, accumulated_state) as each agent node completes,
    enabling live progress updates in the UI. Sync/join nodes are skipped.
    The last yielded accumulated_state contains the final complete output.
    """
    graph = build_tp_graph()
    initial_state = {**state_data, "current_step": "starting", "errors": []}
    accumulated = dict(initial_state)

    for chunk in graph.stream(initial_state, stream_mode="updates"):
        for node_name, updates in chunk.items():
            if updates is None or node_name.startswith("__"):
                continue
            # Merge errors with list concatenation (mirrors Annotated[list, operator.add])
            if "errors" in updates:
                accumulated["errors"] = (
                    accumulated.get("errors", []) + list(updates.pop("errors", []))
                )
            accumulated.update(updates)
            # Only yield real agent nodes, not internal sync barriers
            if not node_name.startswith("sync_"):
                yield node_name, accumulated


def run_single_agent(agent_name: str, state_data: dict) -> dict:
    """Run a single agent node for regeneration (e.g., from the UI)."""
    agents = {
        "business_activities":   generate_business_activities,
        "supply_chain":          generate_supply_chain,
        "industry_global":       research_industry_global,
        "industry_indonesia":    research_industry_indonesia,
        "location_analysis":     research_company_location,
        "industry_regulations":  research_industry_regulations,
        "business_env":          research_business_environment,
        "functional_analysis":   generate_functional_analysis,
        "characterization":      determine_business_characterization,
        "background_transaction":generate_background_transaction,
        "comparability":         generate_comparability_narrative,
        "method_selection":      generate_method_justification,
        "pli_selection":         generate_pli_rationale,
        "conclusion":             generate_conclusion,
        "pl_overview":            generate_pl_overview,
        "research_comparables":   research_comparable_companies,
        "executive_summary":      generate_executive_summary,
    }

    if agent_name not in agents:
        raise ValueError(f"Unknown agent: {agent_name}")

    return agents[agent_name](state_data)
