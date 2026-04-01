import React from "react";
import { FormField } from "../components/FormField";
import { InfoBadge } from "../components/InfoBadge";
import { SectionCard } from "../components/SectionCard";
import { useProjectStore } from "../store/projectStore";

const PL_ITEMS: { key: string; label: string }[] = [
  { key: "sales",             label: "Sales / Revenue" },
  { key: "cogs",              label: "Cost of Goods Sold" },
  { key: "gross_profit",      label: "Gross Profit" },
  { key: "gross_margin_pct",  label: "Gross Profit Margin (%)" },
  { key: "operating_expenses",label: "Operating Expenses" },
  { key: "operating_profit",  label: "Operating Profit" },
  { key: "financial_income",  label: "Financial Income / (Expenses)" },
  { key: "other_income",      label: "Other Income" },
  { key: "other_expense",     label: "Other Expense" },
  { key: "income_before_tax", label: "Income Before Tax" },
  { key: "income_tax",        label: "Income Tax" },
  { key: "net_income",        label: "Net Income" },
];

export function Step6FinancialData() {
  const { state, setState } = useProjectStore();
  const fy = state.fiscal_year || "Current Year";
  const priorFy = isNaN(Number(fy)) ? "Prior Year" : String(Number(fy) - 1);

  const updateCurrent = (key: string, val: string) =>
    setState({ financial_data: { ...state.financial_data, [key]: val } });

  const updatePrior = (key: string, val: string) =>
    setState({ financial_data_prior: { ...state.financial_data_prior, [key]: val } });

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Financial Data</h1>
        <InfoBadge variant="manual" description="Enter Profit & Loss data for current and prior year" />
      </div>

      <SectionCard>
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-gray-700 mb-4 pb-2 border-b border-gray-100">FY {fy}</h3>
            <div className="space-y-3">
              {PL_ITEMS.map(({ key, label }) => (
                <FormField
                  key={key}
                  label={label}
                  value={state.financial_data[key] ?? ""}
                  onChange={(v) => updateCurrent(key, v)}
                  placeholder="e.g., 150,000,000,000"
                />
              ))}
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-gray-700 mb-4 pb-2 border-b border-gray-100">FY {priorFy}</h3>
            <div className="space-y-3">
              {PL_ITEMS.map(({ key, label }) => (
                <FormField
                  key={key}
                  label={label}
                  value={state.financial_data_prior[key] ?? ""}
                  onChange={(v) => updatePrior(key, v)}
                  placeholder="e.g., 130,000,000,000"
                />
              ))}
            </div>
          </div>
        </div>
      </SectionCard>
    </div>
  );
}
