import React from "react";
import { DynamicTable } from "../components/DynamicTable";
import { InfoBadge } from "../components/InfoBadge";
import { SectionCard } from "../components/SectionCard";
import { useProjectStore } from "../store/projectStore";
import type { ComparabilityFactor, SearchCriteriaResult, ComparableCompany, RejectionMatrixRow } from "../types";

export function Step7ComparableCompanies() {
  const { state, setState } = useProjectStore();

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Comparable Companies</h1>
        <InfoBadge variant="manual" description="Enter data from Bureau Van Dijk TP Catalyst Database" />
      </div>

      {/* Table 5.1: Comparability Analysis Factors */}
      <SectionCard>
        <div className="mb-3">
          <h3 className="font-semibold text-gray-800">Table 5.1 — Comparability Analysis Factors</h3>
          <p className="text-xs text-gray-500 mt-1">
            Describe each comparability factor's relevance for the affiliated-party transactions being analyzed.
          </p>
          <p className="text-sm text-gray-700 mt-1 font-medium">
            Comparability Analysis of {state.company_short_name || "[Company]"} Affiliated Transactions FY {state.fiscal_year}
          </p>
        </div>
        <DynamicTable<ComparabilityFactor>
          rows={state.comparability_factors}
          onChange={(rows) => setState({ comparability_factors: rows })}
          addLabel="Add Comparability Factor"
          columns={[
            { key: "factor",      label: "Comparability Factor", placeholder: "e.g., Contract Terms and Conditions" },
            { key: "description", label: "Description",          placeholder: "Describe relevance...", type: "textarea" },
          ]}
        />
      </SectionCard>

      {/* Search Criteria */}
      <SectionCard title="Search Criteria Results">
        <p className="text-xs text-gray-500 mb-3">Enter the step-by-step search funnel from your BvD database search</p>
        <DynamicTable<SearchCriteriaResult>
          rows={state.search_criteria_results}
          onChange={(rows) => setState({ search_criteria_results: rows })}
          addLabel="Add Search Step"
          columns={[
            { key: "step",         label: "Step",     placeholder: "1", width: "60px" },
            { key: "criteria",     label: "Criteria", placeholder: "e.g., All companies in scope" },
            { key: "result_count", label: "Result",   placeholder: "e.g., 3,500", width: "120px" },
          ]}
        />
      </SectionCard>

      {/* Rejection Matrix */}
      <SectionCard title="Manual Review — Rejection Matrix">
        <p className="text-xs text-gray-500 mb-3">
          Companies reviewed and rejected after manual inspection. Tick the reason for rejection, or tick "Accepted" for selected comparables.
        </p>

        {/* Column headers */}
        <div className="overflow-x-auto">
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="bg-gray-800 text-white">
                <th className="px-2 py-2 text-left border border-gray-600 w-6">No.</th>
                <th className="px-2 py-2 text-left border border-gray-600 min-w-[160px]">Company Name</th>
                <th className="px-2 py-2 text-center border border-gray-600 w-20">Limited Financial Statement</th>
                <th className="px-2 py-2 text-center border border-gray-600 w-20">Negative Margin</th>
                <th className="px-2 py-2 text-center border border-gray-600 w-20">Consolidated Financial Statement</th>
                <th className="px-2 py-2 text-center border border-gray-600 w-20">Different Main Activity</th>
                <th className="px-2 py-2 text-center border border-gray-600 w-20">Non-Comparable Line of Business</th>
                <th className="px-2 py-2 text-center border border-gray-600 w-20">Limited Information (Website)</th>
                <th className="px-2 py-2 text-center border border-gray-600 w-20 bg-green-700">Accepted Comparables</th>
                <th className="px-2 py-2 border border-gray-600 w-8"></th>
              </tr>
            </thead>
            <tbody>
              {state.rejection_matrix.map((row, idx) => (
                <tr key={idx} className={idx % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                  <td className="px-2 py-1 text-center border border-gray-200 text-gray-500">{idx + 1}</td>
                  <td className="px-2 py-1 border border-gray-200">
                    <input
                      type="text"
                      className="w-full text-xs border-0 bg-transparent focus:outline-none focus:ring-1 focus:ring-brand-green rounded px-1"
                      placeholder="Company name..."
                      value={row.name}
                      onChange={(e) => {
                        const updated = [...state.rejection_matrix];
                        updated[idx] = { ...updated[idx], name: e.target.value };
                        setState({ rejection_matrix: updated });
                      }}
                    />
                  </td>
                  {(["limited_financial_statement","negative_margin","consolidated_financial_statement","different_main_activity","non_comparable_line_of_business","limited_information_website","accepted"] as const).map((field) => (
                    <td key={field} className={`px-2 py-1 text-center border border-gray-200 ${field === "accepted" ? "bg-green-50" : ""}`}>
                      <input
                        type="checkbox"
                        className={`w-4 h-4 rounded cursor-pointer ${field === "accepted" ? "accent-green-600" : "accent-blue-600"}`}
                        checked={!!row[field]}
                        onChange={(e) => {
                          const updated = [...state.rejection_matrix];
                          updated[idx] = { ...updated[idx], [field]: e.target.checked };
                          setState({ rejection_matrix: updated });
                        }}
                      />
                    </td>
                  ))}
                  <td className="px-2 py-1 text-center border border-gray-200">
                    <button
                      onClick={() => {
                        const updated = state.rejection_matrix.filter((_, i) => i !== idx);
                        setState({ rejection_matrix: updated });
                      }}
                      className="text-red-400 hover:text-red-600 text-xs font-bold"
                    >✕</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <button
          onClick={() => setState({
            rejection_matrix: [
              ...state.rejection_matrix,
              { name: "", limited_financial_statement: false, negative_margin: false, consolidated_financial_statement: false, different_main_activity: false, non_comparable_line_of_business: false, limited_information_website: false, accepted: false },
            ],
          })}
          className="mt-3 inline-flex items-center gap-1 text-xs text-brand-green hover:text-brand-dark font-medium px-3 py-1.5 rounded-md border border-green-200 hover:bg-green-50 transition-colors"
        >
          + Add Company
        </button>
      </SectionCard>

      {/* Selected Comparable Companies */}
      <SectionCard title="Selected Comparable Companies">
        <p className="text-xs text-gray-500 mb-3">Final list of comparable companies after manual selection</p>
        <DynamicTable<ComparableCompany>
          rows={state.comparable_companies}
          onChange={(rows) => setState({ comparable_companies: rows })}
          addLabel="Add Comparable Company"
          columns={[
            { key: "name",        label: "Company Name",        placeholder: "e.g., PT XYZ" },
            { key: "country",     label: "Country",             placeholder: "Indonesia", width: "120px" },
            { key: "description", label: "Business Description", placeholder: "e.g., Heavy equipment distributor" },
            { key: "ros_data",    label: "ROS / Margin (%)",    placeholder: "e.g., 3.2", width: "130px" },
          ]}
        />
      </SectionCard>
    </div>
  );
}
