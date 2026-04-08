import React from "react";
import { FormField, SelectField } from "../components/FormField";
import { DynamicTable } from "../components/DynamicTable";
import { InfoBadge } from "../components/InfoBadge";
import { SectionCard } from "../components/SectionCard";
import { useProjectStore } from "../store/projectStore";
import type { AffiliatedTransaction, IndependentTransaction } from "../types";

const TRANSACTION_TYPES = [
  "Purchase of tangible goods",
  "Sale of tangible goods",
  "Intra-group services",
  "Royalty/License fees",
  "Interest on loans",
  "Management fees",
];

export function Step5Transactions() {
  const { state, setState } = useProjectStore();

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Transaction Details</h1>
        <InfoBadge variant="manual" description="Describe affiliated transactions" />
      </div>

      <SectionCard>
        <div className="space-y-4">
          <SelectField
            label="Primary Transaction Type"
            required
            value={state.transaction_type}
            onChange={(v) => setState({ transaction_type: v })}
            options={TRANSACTION_TYPES.map((t) => ({ value: t, label: t }))}
          />
          <FormField
            label="Transaction Details"
            required
            multiline
            rows={5}
            value={state.transaction_details_text}
            onChange={(v) => setState({ transaction_details_text: v })}
            placeholder="Describe affiliated transactions: what goods/services, volumes, values, counterparties..."
          />
          <FormField
            label="Pricing Policy"
            required
            multiline
            rows={4}
            value={state.pricing_policy}
            onChange={(v) => setState({ pricing_policy: v })}
            placeholder="Describe how prices are determined for affiliated transactions..."
          />
        </div>
      </SectionCard>

      {/* Table 4.1 */}
      <SectionCard title="Table 4.1 — Affiliated Transactions">
        <p className="text-xs text-gray-500 mb-3">Affiliated Party | Jurisdiction | Form of Affiliation | Transaction Type | Amount (IDR)</p>
        <DynamicTable<AffiliatedTransaction>
          rows={state.affiliated_transactions}
          onChange={(rows) => setState({ affiliated_transactions: rows })}
          addLabel="Add Affiliated Transaction"
          columns={[
            { key: "name",             label: "Party Name",       placeholder: "e.g., Sany Heavy Industry" },
            { key: "country",          label: "Country",          placeholder: "China", width: "100px" },
            { key: "affiliation_type", label: "Affiliation",      placeholder: "e.g., Holding" },
            { key: "transaction_type", label: "Trans. Type",      placeholder: "e.g., Purchase goods" },
            { key: "value",            label: "Amount (IDR)",     placeholder: "e.g., 150,000,000,000", width: "180px" },
            { key: "note",             label: "Note",             placeholder: "e.g., CUP applied", width: "140px" },
          ]}
        />
      </SectionCard>

      {/* Table 4.2 */}
      <SectionCard title="Table 4.2 — Independent Transactions">
        <p className="text-xs text-gray-500 mb-3">Independent Party | Location | Transaction Type | Amount (IDR)</p>
        <DynamicTable<IndependentTransaction>
          rows={state.independent_transactions}
          onChange={(rows) => setState({ independent_transactions: rows })}
          addLabel="Add Independent Transaction"
          columns={[
            { key: "name",               label: "Party Name",              placeholder: "e.g., PT Vendor" },
            { key: "country",            label: "Country",                 placeholder: "Indonesia",         width: "110px" },
            { key: "transaction_type",   label: "Trans. Type",             placeholder: "e.g., Service fee" },
            { key: "type_of_product",    label: "Type of Product",         placeholder: "e.g., Raw materials" },
            { key: "amount_idr",         label: "Amount (IDR)",            placeholder: "e.g., 5,000,000,000", width: "160px" },
            { key: "quantity",           label: "Quantity",                placeholder: "e.g., 1,000",          width: "100px" },
            { key: "avg_price_per_unit", label: "Avg Price/Unit (IDR)",    placeholder: "e.g., 5,000,000",      width: "160px" },
          ]}
        />
      </SectionCard>
    </div>
  );
}
