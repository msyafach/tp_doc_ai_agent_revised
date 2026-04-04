import React, { useRef, useState } from "react";
import { ChevronLeft, Settings } from "lucide-react";
import { useProjectStore } from "../store/projectStore";
import { exportProjectJson, loadProjectJson } from "../api/projects";
import { SettingsModal } from "./SettingsModal";
import {
  Sidebar as SidebarRoot,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarSeparator,
} from "@/components/ui/sidebar";

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
      <SidebarProvider defaultOpen>
        <SidebarRoot collapsible="none" className="w-64 min-h-screen border-r border-white/10 bg-brand-grey text-white">
          <SidebarHeader className="px-4 pb-4 pt-5">
            <div className="mb-2 inline-block rounded-lg bg-white p-2">
              <img src="/rsm-logo.png" alt="RSM" className="h-8 w-auto" />
            </div>
            <span className="block text-sm font-bold leading-tight">TP Local File Generator</span>
            <p className="mt-0.5 text-xs text-white/70">PMK-172 · 2023 Compliant</p>
            <button
              onClick={onBackToDashboard}
              className="mt-3 flex items-center gap-1.5 text-xs text-white/60 transition-colors hover:text-white"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
              Back to Projects
            </button>
          </SidebarHeader>

          <SidebarSeparator className="mx-0 bg-white/10" />

          <div className="px-4 py-3">
            <div className="mb-1.5 flex justify-between text-xs text-white/80">
              <span>
                Step {currentStep + 1} of {STEPS.length}
              </span>
              <span>{Math.round(progress * 100)}%</span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-white/20">
              <div className="h-full rounded-full bg-brand-blue transition-all duration-300" style={{ width: `${progress * 100}%` }} />
            </div>
          </div>

          <SidebarSeparator className="mx-0 bg-white/10" />

          <SidebarContent className="px-2 py-3">
            <SidebarGroup className="p-0">
              <SidebarGroupLabel className="sr-only">Steps</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu className="gap-0.5">
                  {STEPS.map((step, idx) => {
                    const isActive = idx === currentStep;
                    const isDone = idx < currentStep;

                    return (
                      <SidebarMenuItem key={idx}>
                        <SidebarMenuButton
                          onClick={() => setStep(idx)}
                          isActive={isActive}
                          className={
                            isActive
                              ? "bg-white font-semibold text-brand-grey shadow-sm hover:bg-white"
                              : isDone
                                ? "text-white/90 hover:bg-white/10"
                                : "text-white/60 hover:bg-white/10 hover:text-white"
                          }
                        >
                          <span className="flex-1 leading-tight">{step.label}</span>
                          {isDone && !isActive && <SidebarMenuBadge className="bg-brand-blue text-transparent">•</SidebarMenuBadge>}
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    );
                  })}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>

          <SidebarSeparator className="mx-0 bg-white/10" />

          <SidebarFooter className="space-y-2 px-4 py-4">
            <button
              onClick={() => setShowSettings(true)}
              className="flex w-full items-center justify-center gap-2 rounded-lg border border-white/20 bg-white/10 py-2 text-xs transition-colors hover:bg-white/20"
            >
              <Settings className="h-3.5 w-3.5" />
              API Settings
            </button>

            <button
              onClick={handleSaveJson}
              className="w-full rounded-lg border border-white/20 bg-white/10 py-2 text-xs transition-colors hover:bg-white/20"
            >
              Save Project JSON
            </button>

            <input ref={fileRef} type="file" accept=".json" className="hidden" onChange={handleLoadJson} />
            <button
              onClick={() => fileRef.current?.click()}
              className="w-full rounded-lg border border-white/20 bg-white/10 py-2 text-xs transition-colors hover:bg-white/20"
            >
              Load Project JSON
            </button>

            <button
              onClick={onLoadDummy}
              className="w-full rounded-lg border border-brand-blue/50 bg-brand-blue/30 py-2 text-xs text-white transition-colors hover:bg-brand-blue/40"
            >
              Fill Dummy Data
            </button>
          </SidebarFooter>
        </SidebarRoot>
      </SidebarProvider>

      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
    </>
  );
}
