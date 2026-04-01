"""
search_pipeline.py
───────────────────
Single-file search pipeline with:
  • Query rewriting via user-supplied LLM callable
  • Parallel Tavily search with deduplication
  • BGE-reranker-v2-m3 local reranking (lazy-loaded)
  • Jina Reader deep-crawl fallback
  • Token-capped context assembly
  • Structured synthesis prompt builder
  • MD5-cached main entry point
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import re
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

import tiktoken
from tavily import TavilyClient

logger = logging.getLogger(__name__)

# ── module-level singletons ──────────────────────────────────────────────────
_reranker = None          # lazy-loaded CrossEncoder
_cache: dict[str, dict] = {}   # in-memory query cache
_tiktoken_enc = None      # lazy tiktoken encoder


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_tiktoken():
    """Return a cached cl100k_base encoder."""
    global _tiktoken_enc
    if _tiktoken_enc is None:
        _tiktoken_enc = tiktoken.get_encoding("cl100k_base")
    return _tiktoken_enc


def _count_tokens(text: str) -> int:
    return len(_get_tiktoken().encode(text))


# ─────────────────────────────────────────────────────────────────────────────
# 1. rewrite_query
# ─────────────────────────────────────────────────────────────────────────────

_REWRITE_SYSTEM_PROMPT = """\
You are a search query optimizer. Given the user's question, produce
search-engine-optimized queries that will find the most relevant, recent results.

Rules:
- Always output the BEST single rewritten query on line 1.
- If the question is complex or multi-faceted, output up to 2 ADDITIONAL
  variant queries (one per line) that cover different angles.
- Output ONLY the queries, one per line. No numbering, no explanation.
- Keep each query concise (≤15 words).
"""


def rewrite_query(query: str, llm_fn: Callable[[str, str], str]) -> list[str]:
    """Rewrite *query* into 1–3 search-optimized variants via *llm_fn*.

    Parameters
    ----------
    query : str
        Raw user question.
    llm_fn : callable(system_prompt, user_prompt) -> str
        Any LLM callable the caller provides.

    Returns
    -------
    list[str]  – 1 to 3 rewritten queries.
    """
    try:
        raw = llm_fn(_REWRITE_SYSTEM_PROMPT, query)
        queries = [q.strip() for q in raw.strip().splitlines() if q.strip()]
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for q in queries:
            low = q.lower()
            if low not in seen:
                seen.add(low)
                unique.append(q)
        return unique[:3] if unique else [query]
    except Exception as e:
        logger.warning("Query rewrite failed, using original: %s", e)
        return [query]


# ─────────────────────────────────────────────────────────────────────────────
# 2. search_with_tavily
# ─────────────────────────────────────────────────────────────────────────────

def _tavily_search_single(query: str, max_results: int = 5) -> dict:
    """Run one Tavily search (sync, meant to be called in executor)."""
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY", ""))
    return client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced",
        include_answer=True,
    )


async def _tavily_search_async(queries: list[str]) -> list[dict]:
    """Dispatch Tavily searches in parallel via a thread-pool executor."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=min(len(queries), 5)) as pool:
        tasks = [
            loop.run_in_executor(pool, _tavily_search_single, q)
            for q in queries
        ]
        return await asyncio.gather(*tasks, return_exceptions=True)


def search_with_tavily(queries: list[str]) -> list[dict]:
    """Search Tavily in parallel for each query, merge & deduplicate by URL.

    Returns a flat list of result dicts, each with at least:
    ``{"url", "title", "content", "score"}``.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're inside an already-running loop (e.g. Streamlit / Jupyter).
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                raw_results = pool.submit(
                    asyncio.run, _tavily_search_async(queries)
                ).result()
        else:
            raw_results = loop.run_until_complete(_tavily_search_async(queries))
    except RuntimeError:
        raw_results = asyncio.run(_tavily_search_async(queries))

    # Merge & deduplicate
    seen_urls: dict[str, dict] = {}
    for res in raw_results:
        if isinstance(res, Exception):
            logger.warning("A Tavily search failed: %s", res)
            continue
        for item in res.get("results", []):
            url = item.get("url", "")
            existing = seen_urls.get(url)
            if existing is None or item.get("score", 0) > existing.get("score", 0):
                seen_urls[url] = item

    return list(seen_urls.values())


# ─────────────────────────────────────────────────────────────────────────────
# 3. rerank_results
# ─────────────────────────────────────────────────────────────────────────────

def _load_reranker():
    """Lazy-load the CrossEncoder reranker model."""
    global _reranker
    if _reranker is None:
        from sentence_transformers import CrossEncoder
        logger.info("Loading BAAI/bge-reranker-v2-m3 (first call)…")
        _reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")
    return _reranker


def rerank_results(query: str, results: list[dict], top_k: int = 5) -> list[dict]:
    """Score each result against *query* using BGE reranker, return top-*k*.

    Each returned dict gets an added ``rerank_score`` field.
    """
    if not results:
        return []

    model = _load_reranker()
    pairs = [(query, r.get("content", "") or r.get("title", "")) for r in results]
    scores = model.predict(pairs)

    for r, s in zip(results, scores):
        r["rerank_score"] = float(s)

    ranked = sorted(results, key=lambda r: r["rerank_score"], reverse=True)
    return ranked[:top_k]


# ─────────────────────────────────────────────────────────────────────────────
# 4. deep_crawl_fallback
# ─────────────────────────────────────────────────────────────────────────────

def deep_crawl_fallback(url: str, timeout: int = 15) -> str:
    """Fetch full page content via Jina Reader and return cleaned markdown.

    Calls ``https://r.jina.ai/{url}`` (free, no API key required).
    """
    jina_url = f"https://r.jina.ai/{url}"
    req = urllib.request.Request(
        jina_url,
        headers={
            "Accept": "text/markdown",
            "User-Agent": "search-pipeline/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        # Light cleanup: collapse excessive blank lines
        cleaned = re.sub(r"\n{3,}", "\n\n", raw).strip()
        return cleaned
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        logger.warning("Jina deep crawl failed for %s: %s", url, e)
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# 5. assemble_context
# ─────────────────────────────────────────────────────────────────────────────

def assemble_context(results: list[dict], max_tokens: int = 3000) -> str:
    """Format results into a numbered source block, hard-capped at *max_tokens*.

    Each block looks like::

        [1] Title — URL — Date
        Excerpt text …
    """
    enc = _get_tiktoken()
    blocks: list[str] = []
    total = 0

    for i, r in enumerate(results, 1):
        title = r.get("title", "Untitled")
        url = r.get("url", "")
        date = r.get("published_date", r.get("date", "n/a"))
        content = r.get("content", "") or ""

        header = f"[{i}] {title} — {url} — {date}"
        header_tokens = _count_tokens(header + "\n")

        remaining = max_tokens - total - header_tokens - 2  # 2 for newlines
        if remaining <= 0:
            break

        # Truncate content to fit token budget
        content_tokens = enc.encode(content)
        if len(content_tokens) > remaining:
            content = enc.decode(content_tokens[:remaining]) + " …"

        block = f"{header}\n{content}"
        blocks.append(block)
        total += _count_tokens(block) + 1  # +1 for separator newline

    return "\n\n".join(blocks)


# ─────────────────────────────────────────────────────────────────────────────
# 6. build_synthesis_prompt
# ─────────────────────────────────────────────────────────────────────────────

def build_synthesis_prompt(query: str, context: str) -> str:
    """Return a structured prompt for the LLM to synthesise an answer.

    The prompt instructs the model to:
    - Answer directly in the first sentence
    - Use inline citations [1], [2], …
    - Flag conflicting sources
    - Explicitly state if the answer isn't in the sources
    """
    return (
        "You are a research analyst. Use ONLY the provided sources to answer "
        "the user's question.\n\n"
        "## Rules\n"
        "1. Begin with a direct, concise answer in the FIRST sentence.\n"
        "2. Cite sources inline using bracketed numbers, e.g. [1], [2].\n"
        "3. If sources conflict, explicitly note the disagreement and which "
        "sources differ.\n"
        "4. If the answer is NOT found in the sources, say: "
        "\"The provided sources do not contain enough information to answer "
        "this question.\"\n"
        "5. Be concise. Do not repeat the question.\n\n"
        "## Sources\n"
        f"{context}\n\n"
        "## Question\n"
        f"{query}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# 7. cached_search  (main entry point)
# ─────────────────────────────────────────────────────────────────────────────

_FALLBACK_THRESHOLD = 0.3


def _cache_key(query: str) -> str:
    """MD5 hash of the normalised query."""
    normalized = query.strip().lower()
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


def clear_cache() -> int:
    """Clear the entire search cache. Returns the number of entries removed."""
    count = len(_cache)
    _cache.clear()
    logger.info("Cache cleared — %d entries removed", count)
    return count


def clear_cache_entry(query: str) -> bool:
    """Remove a single query from the cache. Returns True if it existed."""
    key = _cache_key(query)
    if key in _cache:
        del _cache[key]
        logger.info("Cache entry removed for query: %s", query)
        return True
    return False


def cached_search(
    query: str,
    llm_fn: Callable[[str, str], str],
) -> dict[str, Any]:
    """Main entry point. Returns cached result or runs the full pipeline.

    Parameters
    ----------
    query : str
        The raw user question.
    llm_fn : callable(system_prompt, user_prompt) -> str
        LLM callable for query rewriting.

    Returns
    -------
    dict with keys:
        - ``context``  – formatted source block (str)
        - ``prompt``   – synthesis prompt ready for LLM (str)
        - ``sources``  – list of source dicts with url, title, rerank_score
    """
    key = _cache_key(query)
    if key in _cache:
        logger.info("Cache HIT for query: %s", query)
        return _cache[key]

    logger.info("Cache MISS — running full pipeline for: %s", query)

    # Step 1 — Rewrite
    queries = rewrite_query(query, llm_fn)
    logger.info("Rewritten queries: %s", queries)

    # Step 2 — Search
    raw_results = search_with_tavily(queries)
    logger.info("Tavily returned %d unique results", len(raw_results))

    # Step 3 — Rerank
    ranked = rerank_results(query, raw_results)
    logger.info(
        "Top rerank scores: %s",
        [round(r.get("rerank_score", 0), 4) for r in ranked[:3]],
    )

    # Step 4 — Fallback if top score is too low
    if ranked and ranked[0].get("rerank_score", 0) < _FALLBACK_THRESHOLD:
        logger.info("Top score below %.1f — triggering deep crawl", _FALLBACK_THRESHOLD)
        top_url = ranked[0].get("url", "")
        if top_url:
            deep_content = deep_crawl_fallback(top_url)
            if deep_content:
                ranked[0]["content"] = deep_content
                logger.info("Deep crawl enriched top result (%d chars)", len(deep_content))

    # Step 5 — Assemble context
    context = assemble_context(ranked)

    # Step 6 — Build synthesis prompt
    prompt = build_synthesis_prompt(query, context)

    # Build sources list
    sources = [
        {
            "url": r.get("url", ""),
            "title": r.get("title", ""),
            "rerank_score": r.get("rerank_score", 0),
        }
        for r in ranked
    ]

    result = {
        "context": context,
        "prompt": prompt,
        "sources": sources,
    }

    _cache[key] = result
    return result
