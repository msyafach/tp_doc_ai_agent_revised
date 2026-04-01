// ─── Domain types ─────────────────────────────────────────────────────────────

export interface Shareholder {
  name: string;
  shares: string;
  capital: string;
  percentage: string;
}

export interface Management {
  position: string;
  name: string;
}

export interface AffiliatedParty {
  name: string;
  country: string;
  relationship: string;
  transaction_type: string;
}

export interface Product {
  name: string;
  description: string;
}

export interface AffiliatedTransaction {
  name: string;
  country: string;
  affiliation_type: string;
  transaction_type: string;
  value: string;
  note: string;
}

export interface IndependentTransaction {
  name: string;
  country: string;
  transaction_type: string;
  value: string;
}

export interface FinancialData {
  sales?: string;
  cogs?: string;
  gross_profit?: string;
  gross_margin_pct?: string;
  operating_expenses?: string;
  operating_profit?: string;
  financial_income?: string;
  other_income?: string;
  other_expense?: string;
  income_before_tax?: string;
  income_tax?: string;
  net_income?: string;
  [key: string]: string | undefined;
}

export interface ComparableCompany {
  name: string;
  country: string;
  description: string;
  ros_data: string;
}

export interface SearchCriteriaResult {
  step: string;
  criteria: string;
  result_count: string;
}

export interface RejectionMatrixRow {
  name: string;
  limited_financial_statement: boolean;
  negative_margin: boolean;
  consolidated_financial_statement: boolean;
  different_main_activity: boolean;
  non_comparable_line_of_business: boolean;
  limited_information_website: boolean;
  accepted: boolean;
}

export interface QuartileRange {
  q1: number;
  median: number;
  q3: number;
}

export interface ComparabilityFactor {
  factor: string;
  description: string;
}

export interface OrgDepartment {
  name: string;
  head: string;
  employees: string;
}

// ─── Full project state ───────────────────────────────────────────────────────

export interface ProjectState {
  step: number;

  // Document upload
  uploaded_docs_processed: boolean;
  doc_extraction_result: Record<string, unknown>;

  // Company identity
  company_name: string;
  company_short_name: string;
  company_address: string;
  establishment_info: string;
  fiscal_year: string;
  parent_company: string;
  parent_group: string;
  brand_name: string;

  // Ownership & management
  shareholders: Shareholder[];
  shareholders_source: string;
  management: Management[];
  management_source: string;
  employee_count: string;

  // Affiliated parties
  affiliated_parties: AffiliatedParty[];

  // Business activities
  business_activities_description: string;
  products: Product[];
  business_strategy: string;
  business_restructuring: string;
  business_characterization_text: string;
  org_structure_description: string;
  org_structure_departments: OrgDepartment[];

  // Transactions
  transaction_type: string;
  transaction_details_text: string;
  pricing_policy: string;
  affiliated_transactions: AffiliatedTransaction[];
  independent_transactions: IndependentTransaction[];

  // Financial data
  financial_data: FinancialData;
  financial_data_prior: FinancialData;

  // Comparable companies
  comparability_factors: ComparabilityFactor[];
  search_criteria_results: SearchCriteriaResult[];
  rejection_matrix: RejectionMatrixRow[];
  comparable_companies: ComparableCompany[];

  // TP analysis parameters
  selected_method: string;
  selected_pli: string;
  tested_party: string;
  analysis_period: string;
  quartile_range: QuartileRange;
  tested_party_ratio: number;

  // Non-financial events
  non_financial_events: string;

  // AI-generated
  industry_analysis_global: string;
  industry_analysis_indonesia: string;
  company_location_analysis: string;
  company_location_sources: string[];
  industry_regulations_text: string;
  industry_regulations_sources: string[];
  business_environment_overview: string;
  business_environment_sources: string[];
  executive_summary: string;
  conclusion_text: string;
  background_transaction: string;
  supply_chain_management: string;
  functional_analysis_narrative: string;
  method_selection_justification: string;
  pli_selection_rationale: string;
  comparability_analysis_narrative: string;
  pl_overview_text: string;
  comparable_descriptions: Record<string, string>;
  agent_ran: boolean;
  agent_errors: string[];
}

// ─── API types ────────────────────────────────────────────────────────────────

export interface Project {
  id: string;
  name: string;
  state: ProjectState;
  created_at: string;
  updated_at: string;
}

export interface ProjectListItem {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface AgentTask {
  id: number;
  celery_task_id: string;
  task_type: string;
  status: "pending" | "running" | "success" | "error";
  progress_log: { node: string; label: string }[];
  result: Record<string, unknown> | null;
  error: string | null;
  created_at: string;
}

export interface AppConfig {
  TP_METHODS: string[];
  PLI_OPTIONS: Record<string, string>;
  TRANSACTION_TYPES: string[];
  BUSINESS_TYPES: string[];
}

// ─── API key / LLM settings ───────────────────────────────────────────────────

export interface ApiSettings {
  llm_provider: "groq" | "openai";
  api_key: string;
  model: string;
  tavily_key: string;
}
