from types import SimpleNamespace

from agents import llm_factory, nodes, tools


def test_agent_tools_registry_contains_expected_tools():
    tool_names = {tool_item.name for tool_item in tools.AGENT_TOOLS}
    assert "search_web_tool" in tool_names
    assert "sanitize_search_results_tool" in tool_names


def test_nodes_backward_compat_reexports():
    assert nodes.get_llm is llm_factory.get_llm
    assert nodes.get_tavily is llm_factory.get_tavily
    assert nodes.search_web is llm_factory.search_web


def test_invoke_prompt_with_tools_executes_requested_tool(monkeypatch):
    class FakeTool:
        def invoke(self, args):
            assert args["query"] == "indonesia market"
            return {"results": [{"title": "ok"}]}

    class FakeLLM:
        def __init__(self):
            self.calls = 0

        def bind_tools(self, _tools):
            return self

        def invoke(self, messages):
            self.calls += 1
            if self.calls == 1:
                return SimpleNamespace(
                    content="",
                    tool_calls=[
                        {
                            "id": "call-1",
                            "name": "search_web_tool",
                            "args": {"query": "indonesia market", "max_results": 1},
                        }
                    ],
                )
            return SimpleNamespace(content="final answer", tool_calls=[])

    monkeypatch.setattr(llm_factory, "get_llm", lambda provider=None, model=None: FakeLLM())
    monkeypatch.setattr(llm_factory, "AGENT_TOOL_BY_NAME", {"search_web_tool": FakeTool()})
    monkeypatch.setattr(llm_factory, "AGENT_TOOLS", [object()])

    result = llm_factory.invoke_prompt_with_tools("Use tools if needed.")

    assert result == "final answer"
