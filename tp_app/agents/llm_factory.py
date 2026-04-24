"""
Shared LLM factory and invocation helpers for TP subagents.
"""
from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
import re
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from agents.tools import (
    AGENT_TOOL_BY_NAME,
    AGENT_TOOLS,
    get_tavily,
    sanitize_search_results,
    search_web,
)

load_dotenv()


def get_llm(provider: str | None = None, model: str | None = None):
    """
    Get an LLM instance based on provider preference.

    Priority:
      1. Explicit provider/model args
      2. LLM_PROVIDER env var ("groq" or "openai")
      3. Auto-detect based on available API keys (Groq first, then OpenAI)
    """
    if provider is None:
        provider = os.environ.get("LLM_PROVIDER", "").lower() or None

    if not provider:
        if os.environ.get("GROQ_API_KEY"):
            provider = "groq"
        elif os.environ.get("OPENAI_API_KEY"):
            provider = "openai"
        else:
            raise ValueError("No LLM API key found. Please set GROQ_API_KEY or OPENAI_API_KEY.")

    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=model or os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0.2,
            max_tokens=4096,
            api_key=os.getenv("GROQ_API_KEY"),
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.2,
            max_completion_tokens=4096,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    raise ValueError(f"Unknown LLM provider: '{provider}'. Use 'groq' or 'openai'.")


_SYSTEM_INSTRUCTION = (
    "You are a professional transfer pricing analyst producing formal document text. "
    "Output ONLY the requested document content — no offers, no questions, no follow-up "
    "suggestions, no meta-commentary. End your response when the content is complete."
)

# Regex that matches trailing "offer" sentences at the end of the output
_TRAILING_OFFER_RE = re.compile(
    r"\s*(If you (?:want|need|would like|wish)|I can also|Would you like|Feel free|"
    r"Let me know|Please (?:let me know|feel free)|Should you need|"
    r"Do not hesitate|Don't hesitate|For (?:further|additional)|"
    r"You may also|Additionally,? I can|I'm (?:happy|available) to)[^.!?]*[.!?]?$",
    re.IGNORECASE | re.DOTALL,
)


def _clean_output(text: str) -> str:
    """Strip trailing conversational offers from LLM output."""
    cleaned = _TRAILING_OFFER_RE.sub("", text).rstrip()
    return cleaned


def invoke_prompt(prompt: str, provider: str | None = None, model: str | None = None) -> str:
    """Invoke LLM without tools and return text content."""
    llm = get_llm(provider=provider, model=model)
    messages = [SystemMessage(content=_SYSTEM_INSTRUCTION), HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    raw = response.content if hasattr(response, "content") else str(response)
    return _clean_output(raw)


def invoke_prompt_with_tools(
    prompt: str,
    provider: str | None = None,
    model: str | None = None,
    max_tool_rounds: int = 3,
) -> str:
    """
    Invoke LLM with LangChain tools bound, handling tool-calling loop.
    """
    llm_with_tools = get_llm(provider=provider, model=model).bind_tools(AGENT_TOOLS)
    messages: list[Any] = [SystemMessage(content=_SYSTEM_INSTRUCTION), HumanMessage(content=prompt)]

    for _ in range(max_tool_rounds):
        ai_message = llm_with_tools.invoke(messages)
        messages.append(ai_message)

        tool_calls = getattr(ai_message, "tool_calls", None) or []
        if not tool_calls:
            raw = ai_message.content if hasattr(ai_message, "content") else str(ai_message)
            return _clean_output(raw)

        for call in tool_calls:
            tool_name = call.get("name", "")
            tool_args = call.get("args", {}) or {}
            tool_obj = AGENT_TOOL_BY_NAME.get(tool_name)

            if tool_obj is None:
                tool_output = f"Tool '{tool_name}' is not available."
            else:
                try:
                    tool_output = tool_obj.invoke(tool_args)
                except Exception as exc:  # pragma: no cover
                    tool_output = f"Tool '{tool_name}' failed: {type(exc).__name__}: {exc}"

            content = tool_output if isinstance(tool_output, str) else json.dumps(tool_output, default=str)
            messages.append(ToolMessage(content=content, tool_call_id=call["id"]))

    final_message = llm_with_tools.invoke(messages)
    raw = final_message.content if hasattr(final_message, "content") else str(final_message)
    return _clean_output(raw)
