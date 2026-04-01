import React, { useRef, useState } from "react";
import { ChevronLeft, Settings } from "lucide-react";
import clsx from "clsx";
import { useProjectStore } from "../store/projectStore";
import { exportProjectJson, loadProjectJson } from "../api/projects";
import { SettingsModal } from "./SettingsModal";

const STEPS = [
  { label: "Upload Documents"      },
  { label: "Company Identity"       },
  { label: "Ownership & Mgmt"       },
  { label: "Affiliated Parties"     },
  { label: "Business Activities"    },
  { label: "Transactions"           },
  { label: "Financial Data"         },
  { label: "Comparable Companies"   },
  { label: "TP Analysis"            },
  { label: "Non-Financial Events"   },
  { label: "Run AI Agents"          },
  { label: "Review & Export"        },
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
      a.download = `tp_project.json`;
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
      <aside className="w-64 min-h-screen bg-brand-grey flex flex-col text-white overflow-y-auto">
        {/* Header */}
        <div className="px-4 pt-5 pb-4 border-b border-white/10">
          <div className="flex items-center gap-2 mb-2 p-2 bg-white rounded-lg inline-block">
            <img src="/rsm-logo.png" alt="RSM" className="h-8 w-auto" />
          </div>
          <span className="font-bold text-sm leading-tight block">TP Local File Generator</span>
          <p className="text-xs text-white/70 mt-0.5">PMK-172 · 2023 Compliant</p>
          <button
            onClick={onBackToDashboard}
            className="mt-3 flex items-center gap-1.5 text-xs text-white/60 hover:text-white transition-colors"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            Back to Projects
          </button>
        </div>

        {/* Progress */}
        <div className="px-4 py-3 border-b border-white/10">
          <div className="flex justify-between text-xs text-white/80 mb-1.5">
            <span>Step {currentStep + 1} of {STEPS.length}</span>
            <span>{Math.round(progress * 100)}%</span>
          </div>
          <div className="h-1.5 bg-white/20 rounded-full overflow-hidden">
            <div
              className="h-full bg-brand-blue rounded-full transition-all duration-300"
              style={{ width: `${progress * 100}%` }}
            />
          </div>
        </div>

        {/* Navigation */}
        <nav className="px-2 py-3 flex-1 space-y-0.5">
          {STEPS.map((step, idx) => {
            const isActive = idx === currentStep;
            const isDone = idx < currentStep;

            return (
              <button
                key={idx}
                onClick={() => setStep(idx)}
                className={clsx(
                  "w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left text-sm transition-all",
                  isActive
                    ? "bg-white text-brand-grey font-semibold shadow-sm"
                    : isDone
                    ? "text-white/90 hover:bg-white/10"
                    : "text-white/60 hover:bg-white/10 hover:text-white",
                )}
              >
                <span className="flex-1 leading-tight">{step.label}</span>
                {isDone && !isActive && (
                  <span className="w-2 h-2 rounded-full bg-brand-blue flex-shrink-0" />
                )}
              </button>
            );
          })}
        </nav>

        {/* Footer actions */}
        <div className="px-4 py-4 border-t border-white/10 space-y-2">
          {/* Settings button */}
          <button
            onClick={() => setShowSettings(true)}
            className="w-full flex items-center justify-center gap-2 text-xs bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg py-2 transition-colors"
          >
            <Settings className="w-3.5 h-3.5" />
            API Settings
          </button>

          <button
            onClick={handleSaveJson}
            className="w-full flex items-center justify-center text-xs bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg py-2 transition-colors"
          >
            Save Project JSON
          </button>

          <input
            ref={fileRef}
            type="file"
            accept=".json"
            className="hidden"
            onChange={handleLoadJson}
          />
          <button
            onClick={() => fileRef.current?.click()}
            className="w-full flex items-center justify-center text-xs bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg py-2 transition-colors"
          >
            Load Project JSON
          </button>

          <button
            onClick={onLoadDummy}
            className="w-full flex items-center justify-center text-xs bg-brand-blue/30 hover:bg-brand-blue/40 border border-brand-blue/50 text-white rounded-lg py-2 transition-colors"
          >
            Fill Dummy Data
          </button>
        </div>
      </aside>

      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
    </>
  );
}
