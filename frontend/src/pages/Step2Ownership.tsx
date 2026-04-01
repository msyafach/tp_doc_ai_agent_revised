import React from "react";
import { DynamicTable } from "../components/DynamicTable";
import { FormField } from "../components/FormField";
import { InfoBadge } from "../components/InfoBadge";
import { SectionCard } from "../components/SectionCard";
import { useProjectStore } from "../store/projectStore";
import type { Shareholder, Management } from "../types";

export function Step2Ownership() {
  const { state, setState } = useProjectStore();

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Ownership & Management Structure</h1>
        <InfoBadge variant="manual" description="Enter shareholder and management details" />
      </div>

      <SectionCard title="Shareholders">
        <DynamicTable<Shareholder>
          rows={state.shareholders}
          onChange={(rows) => setState({ shareholders: rows })}
          addLabel="Add Shareholder"
          columns={[
            { key: "name",       label: "Shareholder Name",  placeholder: "e.g., Sany Southeast Asia Pte, Ltd" },
            { key: "shares",     label: "Number of Shares",  placeholder: "e.g., 14,850", width: "140px" },
            { key: "capital",    label: "Capital (IDR)",     placeholder: "e.g., 14,850,000,000", width: "180px" },
            { key: "percentage", label: "Ownership %",       placeholder: "e.g., 99.00%", width: "120px" },
          ]}
        />
        <div className="mt-3">
          <FormField
            label="Source (shareholders table)"
            value={state.shareholders_source}
            onChange={(v) => setState({ shareholders_source: v })}
            placeholder="e.g., Source: Management PT SP, 31 December 2024"
          />
        </div>
      </SectionCard>

      <SectionCard title="Management / Board of Directors">
        <DynamicTable<Management>
          rows={state.management}
          onChange={(rows) => setState({ management: rows })}
          addLabel="Add Management"
          columns={[
            { key: "position", label: "Position",    placeholder: "e.g., President Director" },
            { key: "name",     label: "Name",        placeholder: "e.g., John Doe" },
          ]}
        />
        <div className="mt-3">
          <FormField
            label="Source (management table)"
            value={state.management_source}
            onChange={(v) => setState({ management_source: v })}
            placeholder="e.g., Source: Management PT SP, 31 December 2024"
          />
        </div>
      </SectionCard>

      <SectionCard>
        <FormField
          label="Total Permanent Employees"
          value={state.employee_count}
          onChange={(v) => setState({ employee_count: v })}
          placeholder="e.g., 1,034"
        />
      </SectionCard>
    </div>
  );
}
