import { create } from "zustand";
import type { ProjectState, ApiSettings } from "../types";

const DEFAULT_STATE: ProjectState = {
  step: 0,
  uploaded_docs_processed: false,
  doc_extraction_result: {},
  company_name: "",
  company_short_name: "",
  company_address: "",
  establishment_info: "",
  fiscal_year: "2024",
  parent_company: "",
  parent_group: "",
  brand_name: "",
  shareholders: [{ name: "", shares: "", capital: "", percentage: "" }],
  shareholders_source: "",
  management: [{ position: "", name: "" }],
  management_source: "",
  employee_count: "",
  affiliated_parties: [{ name: "", country: "", relationship: "", transaction_type: "" }],
  business_activities_description: "",
  products: [{ name: "", description: "" }],
  business_strategy: "",
  business_restructuring: "",
  business_characterization_text: "",
  org_structure_description: "",
  org_structure_departments: [{ name: "", head: "", employees: "" }],
  transaction_type: "Purchase of tangible goods",
  transaction_details_text: "",
  pricing_policy: "",
  affiliated_transactions: [{ name: "", country: "", affiliation_type: "", transaction_type: "", value: "", note: "" }],
  independent_transactions: [{ name: "", country: "", transaction_type: "", value: "" }],
  financial_data: {},
  financial_data_prior: {},
  comparability_factors: [
    { factor: "Contract Terms and Conditions", description: "" },
    { factor: "Product Characteristics",       description: "" },
    { factor: "Functional Analysis",           description: "" },
    { factor: "Business Strategy",             description: "" },
    { factor: "Economic Conditions",           description: "" },
  ],
  search_criteria_results: [
    { step: "1", criteria: "All companies in scope", result_count: "" },
    { step: "2", criteria: "Status: Active", result_count: "" },
    { step: "3", criteria: "Geographic region", result_count: "" },
    { step: "4", criteria: "Independence indicator: A+, A, A-", result_count: "" },
    { step: "5", criteria: "Years with available accounts", result_count: "" },
    { step: "6", criteria: "Industry classification (SIC/NACE/NAICS)", result_count: "" },
    { step: "7", criteria: "Companies with overview information", result_count: "" },
  ],
  rejection_matrix: [{ name: "", limited_financial_statement: false, negative_margin: false, consolidated_financial_statement: false, different_main_activity: false, non_comparable_line_of_business: false, limited_information_website: false, accepted: false }],
  comparable_companies: [{ name: "", country: "", description: "", ros_data: "" }],
  selected_method: "TNMM",
  selected_pli: "ROS",
  tested_party: "",
  analysis_period: "2020-2022",
  quartile_range: { q1: 0, median: 0, q3: 0 },
  tested_party_ratio: 0,
  non_financial_events: "",
  industry_analysis_global: "",
  industry_analysis_indonesia: "",
  company_location_analysis: "",
  company_location_sources: [],
  industry_regulations_text: "",
  industry_regulations_sources: [],
  business_environment_overview: "",
  business_environment_sources: [],
  executive_summary: "",
  conclusion_text: "",
  background_transaction: "",
  supply_chain_management: "",
  functional_analysis_narrative: "",
  method_selection_justification: "",
  pli_selection_rationale: "",
  comparability_analysis_narrative: "",
  pl_overview_text: "",
  comparable_descriptions: {},
  agent_ran: false,
  agent_errors: [],
};

const DEFAULT_API_SETTINGS: ApiSettings = {
  llm_provider: "groq",
  api_key: "",
  model: "llama-3.3-70b-versatile",
  tavily_key: "",
};

function sanitizeState(raw: Partial<ProjectState>): ProjectState {
  const merged = { ...DEFAULT_STATE, ...raw };
  // If a field that should be an array arrived as null/non-array, fall back to the default
  (Object.keys(DEFAULT_STATE) as (keyof ProjectState)[]).forEach((key) => {
    if (Array.isArray(DEFAULT_STATE[key]) && !Array.isArray((merged as Record<string, unknown>)[key])) {
      (merged as Record<string, unknown>)[key] = DEFAULT_STATE[key];
    }
  });
  return merged as ProjectState;
}

function loadSavedApiSettings(): ApiSettings {
  try {
    const raw = localStorage.getItem("tp_api_settings");
    if (raw) return { ...DEFAULT_API_SETTINGS, ...JSON.parse(raw) };
  } catch { /* ignore */ }
  return { ...DEFAULT_API_SETTINGS };
}

interface ProjectStore {
  projectId: string | null;
  state: ProjectState;
  apiSettings: ApiSettings;
  isDirty: boolean;

  setProjectId: (id: string) => void;
  setState: (updates: Partial<ProjectState>) => void;
  setFullState: (state: ProjectState) => void;
  setApiSettings: (updates: Partial<ApiSettings>) => void;
  setStep: (step: number) => void;
  markClean: () => void;
  reset: () => void;
}

export const useProjectStore = create<ProjectStore>((set) => ({
  projectId: null,
  state: { ...DEFAULT_STATE },
  apiSettings: loadSavedApiSettings(),
  isDirty: false,

  setProjectId: (id) => set({ projectId: id }),

  setState: (updates) =>
    set((s) => ({
      state: { ...s.state, ...updates },
      isDirty: true,
    })),

  setFullState: (newState) =>
    set({ state: sanitizeState(newState), isDirty: false }),

  setApiSettings: (updates) =>
    set((s) => ({
      apiSettings: { ...s.apiSettings, ...updates },
    })),

  setStep: (step) =>
    set((s) => ({
      state: { ...s.state, step },
      isDirty: true,
    })),

  markClean: () => set({ isDirty: false }),

  reset: () =>
    set({
      projectId: null,
      state: { ...DEFAULT_STATE },
      isDirty: false,
    }),
}));
