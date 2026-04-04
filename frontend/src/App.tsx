import React, { useEffect, useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Sidebar } from "./components/Sidebar";
import { ProjectDashboard } from "./pages/ProjectDashboard";
import { Step0Upload } from "./pages/Step0Upload";
import { Step1CompanyIdentity } from "./pages/Step1CompanyIdentity";
import { Step2Ownership } from "./pages/Step2Ownership";
import { Step3AffiliatedParties } from "./pages/Step3AffiliatedParties";
import { Step4BusinessActivities } from "./pages/Step4BusinessActivities";
import { Step5Transactions } from "./pages/Step5Transactions";
import { Step6FinancialData } from "./pages/Step6FinancialData";
import { Step7ComparableCompanies } from "./pages/Step7ComparableCompanies";
import { Step8TPAnalysis } from "./pages/Step8TPAnalysis";
import { Step9NonFinancial } from "./pages/Step9NonFinancial";
import { Step10AIAgents } from "./pages/Step10AIAgents";
import { Step11ReviewExport } from "./pages/Step11ReviewExport";
import { useProjectStore } from "./store/projectStore";
import { saveProject, getProject } from "./api/projects";
import { Component as LumaSpin } from "@/components/ui/luma-spin";

const queryClient = new QueryClient();

const STEP_COMPONENTS = [
  Step0Upload,
  Step1CompanyIdentity,
  Step2Ownership,
  Step3AffiliatedParties,
  Step4BusinessActivities,
  Step5Transactions,
  Step6FinancialData,
  Step7ComparableCompanies,
  Step8TPAnalysis,
  Step9NonFinancial,
  Step10AIAgents,
  Step11ReviewExport,
];

const TOTAL_STEPS = STEP_COMPONENTS.length;

type View = "loading" | "dashboard" | "wizard";

function AppInner() {
  const {
    projectId,
    state,
    isDirty,
    setProjectId,
    setFullState,
    setState,
    setStep,
    markClean,
    reset,
  } = useProjectStore();
  const [view, setView] = useState<View>("loading");
  const [saving, setSaving] = useState(false);
  const [stepErrors, setStepErrors] = useState<string[]>([]);

  // Init: try to restore last project from localStorage, else show dashboard
  useEffect(() => {
    const stored = localStorage.getItem("tp_project_id");
    const init = async () => {
      if (stored) {
        try {
          const proj = await getProject(stored);
          setProjectId(proj.id);
          setFullState(proj.state);
          setView("wizard");
          return;
        } catch {
          localStorage.removeItem("tp_project_id");
        }
      }
      setView("dashboard");
    };
    init();
  }, []);

  // Auto-save when dirty
  useEffect(() => {
    if (!isDirty || !projectId || view !== "wizard") return;
    const t = setTimeout(async () => {
      setSaving(true);
      try {
        await saveProject(projectId, { state });
        markClean();
      } catch {
        /* ignore */
      }
      setSaving(false);
    }, 1500);
    return () => clearTimeout(t);
  }, [isDirty, state]);

  const handleProjectSelected = () => {
    setView("wizard");
  };

  const handleBackToDashboard = () => {
    reset();
    localStorage.removeItem("tp_project_id");
    setView("dashboard");
  };

  const validateStep = (step: number): string[] => {
    if (step === 1) {
      const errs: string[] = [];
      if (!state.company_name.trim())
        errs.push("Full Company Name is required");
      if (!state.company_short_name.trim())
        errs.push("Short Name / Abbreviation is required");
      if (!state.fiscal_year.trim()) errs.push("Fiscal Year is required");
      return errs;
    }
    if (step === 5) {
      if (!state.transaction_details_text.trim())
        return ["Transaction Details are required"];
    }
    return [];
  };

  const goTo = (step: number) => {
    const errs = validateStep(state.step);
    if (step > state.step && errs.length) {
      setStepErrors(errs);
      return;
    }
    setStepErrors([]);
    setStep(step);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const loadDummy = async () => {
    try {
      const { DUMMY_DATA } = await import("./dummyData");
      setState(DUMMY_DATA as Parameters<typeof setState>[0]);
    } catch {
      alert("Dummy data not available.");
    }
  };

  if (view === "loading") {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-3">
          <LumaSpin />
          <p className="text-sm text-gray-500">Loading…</p>
        </div>
      </div>
    );
  }

  if (view === "dashboard") {
    return <ProjectDashboard onProjectSelected={handleProjectSelected} />;
  }

  const StepComponent = STEP_COMPONENTS[state.step];
  const canGoBack = state.step > 0;
  const canGoNext = state.step < TOTAL_STEPS - 1;

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar
        onLoadDummy={loadDummy}
        onBackToDashboard={handleBackToDashboard}
      />

      {/* Main content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Top bar */}
        <div className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between sticky top-0 z-10">
          <div className="text-sm text-gray-500">
            {state.company_short_name && (
              <span className="font-medium text-gray-700">
                {state.company_short_name}
              </span>
            )}
            {state.company_short_name && state.fiscal_year && " · "}
            {state.fiscal_year && `FY ${state.fiscal_year}`}
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-400">
            {saving && (
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                Saving…
              </span>
            )}
            {!saving && !isDirty && projectId && (
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-green" />
                Saved
              </span>
            )}
          </div>
        </div>

        {/* Step content */}
        <div className="flex-1 px-8 py-6 max-w-5xl w-full mx-auto">
          {stepErrors.length > 0 && (
            <div className="mb-4 rounded-lg bg-red-50 border border-red-200 px-4 py-3 space-y-1">
              {stepErrors.map((e) => (
                <p key={e} className="text-sm text-red-700">
                  {e}
                </p>
              ))}
            </div>
          )}

          <StepComponent />
        </div>

        {/* Navigation footer */}
        <div className="bg-white border-t border-gray-200 px-8 py-4 flex items-center justify-between sticky bottom-0">
          <button
            onClick={() => goTo(state.step - 1)}
            disabled={!canGoBack}
            className="flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-brand-grey border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Previous
          </button>

          <span className="text-xs text-gray-400">
            Step {state.step + 1} of {TOTAL_STEPS}
          </span>

          <button
            onClick={() => goTo(state.step + 1)}
            disabled={!canGoNext}
            className="flex items-center gap-2 px-5 py-2.5 text-sm font-medium bg-brand-green text-white rounded-lg hover:bg-brand-dark disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppInner />
    </QueryClientProvider>
  );
}
