import React, { useEffect, useRef, useState } from 'react';
import { ChevronLeft } from 'lucide-react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Sidebar } from './components/Sidebar';
import { LoginPage } from './pages/LoginPage';
import { ProjectDashboard } from './pages/ProjectDashboard';
import { LandingPage } from './pages/LandingPage';
import { AdminUsersPage } from './pages/AdminUsersPage';
import { Step0Upload } from './pages/Step0Upload';
import { Step1CompanyIdentity } from './pages/Step1CompanyIdentity';
import { Step2Ownership } from './pages/Step2Ownership';
import { Step3AffiliatedParties } from './pages/Step3AffiliatedParties';
import { Step4BusinessActivities } from './pages/Step4BusinessActivities';
import { Step5Transactions } from './pages/Step5Transactions';
import { Step6FinancialData } from './pages/Step6FinancialData';
import { Step7ComparableCompanies } from './pages/Step7ComparableCompanies';
import { Step8TPAnalysis } from './pages/Step8TPAnalysis';
import { Step9NonFinancial } from './pages/Step9NonFinancial';
import { Step10AIAgents } from './pages/Step10AIAgents';
import { Step11ReviewExport } from './pages/Step11ReviewExport';
import { useProjectStore } from './store/projectStore';
import { useAuthStore } from './store/authStore';
import { saveProject, getProject } from './api/projects';
import { logoutApi } from './api/auth';
import { getSettingsStatusApi } from './api/settings';
import { Component as LumaSpin } from '@/components/ui/luma-spin';

const queryClient = new QueryClient();

const STEP_COMPONENTS = [
  Step0Upload, Step1CompanyIdentity, Step2Ownership, Step3AffiliatedParties,
  Step4BusinessActivities, Step5Transactions, Step6FinancialData,
  Step7ComparableCompanies, Step8TPAnalysis, Step9NonFinancial,
  Step10AIAgents, Step11ReviewExport,
];

const TOTAL_STEPS = STEP_COMPONENTS.length;
const INACTIVITY_MS = 15 * 60 * 1000;

type View = "loading" | "login" | "landing" | "dashboard" | "wizard" | "admin";

function AppInner() {
  const {
    projectId, state, isDirty,
    setProjectId, setFullState, setState, setStep, markClean, reset, setApiSettings,
    agentTaskId, agentPolling, setAgentPolling, setAgentTask,
  } = useProjectStore();

  const { isAuthenticated, user, refreshToken, logout: authLogout } = useAuthStore();
  const [view, setView] = useState<View>("loading");
  const [saving, setSaving] = useState(false);
  const [stepErrors, setStepErrors] = useState<string[]>([]);
  const inactivityTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Inactivity logout after 15 minutes ────────────────────────────────────
  useEffect(() => {
    if (!isAuthenticated) return;
    const resetTimer = () => {
      if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
      inactivityTimer.current = setTimeout(() => handleLogout(), INACTIVITY_MS);
    };
    const events = ["mousemove", "mousedown", "keydown", "touchstart", "scroll"];
    events.forEach((e) => window.addEventListener(e, resetTimer, { passive: true }));
    resetTimer();
    return () => {
      if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
      events.forEach((e) => window.removeEventListener(e, resetTimer));
    };
  }, [isAuthenticated]);

  // ── Init: restore project + load API settings from backend ──────────────────
  useEffect(() => {
    const stored = localStorage.getItem("tp_project_id");
    const init = async () => {
      if (isAuthenticated) {
        // Load API settings from backend (non-sensitive status for all users)
        getSettingsStatusApi()
          .then((s) => setApiSettings({
            llm_provider: s.llm_provider as "groq" | "openai",
            model: s.model,
            langsmith_project: s.langsmith_project,
            api_key: s.has_api_key ? "__configured__" : "",
            tavily_key: s.has_tavily_key ? "__configured__" : "",
            langsmith_api_key: s.has_langsmith_key ? "__configured__" : "",
          }))
          .catch(() => { /* ignore — defaults remain */ });

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
      } else {
        setView("landing");
      }
    };
    init();
  }, [isAuthenticated, setApiSettings, setProjectId, setFullState]);

  const handleLogin = () => {
    setView("dashboard");
  };

  const handleLogout = async () => {
    try {
      if (refreshToken) await logoutApi(refreshToken);
    } catch {
      /* ignore */
    }
    authLogout();
    reset();
    localStorage.removeItem("tp_project_id");
    setView("landing");
  };

  // ── Global agent polling — survives navigation ────────────────────────────
  useEffect(() => {
    if (!agentPolling || agentTaskId === null) return;
    let cancelled = false;

    const poll = async () => {
      while (!cancelled) {
        try {
          const { pollTaskStatus } = await import("./api/projects");
          const t = await pollTaskStatus(agentTaskId);
          setAgentTask(t);
          if (t.status === "success" || t.status === "error") {
            setAgentPolling(false);
            if (t.status === "success" && projectId) {
              const { getProject } = await import("./api/projects");
              const proj = await getProject(projectId);
              setFullState(proj.state);
            }
            return;
          }
        } catch { /* ignore transient errors */ }
        await new Promise((r) => setTimeout(r, 2000));
      }
    };
    poll();
    return () => { cancelled = true; };
  }, [agentPolling, agentTaskId]);

  // ── Auto-save when dirty ──────────────────────────────────────────────────
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
  }, [isDirty, state, view, projectId, markClean]);

  const handleProjectSelected = () => {
    setView("wizard");
  };

  const handleBackToDashboard = () => {
    reset();
    localStorage.removeItem("tp_project_id");
    setView("dashboard");
  };

  const handleLandingAction = () => {
    if (isAuthenticated) {
      setView("dashboard");
    } else {
      setView("login");
    }
  };

  const validateStep = (step: number): string[] => {
    if (step === 1) {
      const errs: string[] = [];
      if (!state.company_name.trim()) errs.push("Full Company Name is required");
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

  // ── Render ────────────────────────────────────────────────────────────────

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

  if (view === "landing") {
    return (
      <LandingPage
        onStart={handleLandingAction}
        onNewProject={handleLandingAction}
        companyName={state.company_short_name}
        isAuthenticated={isAuthenticated}
      />
    );
  }

  if (view === "login") {
    return <LoginPage onLogin={handleLogin} />;
  }

  if (view === "dashboard") {
    return (
      <ProjectDashboard
        onProjectSelected={handleProjectSelected}
        onLogout={handleLogout}
        isAdmin={user?.is_staff ?? false}
        username={user?.username ?? ""}
        onAdminClick={() => setView("admin")}
        onBackToLanding={() => setView("landing")}
      />
    );
  }

  // wizard + admin: shared layout with sidebar
  const StepComponent = STEP_COMPONENTS[state.step];
  const canGoBack = state.step > 0;
  const canGoNext = state.step < TOTAL_STEPS - 1;

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar
        onLoadDummy={loadDummy}
        onBackToDashboard={() => {
          reset(); localStorage.removeItem("tp_project_id"); setView("dashboard");
        }}
        onBackToLanding={() => setView("landing")}
        onLogout={handleLogout}
        onAdminClick={() => setView("admin")}
        onWizardClick={() => setView("wizard")}
        isAdmin={user?.is_staff ?? false}
        currentView={view === "admin" ? "admin" : "wizard"}
      />

      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top bar */}
        <div className="shrink-0 bg-white/80 backdrop-blur-md border-b border-gray-100 px-8 py-3 flex items-center justify-between z-10 shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
          {view === "admin" ? (
            <span className="text-sm font-semibold text-gray-700">User Management</span>
          ) : (
            (state.company_short_name || state.fiscal_year) && (
              <div className="flex items-center gap-2.5">
                {state.company_short_name && (
                  <span className="text-sm font-semibold text-gray-800 tracking-tight">
                    {state.company_short_name}
                  </span>
                )}
                {state.company_short_name && state.fiscal_year && (
                  <span className="text-gray-300 font-light">·</span>
                )}
                {state.fiscal_year && (
                  <span className="text-sm text-gray-400 font-medium">FY {state.fiscal_year}</span>
                )}
              </div>
            )
          )}
          <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest ml-auto">
            {agentPolling && (
              <span className="flex items-center gap-2 text-purple-600 bg-purple-50 px-3 py-1.5 rounded-full border border-purple-200 cursor-pointer" onClick={() => setStep(10)} title="Click to view progress">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse" /> AI Agents Running
              </span>
            )}
            {saving && (
              <span className="flex items-center gap-2 text-amber-500 bg-amber-50 px-3 py-1.5 rounded-full border border-amber-100">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" /> Auto-saving
              </span>
            )}
            {!saving && !isDirty && projectId && view === "wizard" && (
              <span className="flex items-center gap-2 text-brand-green bg-green-50 px-3 py-1.5 rounded-full border border-green-100">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-green" /> Synced
              </span>
            )}
          </div>
        </div>

        {/* Scrollable content */}
        <div className="flex-1 overflow-y-auto">
          {view === "admin" ? (
            <AdminUsersPage />
          ) : (
            <div className="px-8 py-10 max-w-5xl w-full mx-auto">
              {stepErrors.length > 0 && (
                <div className="mb-8 rounded-xl bg-red-50 border border-red-100 p-5 shadow-sm">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                    <h4 className="text-sm font-bold text-red-800 uppercase tracking-wider">
                      Validation Errors
                    </h4>
                  </div>
                  <ul className="space-y-1 list-disc list-inside">
                    {stepErrors.map((e) => (
                      <li key={e} className="text-sm text-red-700 font-medium">{e}</li>
                    ))}
                  </ul>
                </div>
              )}
              <div className="bg-white rounded-2xl border border-gray-100 shadow-xl shadow-gray-200/50 p-8 sm:p-10 min-h-[600px]">
                <StepComponent />
              </div>
            </div>
          )}
        </div>

        {/* Navigation footer — wizard only */}
        {view === "wizard" && (
          <div className="bg-white border-t border-gray-200 px-8 py-6 flex items-center justify-between shrink-0 z-10 shadow-[0_-4px_12px_rgba(0,0,0,0.03)]">
            <button
              onClick={() => goTo(state.step - 1)}
              disabled={!canGoBack}
              className="flex items-center gap-2 px-6 py-3 text-sm font-bold text-gray-600 border-2 border-gray-100 rounded-xl hover:bg-gray-50 hover:border-gray-200 disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-95"
            >
              <ChevronLeft className="w-4 h-4" /> PREVIOUS
            </button>

            <div className="flex flex-col items-center gap-1">
              <span className="text-[10px] font-black text-gray-300 uppercase tracking-[0.2em]">
                Progress
              </span>
              <div className="flex items-center gap-2">
                {[...Array(TOTAL_STEPS)].map((_, i) => (
                  <div
                    key={i}
                    className={[
                      "w-1.5 h-1.5 rounded-full transition-all duration-300",
                      i === state.step ? "bg-brand-blue w-4"
                        : i < state.step ? "bg-brand-green" : "bg-gray-200",
                    ].join(" ")}
                  />
                ))}
              </div>
            </div>

            <button
              onClick={() => goTo(state.step + 1)}
              disabled={!canGoNext}
              className="flex items-center gap-2 px-8 py-3 text-sm font-bold bg-brand-green text-white rounded-xl hover:bg-brand-dark shadow-lg shadow-brand-green/20 disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-95"
            >
              {state.step === TOTAL_STEPS - 1 ? "FINISH" : "NEXT STEP"}
            </button>
          </div>
        )}
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
