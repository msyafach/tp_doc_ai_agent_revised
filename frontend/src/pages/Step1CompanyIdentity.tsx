import React from "react";
import { FormField } from "../components/FormField";
import { InfoBadge } from "../components/InfoBadge";
import { SectionCard } from "../components/SectionCard";
import { useProjectStore } from "../store/projectStore";

export function Step1CompanyIdentity() {
  const { state, setState } = useProjectStore();
  const s = (key: string, val: string) => setState({ [key]: val } as Parameters<typeof setState>[0]);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Company Identity</h1>
        <InfoBadge variant="manual" description="Enter company identification details" />
      </div>

      <SectionCard>
        <div className="grid grid-cols-2 gap-5">
          <div className="space-y-4">
            <FormField
              label="Full Company Name"
              required
              value={state.company_name}
              onChange={(v) => s("company_name", v)}
              placeholder="e.g., PT Sany Perkasa"
            />
            <FormField
              label="Short Name / Abbreviation"
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
          <div className="space-y-4">
            <FormField
              label="Company Address"
              required
              multiline
              rows={3}
              value={state.company_address}
              onChange={(v) => s("company_address", v)}
              placeholder="Street, City, Province..."
            />
            <FormField
              label="Establishment Information"
              multiline
              rows={3}
              value={state.establishment_info}
              onChange={(v) => s("establishment_info", v)}
              placeholder="Deed number, date, notary, Ministry approval details..."
            />
          </div>
        </div>

        <div className="mt-5 border-t border-gray-100 pt-5 grid grid-cols-3 gap-5">
          <FormField
            label="Direct Parent Company"
            value={state.parent_company}
            onChange={(v) => s("parent_company", v)}
            placeholder="e.g., Sany Southeast Asia Pte, Ltd"
          />
          <FormField
            label="Ultimate Parent Group"
            value={state.parent_group}
            onChange={(v) => s("parent_group", v)}
            placeholder="e.g., Sany Group"
          />
          <FormField
            label="Product / Trade Brand Name"
            value={state.brand_name}
            onChange={(v) => s("brand_name", v)}
            placeholder="e.g., SANY (leave blank to use short name)"
            hint="Leave blank to use company short name"
          />
        </div>
      </SectionCard>
    </div>
  );
}
