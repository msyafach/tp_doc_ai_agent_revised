from agents.summary_subagent import (
    _extract_json_payload,
    _fallback_transaction_summary_packet,
    generate_transaction_findings_summary,
)


def test_extract_json_payload_handles_fenced_json():
    payload = """```json
    [{"section_title":"Purchase Transaction","holding":"arm's length"}]
    ```"""

    parsed = _extract_json_payload(payload)

    assert parsed[0]["section_title"] == "Purchase Transaction"
    assert parsed[0]["holding"] == "arm's length"


def test_fallback_transaction_summary_packet_builds_expected_shape():
    packets = _fallback_transaction_summary_packet({
        "transaction_type": "Purchase Transaction",
        "company_short_name": "PT SP",
        "selected_method": "TNMM",
        "selected_pli": "ROS",
        "quartile_range": {"q1": 2.14, "median": 3.14, "q3": 4.05},
        "tested_party_ratio": 4.45,
        "comparable_companies": [{"name": "A"}, {"name": "B"}],
        "method_selection_justification": "TNMM is the most reliable method.",
    })

    assert packets[0]["section_title"] == "Purchase Transaction"
    assert packets[0]["selected_method"] == "TNMM"
    assert packets[0]["comparable_count"] == 2
    assert packets[0]["holding"] == "above range"


def test_generate_transaction_findings_summary_falls_back_on_invalid_json(monkeypatch):
    monkeypatch.setattr(
        "agents.summary_subagent.invoke_prompt",
        lambda prompt: "not valid json",
    )

    result = generate_transaction_findings_summary({
        "transaction_type": "Purchase Transaction",
        "company_short_name": "PT SP",
        "selected_method": "TNMM",
        "selected_pli": "ROS",
        "quartile_range": {"q1": 2.14, "median": 3.14, "q3": 4.05},
        "tested_party_ratio": 4.45,
        "comparable_companies": [{"name": "A"}, {"name": "B"}],
        "method_selection_justification": "TNMM is the most reliable method.",
    })

    assert result["transaction_summary_packets"][0]["section_title"] == "Purchase Transaction"
