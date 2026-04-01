"""
Wraps tp_app document processing and AI extraction.
"""
from __future__ import annotations
import os
import io
from dataclasses import dataclass
from typing import Any


@dataclass
class UploadedFileProxy:
    """Mimics Streamlit's UploadedFile so tp_app code works unchanged."""
    name: str
    size: int
    _data: bytes

    def read(self) -> bytes:
        return self._data

    def getvalue(self) -> bytes:
        return self._data

    def seek(self, pos: int) -> None:
        pass


def process_documents(files: list[dict], llm_provider: str, api_key: str,
                      model: str, tavily_key: str = "") -> dict[str, Any]:
    """
    files: list of {"name": str, "data_hex": str}  (bytes encoded as hex for Celery JSON transport)
    Returns extraction result dict (mirrors st.session_state.doc_extraction_result).
    """
    _set_env(llm_provider, api_key, model, tavily_key)

    proxies = []
    for f in files:
        raw = bytes.fromhex(f["data_hex"]) if "data_hex" in f else f.get("data", b"")
        proxies.append(UploadedFileProxy(name=f["name"], size=len(raw), _data=raw))

    from utils.document_processor import process_uploaded_files
    from agents.extraction_agent import extract_form_fields
    from agents.nodes import get_llm

    doc_context, errors = process_uploaded_files(proxies)
    if doc_context is None:
        return {"success": False, "errors": errors, "extraction": {}}

    llm = get_llm()
    extraction = extract_form_fields(doc_context, llm)

    return {
        "success": True,
        "errors": errors,
        "extraction": extraction,
        "strategy": getattr(doc_context, "strategy", "vector"),
        "page_count": getattr(doc_context, "page_count", None),
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
