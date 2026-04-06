import React, { useState, useEffect } from "react";
import { Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { InfoBadge } from "../components/InfoBadge";
import { SectionCard } from "../components/SectionCard";
import { FormField } from "../components/FormField";
import { useProjectStore } from "../store/projectStore";
import { runAgents, runSingleAgent, pollTaskStatus, getProject } from "../api/projects";
import type { AgentTask } from "../types";
import clsx from "clsx";

const NODE_LABELS: Record<string, string> = {
  business_activities:    "Business activities description generated",
  supply_chain:           "Supply chain management written",
  industry_global:        "Global industry research complete",
  industry_indonesia:     "Indonesian industry research complete",
  location_analysis:      "Company location analysis complete",
  industry_regulations:   "Industry regulations research complete",
  business_env:           "Business environment research complete",
  functional_analysis:    "Functional analysis generated",
  characterization:       "Business characterization determined",
  background_tx:          "Transaction background written",
  comparability:          "Comparability analysis generated",
  method_selection:       "TP method justification written",
  pli_selection:          "PLI rationale written",
  conclusion:             "Conclusion written",
  pl_overview:             "P/L overview generated",
  research_comparables:    "Comparable companies researched",
  exec_summary:            "Executive summary written",
};

const REVIEWABLE_SECTIONS: { key: string; label: string }[] = [
  { key: "industry_analysis_global",       label: "Global Industry Analysis" },
  { key: "industry_analysis_indonesia",    label: "Indonesian Industry Analysis" },
  { key: "company_location_analysis",      label: "Efficiency & Excellence of Company Location" },
  { key: "industry_regulations_text",      label: "Regulations Affecting the Industry" },
  { key: "business_environment_overview",  label: "Business Environment" },
  { key: "supply_chain_management",        label: "Supply Chain Management" },
  { key: "functional_analysis_narrative",  label: "Functional Analysis" },
  { key: "comparability_analysis_narrative","label": "Comparability Analysis" } as unknown as { key: string; label: string },
  { key: "method_selection_justification", label: "Method Selection Justification" },
  { key: "pli_selection_rationale",        label: "PLI Selection Rationale" },
  { key: "conclusion_text",                label: "Conclusion" },
  { key: "pl_overview_text",               label: "Profit/Loss Overview" },
  { key: "executive_summary",              label: "Executive Summary" },
];

export function Step10AIAgents() {
  const { projectId, state, apiSettings, setState } = useProjectStore();
  const [taskId, setTaskId] = useState<number | null>(null);
  const [task, setTask] = useState<AgentTask | null>(null);
  const [polling, setPolling] = useState(false);
  const [openSections, setOpenSections] = useState<Set<string>>(new Set());
  const [regenLoading, setRegenLoading] = useState<string | null>(null);

  const hasLlm = !!apiSettings.api_key;
  const hasTavily = !!apiSettings.tavily_key;

  const missingFields = [
    !state.company_name && "Company Name",
    !state.company_short_name && "Company Short Name",
    !state.fiscal_year && "Fiscal Year",
  ].filter(Boolean) as string[];

  const startAgents = async () => {
    if (!projectId) {
      alert("No project loaded. Please refresh the page or create a new project.");
      return;
    }
    if (!hasLlm) {
      alert("Please add your LLM API key in the sidebar (Groq or OpenAI).");
      return;
    }
    if (missingFields.length > 0) {
      alert(`Please fill in required fields first: ${missingFields.join(", ")}`);
      return;
    }
    setTask(null);
    try {
      const { task_id } = await runAgents(projectId, apiSettings);
      setTaskId(task_id);
      setPolling(true);
    } catch (e: unknown) {
      let errStr = "Unknown error";
      if (e && typeof e === "object" && "response" in e) {
        const res = (e as { response?: { data?: unknown; status?: number } }).response;
        if (res?.data && typeof res.data === "object" && "detail" in res.data) {
          errStr = String((res.data as { detail: unknown }).detail);
        } else if (res?.status === 404) {
          errStr = "Backend not found. Is the server running?";
        } else if (res?.status) {
          errStr = `HTTP ${res.status}`;
        }
      } else if (e instanceof Error) {
        errStr = e.message;
      }
      alert(`Failed to start agents: ${errStr}\n\nMake sure the backend is running (e.g. docker-compose up) and the API proxy is configured.`);
    }
  };

  useEffect(() => {
    if (!polling || taskId === null) return;
    let cancelled = false;

    const poll = async () => {
      while (!cancelled) {
        try {
          const t = await pollTaskStatus(taskId);
          setTask(t);
          if (t.status === "success" || t.status === "error") {
            setPolling(false);
            if (t.status === "success" && t.result && projectId) {
              // Refresh project state from server
              const proj = await getProject(projectId);
              setState(proj.state);
            }
            return;
          }
        } catch { /* ignore */ }
        await new Promise((r) => setTimeout(r, 2000));
      }
    };
    poll();
    return () => { cancelled = true; };
  }, [polling, taskId]);

  const toggleSection = (key: string) =>
    setOpenSections((prev) => { const n = new Set(prev); n.has(key) ? n.delete(key) : n.add(key); return n; });

  const handleRegen = async (sectionKey: string) => {
    if (!projectId) return;
    setRegenLoading(sectionKey);
    try {
      const { task_id } = await runSingleAgent(projectId, sectionKey, apiSettings);
      // Wait for completion
      const wait = async (): Promise<void> => {
        const t = await pollTaskStatus(task_id);
        if (t.status === "success" || t.status === "error") {
          if (t.status === "success" && t.result) {
            setState(t.result as Parameters<typeof setState>[0]);
          }
          return;
        }
        await new Promise((r) => setTimeout(r, 2000));
        return wait();
      };
      await wait();
    } catch { /* ignore */ }
    setRegenLoading(null);
  };

  const completedNodes = task?.progress_log.map((p) => p.node) ?? [];
  const allNodes = Object.keys(NODE_LABELS);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">AI Agent Generation</h1>
        <InfoBadge variant="ai" description="AI agents research and generate content sections" />
      </div>

      {/* Status cards */}
      <div className="grid grid-cols-2 gap-3">
        <div className={clsx("rounded-lg border px-4 py-3 text-sm font-medium",
          hasLlm ? "border-green-200 bg-green-50 text-brand-dark" : "border-red-200 bg-red-50 text-red-700"
        )}>
          LLM: {apiSettings.llm_provider.toUpperCase()} / {apiSettings.model}
        </div>
        <div className={clsx("rounded-lg border px-4 py-3 text-sm font-medium",
          hasTavily ? "border-green-200 bg-green-50 text-brand-dark" : "border-amber-200 bg-amber-50 text-amber-700"
        )}>
          {hasTavily ? "Tavily API configured" : "Tavily key missing (web research disabled)"}
        </div>
      </div>

      {missingFields.length > 0 && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Please fill in required fields first: <strong>{missingFields.join(", ")}</strong>
        </div>
      )}

      <SectionCard>
        <button
          onClick={startAgents}
          disabled={polling}
          title={
            polling ? "Agents are running…" :
            !hasLlm ? "Add your LLM API key in the sidebar" :
            missingFields.length > 0 ? `Fill in: ${missingFields.join(", ")}` :
            undefined
          }
          className="w-full py-3 bg-brand-green text-white font-semibold rounded-lg hover:bg-brand-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          {polling ? (
            <><Loader2 className="w-5 h-5 animate-spin" /> Running agents…</>
          ) : (
            "Run All AI Agents"
          )}
        </button>
        {!polling && (!hasLlm || missingFields.length > 0) && (
          <p className="mt-2 text-xs text-amber-600">
            {!hasLlm
              ? "Add your Groq or OpenAI API key in the sidebar to enable this button."
              : `Required: ${missingFields.join(", ")}`}
          </p>
        )}

        {/* Progress log */}
        {(task || polling) && (
          <div className="mt-5">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Progress</h4>
            <div className="space-y-2">
              {allNodes.map((node) => {
                const done = completedNodes.includes(node);
                const isCurrentlyRunning = polling && !done && completedNodes.length > 0
                  && allNodes.indexOf(node) === completedNodes.length;
                return (
                  <div key={node} className="flex items-center gap-3 text-sm">
                    {done ? (
                      <span className="w-4 h-4 rounded-full bg-brand-green flex-shrink-0" />
                    ) : isCurrentlyRunning ? (
                      <Loader2 className="w-4 h-4 text-amber-500 animate-spin flex-shrink-0" />
                    ) : (
                      <span className="w-4 h-4 rounded-full border-2 border-gray-300 flex-shrink-0" />
                    )}
                    <span className={clsx(done ? "text-gray-800" : "text-gray-400")}>
                      {NODE_LABELS[node]}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {task?.status === "error" && (
          <div className="mt-3 bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
            {task.error}
          </div>
        )}
      </SectionCard>

      {/* Review & Edit AI content */}
      {state.agent_ran && (
        <SectionCard title="Review & Edit AI-Generated Content">
          <p className="text-xs text-gray-400 mb-4">You can edit any AI-generated section below before exporting.</p>
          <div className="space-y-2">
            {REVIEWABLE_SECTIONS.map(({ key, label }) => {
              const isOpen = openSections.has(key);
              const value = (state as unknown as Record<string, string>)[key] ?? "";
              return (
                <div key={key} className="border border-gray-200 rounded-lg overflow-hidden">
                  <button
                    onClick={() => toggleSection(key)}
                    className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors text-sm font-medium text-gray-700"
                  >
                    <span>{label}</span>
                    <div className="flex items-center gap-2">
                      {value && <span className="text-xs text-brand-green font-normal">Generated</span>}
                      {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </div>
                  </button>
                  {isOpen && (
                    <div className="p-4">
                      <textarea
                        rows={8}
                        className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-green resize-y"
                        value={value}
                        onChange={(e) => setState({ [key]: e.target.value } as Parameters<typeof setState>[0])}
                      />
                      <button
                        onClick={() => handleRegen(key)}
                        disabled={regenLoading === key || !hasLlm}
                        className="mt-2 inline-flex items-center gap-1.5 text-xs text-brand-green hover:text-brand-dark font-medium px-3 py-1.5 rounded-md hover:bg-green-50 border border-green-200 disabled:opacity-50 transition-colors"
                      >
                        {regenLoading === key ? (
                          <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Regenerating…</>
                        ) : (
                          "Regenerate"
                        )}
                      </button>
                    </div>
                  )}
                </div>
              );
            })}

            {/* Comparable Descriptions — dict preview */}
            {(() => {
              const isOpen = openSections.has("comparable_descriptions");
              const descs = state.comparable_descriptions ?? {};
              const entries = Object.entries(descs);
              return (
                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <button
                    onClick={() => toggleSection("comparable_descriptions")}
                    className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors text-sm font-medium text-gray-700"
                  >
                    <span>Comparable Companies Descriptions</span>
                    <div className="flex items-center gap-2">
                      {entries.length > 0 && <span className="text-xs text-brand-green font-normal">Generated ({entries.length})</span>}
                      {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </div>
                  </button>
                  {isOpen && (
                    <div className="p-4 space-y-4">
                      {entries.length === 0 ? (
                        <p className="text-sm text-gray-400 italic">No descriptions generated yet.</p>
                      ) : (
                        entries.map(([name, desc]) => (
                          <div key={name}>
                            <p className="text-xs font-semibold text-gray-600 mb-1">{name}</p>
                            <textarea
                              rows={4}
                              className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-green resize-y"
                              value={desc}
                              onChange={(e) =>
                                setState({
                                  comparable_descriptions: { ...state.comparable_descriptions, [name]: e.target.value },
                                })
                              }
                            />
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </div>
              );
            })()}
          </div>
        </SectionCard>
      )}
    </div>
  );
}
