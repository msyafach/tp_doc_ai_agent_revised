import React, { useState } from "react";
import { Loader2 } from "lucide-react";
import { InfoBadge } from "../components/InfoBadge";
import { SectionCard } from "../components/SectionCard";
import { useProjectStore } from "../store/projectStore";
import { exportDocx } from "../api/projects";
import clsx from "clsx";

interface CheckItem { label: string; ok: boolean }

const SECTION_STATUS: { label: string; key: string; source: string }[] = [
  { label: "Cover Page",               key: "",                         source: "Template" },
  { label: "Glossary",                 key: "",                         source: "Template" },
  { label: "Statement Letter",         key: "",                         source: "Template" },
  { label: "Ch.1 Executive Summary",   key: "executive_summary",        source: "AI" },
  { label: "Ch.2 TP Regulations",      key: "",                         source: "Template" },
  { label: "Ch.3 Company Identity",    key: "company_name",             source: "Manual" },
  { label: "Ch.3 Business Environment",key: "business_environment_overview", source: "AI" },
  { label: "Ch.4 Transactions",        key: "transaction_details_text", source: "Manual" },
  { label: "Ch.4 Functional Analysis", key: "functional_analysis_narrative", source: "AI" },
  { label: "Ch.5 Industry Analysis",   key: "industry_analysis_global", source: "AI" },
  { label: "Ch.5 Method Selection",    key: "method_selection_justification", source: "AI" },
  { label: "Ch.5 Conclusion",          key: "conclusion_text",          source: "AI" },
  { label: "Ch.6 Financial Info",      key: "financial_data.sales",     source: "Manual" },
  { label: "Ch.7 Non-Financial Events",key: "",                         source: "Manual" },
  { label: "References",               key: "",                         source: "Template" },
  { label: "Appendices",               key: "",                         source: "Manual" },
];

export function Step11ReviewExport() {
  const { projectId, state } = useProjectStore();
  const [exporting, setExporting] = useState<"builder" | "template" | null>(null);

  const getVal = (key: string): unknown => {
    if (!key) return true;
    const parts = key.split(".");
    let val: unknown = state;
    for (const p of parts) {
      if (val == null || typeof val !== "object") return undefined;
      val = (val as Record<string, unknown>)[p];
    }
    return val;
  };

  const checks: CheckItem[] = [
    { label: "Company Identity",      ok: !!(state.company_name && state.company_short_name) },
    { label: "Ownership Structure",   ok: !!(state.shareholders[0]?.name) },
    { label: "Management",            ok: !!(state.management[0]?.name) },
    { label: "Affiliated Parties",    ok: !!(state.affiliated_parties[0]?.name) },
    { label: "Business Activities",   ok: !!state.business_activities_description },
    { label: "Products",              ok: !!(state.products[0]?.name) },
    { label: "Transaction Details",   ok: !!state.transaction_details_text },
    { label: "Financial Data",        ok: !!state.financial_data?.sales },
    { label: "Comparable Companies",  ok: !!(state.comparable_companies[0]?.name) },
    { label: "TP Analysis Parameters",ok: !!(state.quartile_range?.q1) },
    { label: "AI Agents Run",         ok: state.agent_ran },
  ];

  const handleExport = async (type: "builder" | "template") => {
    if (!projectId) return;
    setExporting(type);
    try {
      const blob = await exportDocx(projectId, type);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const short = state.company_short_name || "project";
      const fy = state.fiscal_year || "";
      const suffix = type === "template" ? "_template" : "";
      a.download = `TP_LocalFile_${short}_${fy}${suffix}.docx`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      alert("Export failed. Check the backend logs.");
    }
    setExporting(null);
  };

  const passCount = checks.filter((c) => c.ok).length;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Review & Export Document</h1>
      </div>

      {/* Completeness check */}
      <SectionCard title="Completeness Check">
        <div className="mb-3">
          <span className={clsx("text-sm font-medium", passCount === checks.length ? "text-brand-green" : "text-amber-600")}>
            {passCount} / {checks.length} sections complete
          </span>
        </div>
        <div className="grid grid-cols-3 gap-2">
          {checks.map((c) => (
            <div
              key={c.label}
              className={clsx(
                "flex items-center gap-2 px-3 py-2 rounded-lg text-sm",
                c.ok ? "bg-green-50 text-brand-dark border border-green-200"
                     : "bg-amber-50 text-amber-700 border border-amber-200",
              )}
            >
              {c.label}
            </div>
          ))}
        </div>
      </SectionCard>

      {/* Document structure overview */}
      <SectionCard title="Document Structure">
        <div className="grid grid-cols-2 gap-1">
          {SECTION_STATUS.map((sec) => {
            const val = getVal(sec.key);
            const pending = sec.key && !val;
            return (
              <div key={sec.label} className="flex items-center justify-between text-sm px-3 py-1.5 rounded hover:bg-gray-50">
                <span className={clsx(pending ? "text-gray-400" : "text-gray-700")}>{sec.label}</span>
                <span className={clsx("text-xs font-medium", pending ? "text-gray-300" : "text-gray-500")}>
                  {pending ? "Pending" : sec.source}
                </span>
              </div>
            );
          })}
        </div>
      </SectionCard>

      {/* Export buttons */}
      <SectionCard title="Export Document">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <p className="text-xs text-gray-500">Recommended — builds full document from scratch using python-docx</p>
            <button
              onClick={() => handleExport("builder")}
              disabled={!!exporting}
              className="w-full flex items-center justify-center gap-2 py-3 bg-brand-green text-white font-semibold rounded-lg hover:bg-brand-dark disabled:opacity-50 transition-colors text-sm"
            >
              {exporting === "builder" ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Generating…</>
              ) : (
                "Export Full Document (.docx)"
              )}
            </button>
          </div>

          <div className="space-y-2">
            <p className="text-xs text-gray-500">Uses the master Word template with Jinja2 placeholders</p>
            <button
              onClick={() => handleExport("template")}
              disabled={!!exporting}
              className="w-full flex items-center justify-center gap-2 py-3 bg-white border-2 border-brand-green text-brand-green font-semibold rounded-lg hover:bg-green-50 disabled:opacity-50 transition-colors text-sm"
            >
              {exporting === "template" ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Rendering…</>
              ) : (
                "Export from Master Template (.docx)"
              )}
            </button>
          </div>
        </div>

        <div className="mt-4 rounded-lg bg-blue-50 border border-blue-100 px-4 py-3 text-xs text-blue-700">
          After downloading, open in Microsoft Word and press <strong>Ctrl+A → F9</strong> to refresh the Table of Contents page numbers.
        </div>
      </SectionCard>
    </div>
  );
}
