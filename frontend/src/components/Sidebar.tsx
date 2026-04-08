import React, { useRef, useState } from "react";
import { ChevronLeft, Settings } from "lucide-react";
import { useProjectStore } from "../store/projectStore";
import { exportProjectJson, loadProjectJson } from "../api/projects";
import { SettingsModal } from "./SettingsModal";

const STEPS = [
  { label: "Upload Documents" },
  { label: "Company Identity" },
  { label: "Ownership & Mgmt" },
  { label: "Affiliated Parties" },
  { label: "Business Activities" },
  { label: "Transactions" },
  { label: "Financial Data" },
  { label: "Comparable Companies" },
  { label: "TP Analysis" },
  { label: "Non-Financial Events" },
  { label: "Run AI Agents" },
  { label: "Review & Export" },
];

interface Props {
  onLoadDummy: () => void;
  onBackToDashboard: () => void;
}

export function Sidebar({ onLoadDummy, onBackToDashboard }: Props) {
  const { projectId, state, setStep } = useProjectStore();
  const fileRef = useRef<HTMLInputElement>(null);
  const [showSettings, setShowSettings] = useState(false);

  const currentStep = state.step;
  const progress = currentStep / (STEPS.length - 1);

  const handleSaveJson = async () => {
    if (!projectId) return;
    try {
      const blob = await exportProjectJson(projectId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const co = state.company_short_name || "project";
      const fy = state.fiscal_year || "";
      a.download = `tp_project_${co}_${fy}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      const json = JSON.stringify(state, null, 2);
      const blob = new Blob([json], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "tp_project.json";
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const handleLoadJson = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !projectId) return;
    try {
      await loadProjectJson(projectId, file);
      window.location.reload();
    } catch {
      alert("Failed to load JSON.");
    }
    e.target.value = "";
  };

  return (
    <>
      <aside className="flex w-72 flex-shrink-0 flex-col h-screen border-r border-gray-200 bg-white text-gray-700">
        {/* Header */}
        <div className="px-6 pb-6 pt-8 bg-gray-50/50">
          <div className="mb-6">
            <img src="/rsm-logo.png" alt="RSM Logo" className="h-10 w-auto object-contain" />
          </div>
          <h1 className="text-lg font-bold text-gray-900 leading-tight">RSM AI Tax Platform</h1>
          <p className="mt-1 text-xs font-medium text-brand-green uppercase tracking-wider">PMK-172 · 2023 Compliant</p>
          <button
            onClick={onBackToDashboard}
            className="mt-4 flex items-center gap-1.5 text-xs font-medium text-gray-500 transition-colors hover:text-brand-blue"
          >
            <ChevronLeft className="h-4 w-4" />
            Back to Project Dashboard
          </button>
        </div>

        <div className="h-px bg-gray-200" />

        {/* Progress */}
        <div className="px-6 py-5">
          <div className="mb-2 flex justify-between items-end text-xs font-semibold uppercase tracking-tight">
            <span className="text-gray-500">Progress</span>
            <span className="text-brand-blue">{Math.round(progress * 100)}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-gray-100">
            <div
              className="h-full rounded-full bg-brand-blue transition-all duration-500 ease-out shadow-[0_0_8px_rgba(0,149,214,0.3)]"
              style={{ width: `${progress * 100}%` }}
            />
          </div>
          <p className="mt-2 text-[10px] text-gray-400 font-medium">
            STEP {currentStep + 1} OF {STEPS.length}: {STEPS[currentStep].label.toUpperCase()}
          </p>
        </div>

        <div className="h-px bg-gray-200" />

        {/* Step list */}
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          <ul className="flex flex-col gap-1">
            {STEPS.map((step, idx) => {
              const isActive = idx === currentStep;
              const isDone = idx < currentStep;

              return (
                <li key={idx}>
                  <button
                    onClick={() => setStep(idx)}
                    className={[
                      "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition-all duration-200",
                      isActive
                        ? "bg-brand-green/10 text-brand-green font-bold shadow-sm ring-1 ring-brand-green/20"
                        : isDone
                          ? "text-gray-600 hover:bg-gray-50 font-medium"
                          : "text-gray-400 hover:bg-gray-50 hover:text-gray-600",
                    ].join(" ")}
                  >
                    <div className={[
                      "flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-bold transition-colors",
                      isActive
                        ? "bg-brand-green text-white"
                        : isDone
                          ? "bg-brand-blue/10 text-brand-blue"
                          : "bg-gray-100 text-gray-400"
                    ].join(" ")}>
                      {isDone && !isActive ? "✓" : idx + 1}
                    </div>
                    <span className="flex-1 leading-tight">{step.label}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="h-px bg-gray-200" />

        {/* Footer actions */}
        <div className="space-y-2 px-4 py-6 bg-gray-50/50">
          <button
            onClick={() => setShowSettings(true)}
            className="flex w-full items-center justify-center gap-2 rounded-lg border border-gray-200 bg-white py-2 text-xs font-semibold text-gray-600 transition-all hover:bg-gray-50 hover:border-gray-300 hover:shadow-sm"
          >
            <Settings className="h-3.5 w-3.5" />
            API Settings
          </button>

          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={handleSaveJson}
              className="rounded-lg border border-gray-200 bg-white py-2 text-[10px] font-bold text-gray-600 uppercase tracking-tight transition-all hover:bg-gray-50 hover:border-gray-300"
            >
              Export JSON
            </button>

            <button
              onClick={() => fileRef.current?.click()}
              className="rounded-lg border border-gray-200 bg-white py-2 text-[10px] font-bold text-gray-600 uppercase tracking-tight transition-all hover:bg-gray-50 hover:border-gray-300"
            >
              Import JSON
            </button>
            <input ref={fileRef} type="file" accept=".json" className="hidden" onChange={handleLoadJson} />
          </div>

          <button
            onClick={onLoadDummy}
            className="w-full rounded-lg bg-gray-800 py-2.5 text-[10px] font-bold text-white uppercase tracking-wider transition-all hover:bg-gray-900 shadow-md active:scale-[0.98]"
          >
            Fill Sample Data
          </button>
        </div>
      </aside>

      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
    </>
  );
}
