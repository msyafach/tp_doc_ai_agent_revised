"""
Backward-compatibility re-exports.

All logic has been split into focused subagent modules:
  - agents/llm_factory.py         — get_llm, get_tavily, search_web
  - agents/business_subagent.py   — business activities narrative
  - agents/research_subagent.py   — industry & business-environment research
  - agents/analysis_subagent.py   — functional analysis & characterization
  - agents/transaction_subagent.py — background tx, comparability, method, PLI
  - agents/summary_subagent.py    — conclusion, P/L overview, executive summary

This file is kept so that external imports (e.g. `from agents.nodes import get_llm`)
continue to work without modification.
"""

from agents.llm_factory import get_llm, get_tavily, search_web          # noqa: F401
from agents.business_subagent import generate_business_activities        # noqa: F401
from agents.research_subagent import (                                   # noqa: F401
    research_industry_global,
    research_industry_indonesia,
    research_business_environment,
)
from agents.analysis_subagent import (                                   # noqa: F401
    generate_functional_analysis,
    determine_business_characterization,
)
from agents.transaction_subagent import (                                # noqa: F401
    generate_background_transaction,
    generate_comparability_narrative,
    generate_method_justification,
    generate_pli_rationale,
)
from agents.summary_subagent import (                                    # noqa: F401
    generate_executive_summary,
    generate_conclusion,
    generate_pl_overview,
)
