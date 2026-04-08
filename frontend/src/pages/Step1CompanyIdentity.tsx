import React from "react";
import { FormField } from "../components/FormField";
import { InfoBadge } from "../components/InfoBadge";
import { SectionCard } from "../components/SectionCard";
import { useProjectStore } from "../store/projectStore";

export function Step1CompanyIdentity() {
  const { state, setState } = useProjectStore();
  const s = (key: string, val: string) => setState({ [key]: val } as Parameters<typeof setState>[0]);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-black text-gray-900 tracking-tight">Company Identity</h1>
        <InfoBadge variant="manual" description="Define the primary identification and organizational structure of the entity." />
      </div>

      <SectionCard title="General Identification">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-6">
            <FormField
              label="Full Company Name"
              required
              value={state.company_name}
              onChange={(v) => s("company_name", v)}
              placeholder="e.g., PT Sany Perkasa"
            />
            <div className="grid grid-cols-2 gap-4">
              <FormField
                label="Short Name / Abbr"
                required
                value={state.company_short_name}
                onChange={(v) => s("company_short_name", v)}
                placeholder="e.g., PT SP"
              />
              <FormField
                label="Fiscal Year"
                required
                value={state.fiscal_year}
                onChange={(v) => s("fiscal_year", v)}
                placeholder="e.g., 2024"
              />
            </div>
            <FormField
              label="Product / Trade Brand Name"
              value={state.brand_name}
              onChange={(v) => s("brand_name", v)}
              placeholder="e.g., SANY"
              hint="Leave blank to use company short name"
            />
          </div>
          <div className="space-y-6">
            <FormField
              label="Company Address"
              required
              multiline
              rows={4}
              value={state.company_address}
              onChange={(v) => s("company_address", v)}
              placeholder="Full registered street address, city, and province..."
            />
            <FormField
              label="Establishment Info"
              multiline
              rows={4}
              value={state.establishment_info}
              onChange={(v) => s("establishment_info", v)}
              placeholder="Deed number, date, notary, and Ministry approval details..."
            />
          </div>
        </div>
      </SectionCard>

      <SectionCard title="Ownership & Group Hierarchy">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <FormField
            label="Direct Parent Company"
            value={state.parent_company}
            onChange={(v) => s("parent_company", v)}
            placeholder="e.g., Sany Southeast Asia Pte, Ltd"
            hint="The immediate entity that holds shares in the local company"
          />
          <FormField
            label="Ultimate Parent Group"
            value={state.parent_group}
            onChange={(v) => s("parent_group", v)}
            placeholder="e.g., Sany Group"
            hint="The global group head or ultimate parent company"
          />
        </div>
      </SectionCard>
    </div>
  );
}
