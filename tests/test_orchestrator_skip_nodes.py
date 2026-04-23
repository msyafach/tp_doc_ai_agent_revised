from agents.orchestrator import stream_agents


def test_stream_agents_all_skipped_nodes_do_not_raise_invalid_update():
    # Reproduces "Must write to at least one of [...]" when skipped nodes return {}.
    state = {
        "_skip_nodes": [
            "business_activities",
            "supply_chain",
            "industry_global",
            "industry_indonesia",
            "location_analysis",
            "industry_regulations",
            "business_env",
            "functional_analysis",
            "characterization",
            "background_transaction",
            "comparability",
            "method_selection",
            "pli_selection",
            "conclusion",
            "pl_overview",
            "research_comparables",
            "executive_summary",
        ]
    }

    updates = list(stream_agents(state))

    # If we reached here, no InvalidUpdateError was raised.
    assert updates
