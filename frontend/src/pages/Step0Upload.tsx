import React, { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { FileDropzone } from "../components/FileDropzone";
import { InfoBadge } from "../components/InfoBadge";
import { SectionCard } from "../components/SectionCard";
import { useProjectStore } from "../store/projectStore";
import { uploadDocuments, pollTaskStatus, getProject } from "../api/projects";
import type { AgentTask } from "../types";

interface FileItem { file: File; valid: boolean; sizeLabel: string; error?: string }

interface ExtractionSection {
  key: string;
  label: string;
  stateKeys: string[];
}

const SECTIONS: ExtractionSection[] = [
  { key: "identity",     label: "Company Identity",     stateKeys: ["company_name","company_short_name","company_address","establishment_info","fiscal_year","parent_company","parent_group"] },
  { key: "shareholders", label: "Shareholders",         stateKeys: ["shareholders"] },
  { key: "management",   label: "Management / Board",   stateKeys: ["management","employee_count"] },
  { key: "affiliated",   label: "Affiliated Parties",   stateKeys: ["affiliated_parties"] },
  { key: "business",     label: "Business Activities",  stateKeys: ["business_activities_description","business_strategy","business_restructuring"] },
  { key: "products",     label: "Products / Services",  stateKeys: ["products"] },
  { key: "transactions", label: "Transaction Details",  stateKeys: ["transaction_details_text","pricing_policy"] },
  { key: "financials",   label: "Financial Data",       stateKeys: ["financial_data","financial_data_prior"] },
];

function previewValue(val: unknown): string {
  if (val == null) return "Not found in documents";
  if (Array.isArray(val)) {
    return `${val.length} item(s): ${val.slice(0,3).map((v) => typeof v === "object" && v ? Object.values(v as Record<string,unknown>)[0] : v).join(", ")}`;
  }
  if (typeof val === "object") {
    return Object.entries(val as Record<string,unknown>).filter(([,v])=>v).slice(0,4).map(([k,v])=>`${k}: ${v}`).join(", ");
  }
  return String(val).slice(0,200);
}

export function Step0Upload() {
  const { projectId, apiSettings, setState, setFullState } = useProjectStore();
  const [files, setFiles] = useState<FileItem[]>([]);
  const [processing, setProcessing] = useState(false);
  const [task, setTask] = useState<AgentTask | null>(null);
  const [extraction, setExtraction] = useState<Record<string,unknown> | null>(null);
  const [openSections, setOpenSections] = useState<Set<string>>(new Set());
  const [log, setLog] = useState<string[]>([]);

  const validFiles = files.filter((f) => f.valid);

  const handleProcess = async () => {
    if (!projectId || validFiles.length === 0) return;
    setProcessing(true);
    setLog(["Uploading files…"]);

    try {
      const { task_id } = await uploadDocuments(projectId, validFiles.map((f) => f.file), apiSettings);
      setLog((l) => [...l, "Running AI extraction agent…"]);

      // Poll until done
      const poll = async (): Promise<void> => {
        const t = await pollTaskStatus(task_id);
        setTask(t);
        if (t.status === "success" || t.status === "error") {
          if (t.status === "success" && t.result) {
            const r = t.result as Record<string,unknown>;
            setExtraction((r.extraction as Record<string,unknown>) ?? null);
            setLog((l) => [...l, "Extraction complete!"]);
          } else {
            setLog((l) => [...l, `Error: ${t.error}`]);
          }
          return;
        }
        await new Promise((res) => setTimeout(res, 2000));
        return poll();
      };
      await poll();
    } catch (e: unknown) {
      setLog((l) => [...l, `${e instanceof Error ? e.message : "Unknown error"}`]);
    }
    setProcessing(false);
  };

  const acceptSection = (keys: string[]) => {
    if (!extraction) return;
    const updates: Record<string,unknown> = {};
    keys.forEach((k) => {
      if (extraction[k] != null && extraction[k] !== "") updates[k] = extraction[k];
    });
    setState(updates as Parameters<typeof setState>[0]);
  };

  const acceptAll = () => {
    if (!extraction) return;
    const allKeys = SECTIONS.flatMap((s) => s.stateKeys);
    acceptSection(allKeys);
  };

  const toggleSection = (key: string) => {
    setOpenSections((prev) => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-black text-gray-900 tracking-tight">Upload Documents</h1>
        <p className="text-gray-500 text-sm font-medium max-w-2xl leading-relaxed">
          Upload company legal documents, financial statements, and contracts. Our AI agent will automatically extract relevant transfer pricing information to pre-fill your local file.
        </p>
      </div>

      <SectionCard title="Source Documentation">
        <div className="mb-6">
          <FileDropzone files={files} onChange={setFiles} />
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-gray-50">
          <div className="flex items-center gap-3">
            <button
              onClick={handleProcess}
              disabled={validFiles.length === 0 || processing}
              className="px-8 py-3.5 bg-brand-green text-white rounded-xl font-bold text-sm hover:bg-brand-dark disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-lg shadow-brand-green/20 flex items-center gap-3 active:scale-95"
            >
              {processing ? (
                <>
                  <span className="animate-spin inline-block w-5 h-5 border-3 border-white/30 border-t-white rounded-full" />
                  ANALYZING DOCUMENTS...
                </>
              ) : (
                "PROCESS & EXTRACT DATA"
              )}
            </button>
            {task?.status === "success" && (
              <div className="flex items-center gap-2 text-sm font-bold text-brand-green bg-green-50 px-4 py-2 rounded-full border border-green-100 animate-in zoom-in-95">
                <span className="w-2 h-2 rounded-full bg-brand-green animate-pulse" />
                EXTRACTION COMPLETE
              </div>
            )}
          </div>
          
          <div className="text-[10px] font-black text-gray-300 uppercase tracking-widest text-right">
            SECURE LOCAL PROCESSING · GDPR COMPLIANT
          </div>
        </div>

        {log.length > 0 && (
          <div className="mt-6 bg-gray-900 rounded-xl p-5 shadow-inner border border-gray-800">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-1.5 h-1.5 rounded-full bg-brand-blue animate-pulse" />
              <span className="text-[10px] font-black text-brand-blue uppercase tracking-widest">AI Agent Activity Log</span>
            </div>
            <div className="space-y-1 font-mono text-xs text-gray-400">
              {log.map((l, i) => (
                <div key={i} className="flex gap-3">
                  <span className="text-gray-600">[{new Date().toLocaleTimeString([], {hour12:false})}]</span>
                  <span className={i === log.length - 1 ? "text-white font-bold" : ""}>{l}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </SectionCard>

      {extraction && (
        <SectionCard title="Extraction Results — Review & Accept">
          <div className="flex items-center justify-between mb-8">
            <p className="text-sm text-gray-500 font-medium leading-relaxed max-w-md">
              The AI has extracted the following data. Review each section carefully and accept them to populate your project fields.
            </p>
            <button
              onClick={acceptAll}
              className="px-6 py-3 bg-gray-900 text-white rounded-xl font-bold text-xs hover:bg-black transition-all shadow-xl shadow-gray-200 active:scale-95"
            >
              ACCEPT ALL EXTRACTED DATA
            </button>
          </div>

          <div className="grid gap-3">
            {SECTIONS.map((sec) => {
              const isOpen = openSections.has(sec.key);
              return (
                <div key={sec.key} className="group border-2 border-gray-50 rounded-2xl overflow-hidden transition-all hover:border-brand-blue/20">
                  <button
                    onClick={() => toggleSection(sec.key)}
                    className={clsx(
                      "w-full flex items-center justify-between px-6 py-4 transition-all text-sm font-bold uppercase tracking-wider",
                      isOpen ? "bg-brand-blue/5 text-brand-blue" : "bg-white text-gray-600 hover:bg-gray-50"
                    )}
                  >
                    <span className="flex items-center gap-3">
                      <div className={clsx(
                        "w-2 h-2 rounded-full transition-colors",
                        isOpen ? "bg-brand-blue" : "bg-gray-200 group-hover:bg-brand-blue/40"
                      )} />
                      {sec.label}
                    </span>
                    {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>

                  {isOpen && (
                    <div className="px-6 py-6 bg-white space-y-4 animate-in slide-in-from-top-2 duration-200">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
                        {sec.stateKeys.map((k) => (
                          <div key={k} className="flex flex-col gap-1 pb-3 border-b border-gray-50 last:border-0">
                            <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{k.replace(/_/g," ")}</span>
                            <span className="text-sm text-gray-800 font-medium leading-relaxed">{previewValue(extraction[k])}</span>
                          </div>
                        ))}
                      </div>
                      <div className="pt-4 flex justify-end">
                        <button
                          onClick={() => acceptSection(sec.stateKeys)}
                          className="px-5 py-2.5 bg-brand-green/10 text-brand-green text-[11px] font-black uppercase tracking-widest rounded-lg hover:bg-brand-green hover:text-white transition-all"
                        >
                          Accept Section
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </SectionCard>
      )}
    </div>
  );
}
