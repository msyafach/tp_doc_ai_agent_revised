import React from "react";
import { SelectField, FormField } from "../components/FormField";
import { InfoBadge } from "../components/InfoBadge";
import { SectionCard } from "../components/SectionCard";
import { useProjectStore } from "../store/projectStore";
import clsx from "clsx";

const TP_METHODS = ["CUP", "RPM", "CPM", "PSM", "TNMM"];
const PLI_OPTIONS: Record<string, string> = {
  "ROS":         "Return on Sales (Operating Profit / Sales)",
  "GPM":         "Gross Profit Margin (Gross Profit / Sales)",
  "Berry Ratio": "Berry Ratio (Gross Profit / Operating Expenses)",
  "NCPM":        "Net Cost Plus Markup (Operating Profit / Total Costs)",
  "ROA":         "Return on Assets (Operating Profit / Total Assets)",
  "ROCE":        "Return on Capital Employed",
};

export function Step8TPAnalysis() {
  const { state, setState } = useProjectStore();
  const { quartile_range: qr, tested_party_ratio: ratio } = state;

  const isWithin = ratio >= qr.q1 && ratio <= qr.q3;
  const isAbove  = ratio > qr.q3;
  const isBelow  = ratio < qr.q1 && ratio > 0;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Transfer Pricing Analysis Parameters</h1>
        <InfoBadge variant="manual" description="Set analysis parameters and IQR results" />
      </div>

      <SectionCard>
        <div className="grid grid-cols-2 gap-5">
          <div className="space-y-4">
            <SelectField
              label="Selected TP Method"
              required
              value={state.selected_method}
              onChange={(v) => setState({ selected_method: v })}
              options={TP_METHODS.map((m) => ({ value: m, label: m }))}
            />
            <SelectField
              label="Selected PLI"
              required
              value={state.selected_pli}
              onChange={(v) => setState({ selected_pli: v })}
              options={Object.entries(PLI_OPTIONS).map(([k, v]) => ({ value: k, label: `${k} — ${v}` }))}
            />
            <FormField
              label="Tested Party"
              required
              value={state.tested_party || state.company_short_name}
              onChange={(v) => setState({ tested_party: v })}
              placeholder="e.g., PT SP"
            />
          </div>

          <div className="space-y-4">
            <FormField
              label="Analysis Period (comparable years)"
              required
              value={state.analysis_period}
              onChange={(v) => setState({ analysis_period: v })}
              placeholder="e.g., 2020-2022"
            />
            <FormField
              label={`Tested Party Weighted Average ${state.selected_pli} (%)`}
              required
              type="number"
              value={String(state.tested_party_ratio)}
              onChange={(v) => setState({ tested_party_ratio: parseFloat(v) || 0 })}
              placeholder="e.g., 3.25"
            />
          </div>
        </div>
      </SectionCard>

      {/* IQR */}
      <SectionCard title="Interquartile Range Results">
        <div className="grid grid-cols-3 gap-4 mb-5">
          <FormField
            label="1st Quartile (%)"
            type="number"
            value={String(qr.q1)}
            onChange={(v) => setState({ quartile_range: { ...qr, q1: parseFloat(v) || 0 } })}
            placeholder="e.g., 2.10"
          />
          <FormField
            label="Median (%)"
            type="number"
            value={String(qr.median)}
            onChange={(v) => setState({ quartile_range: { ...qr, median: parseFloat(v) || 0 } })}
            placeholder="e.g., 3.50"
          />
          <FormField
            label="3rd Quartile (%)"
            type="number"
            value={String(qr.q3)}
            onChange={(v) => setState({ quartile_range: { ...qr, q3: parseFloat(v) || 0 } })}
            placeholder="e.g., 5.80"
          />
        </div>

        {/* Visual indicator */}
        {qr.q1 > 0 && ratio > 0 && (
          <div
            className={clsx(
              "rounded-lg px-4 py-3 text-sm font-medium",
              isWithin && "bg-green-50 border border-green-200 text-brand-dark",
              isAbove  && "bg-blue-50 border border-blue-200 text-blue-800",
              isBelow  && "bg-amber-50 border border-amber-200 text-amber-800",
            )}
          >
            {isWithin && `Tested party ratio (${ratio.toFixed(2)}%) is WITHIN the interquartile range (${qr.q1.toFixed(2)}% – ${qr.q3.toFixed(2)}%). Transaction is arm's length.`}
            {isAbove  && `Tested party ratio (${ratio.toFixed(2)}%) is ABOVE the interquartile range. Transaction is arm's length but may require additional documentation.`}
            {isBelow  && `Tested party ratio (${ratio.toFixed(2)}%) is BELOW the interquartile range. A transfer pricing adjustment may be required.`}
          </div>
        )}

        {/* IQR range bar */}
        {qr.q3 > 0 && (
          <div className="mt-4">
            <div className="relative h-8 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="absolute h-full bg-brand-green/30"
                style={{
                  left: `${(qr.q1 / (qr.q3 * 1.5)) * 100}%`,
                  width: `${((qr.q3 - qr.q1) / (qr.q3 * 1.5)) * 100}%`,
                }}
              />
              {ratio > 0 && (
                <div
                  className="absolute top-0 h-full w-1 bg-brand-green"
                  style={{ left: `${Math.min((ratio / (qr.q3 * 1.5)) * 100, 98)}%` }}
                  title={`Tested party: ${ratio.toFixed(2)}%`}
                />
              )}
            </div>
            <div className="flex justify-between text-xs text-gray-400 mt-1 px-1">
              <span>Q1: {qr.q1.toFixed(2)}%</span>
              <span>Median: {qr.median.toFixed(2)}%</span>
              <span>Q3: {qr.q3.toFixed(2)}%</span>
            </div>
          </div>
        )}
      </SectionCard>
    </div>
  );
}
