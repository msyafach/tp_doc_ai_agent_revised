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
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Upload Documents</h1>
        <InfoBadge
          variant="optional"
          description="Upload company documents and let AI pre-fill the form. All uploads are processed locally."
        />
      </div>

      <SectionCard>
        <FileDropzone files={files} onChange={setFiles} />

        <div className="mt-4 flex items-center gap-3">
          <button
            onClick={handleProcess}
            disabled={validFiles.length === 0 || processing}
            className="px-5 py-2.5 bg-brand-green text-white rounded-lg font-medium text-sm hover:bg-brand-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {processing ? (
              <>
                <span className="animate-spin inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full" />
                Processing…
              </>
            ) : (
              "Process & Extract"
            )}
          </button>
          {task?.status === "success" && (
            <span className="text-sm text-brand-green">Extraction complete</span>
          )}
        </div>

        {log.length > 0 && (
          <div className="mt-3 bg-gray-50 rounded-lg p-3 text-sm font-mono text-gray-600 space-y-0.5">
            {log.map((l, i) => <div key={i}>{l}</div>)}
          </div>
        )}
      </SectionCard>

      {extraction && (
        <SectionCard title="Extraction Results — Review & Accept">
          <p className="text-sm text-gray-500 mb-4">
            Accept individual sections or click Accept All to pre-fill all form fields at once.
          </p>

          <div className="space-y-2">
            {SECTIONS.map((sec) => {
              const isOpen = openSections.has(sec.key);
              return (
                <div key={sec.key} className="border border-gray-200 rounded-lg overflow-hidden">
                  <button
                    onClick={() => toggleSection(sec.key)}
                    className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors text-sm font-medium text-gray-700"
                  >
                    <span>{sec.label}</span>
                    {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>

                  {isOpen && (
                    <div className="px-4 py-3 space-y-2">
                      {sec.stateKeys.map((k) => (
                        <div key={k}>
                          <span className="text-xs font-medium text-gray-500 uppercase">{k.replace(/_/g," ")}: </span>
                          <span className="text-sm text-gray-700">{previewValue(extraction[k])}</span>
                        </div>
                      ))}
                      <button
                        onClick={() => acceptSection(sec.stateKeys)}
                        className="mt-2 px-3 py-1.5 bg-brand-green text-white text-xs rounded-md hover:bg-brand-dark transition-colors"
                      >
                        Accept Section
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="mt-4 pt-4 border-t border-gray-100 flex items-center gap-3">
            <button
              onClick={acceptAll}
              className="px-5 py-2 bg-brand-green text-white rounded-lg font-medium text-sm hover:bg-brand-dark transition-colors"
            >
              Accept All Extracted Data
            </button>
            <span className="text-xs text-gray-400">Accepting pre-fills corresponding form fields. You can still edit them in each step.</span>
          </div>
        </SectionCard>
      )}
    </div>
  );
}
