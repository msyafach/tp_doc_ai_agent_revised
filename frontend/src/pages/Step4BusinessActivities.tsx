import React, { useRef } from "react";
import { Plus, Trash2, Image as ImageIcon } from "lucide-react";
import { FormField } from "../components/FormField";
import { InfoBadge } from "../components/InfoBadge";
import { SectionCard } from "../components/SectionCard";
import { DynamicTable } from "../components/DynamicTable";
import { useProjectStore } from "../store/projectStore";
import type { Product, OrgDepartment } from "../types";

export function Step4BusinessActivities() {
  const { state, setState } = useProjectStore();
  const orgImgRef = useRef<HTMLInputElement>(null);

  const addProduct = () => setState({ products: [...state.products, { name: "", description: "" }] });
  const removeProduct = (i: number) => setState({ products: state.products.filter((_, idx) => idx !== i) });
  const updateProduct = (i: number, key: keyof Product, val: string) => {
    setState({ products: state.products.map((p, idx) => idx === i ? { ...p, [key]: val } : p) });
  };

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Business Activities & Products</h1>
        <InfoBadge variant="manual" description="Describe the company's business" />
      </div>

      <SectionCard>
        <FormField
          label="Business Activities Description"
          required
          multiline
          rows={5}
          value={state.business_activities_description}
          onChange={(v) => setState({ business_activities_description: v })}
          placeholder="Describe main business activities, operational aspects, industry sector..."
        />
      </SectionCard>

      {/* Org Structure */}
      <SectionCard title="Organization Structure (Appendix 1)">
        <FormField
          label="Description"
          multiline
          rows={3}
          value={state.org_structure_description}
          onChange={(v) => setState({ org_structure_description: v })}
          placeholder="Briefly describe the organizational structure..."
        />

        <div className="mt-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Departments / Units</p>
          <DynamicTable<OrgDepartment>
            rows={state.org_structure_departments}
            onChange={(rows) => setState({ org_structure_departments: rows })}
            addLabel="Add Department"
            columns={[
              { key: "name",      label: "Dept / Unit Name", placeholder: "e.g., Sales" },
              { key: "head",      label: "Head / PIC",       placeholder: "e.g., John Doe", width: "180px" },
              { key: "employees", label: "# Employees",      placeholder: "e.g., 20", width: "120px" },
            ]}
          />
        </div>
      </SectionCard>

      {/* Products */}
      <SectionCard title="Products / Services">
        <div className="space-y-3">
          {state.products.map((p, i) => (
            <div key={i} className="flex gap-3 items-start">
              <span className="text-sm font-medium text-gray-400 pt-2 w-6 text-right">{i + 1}</span>
              <div className="flex-1 grid grid-cols-2 gap-3">
                <FormField
                  label={i === 0 ? "Product Name" : ""}
                  value={p.name}
                  onChange={(v) => updateProduct(i, "name", v)}
                  placeholder="e.g., Heavy Equipment"
                />
                <FormField
                  label={i === 0 ? "Description" : ""}
                  value={p.description}
                  onChange={(v) => updateProduct(i, "description", v)}
                  placeholder="Brief description..."
                />
              </div>
              <button
                type="button"
                disabled={state.products.length <= 1}
                onClick={() => removeProduct(i)}
                className="mt-6 p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={addProduct}
            className="inline-flex items-center gap-1.5 text-sm text-brand-green hover:text-brand-dark font-medium px-3 py-1.5 rounded-md hover:bg-green-50 transition-colors"
          >
            <Plus className="w-4 h-4" /> Add Product
          </button>
        </div>
      </SectionCard>

      {/* Business Strategy & Restructuring */}
      <SectionCard>
        <div className="space-y-4">
          <FormField
            label="Business Strategy"
            multiline
            rows={4}
            value={state.business_strategy}
            onChange={(v) => setState({ business_strategy: v })}
            placeholder="Describe the company's business strategy..."
          />
          <FormField
            label="Business Restructuring / Transfer of Intangible Assets"
            multiline
            rows={3}
            value={state.business_restructuring}
            onChange={(v) => setState({ business_restructuring: v })}
            placeholder="Leave blank if no restructuring occurred in the fiscal year"
          />
        </div>
      </SectionCard>

      {/* Business Characterization */}
      <SectionCard title="Business Characteristics (Section 4.2.3)">
        <InfoBadge
          variant="manual"
          description="Describe business characterization (e.g., Contract Manufacturer, Distributor) based on functional analysis."
        />
        <div className="mt-3">
          <FormField
            label="Business Characterization Text"
            multiline
            rows={6}
            value={state.business_characterization_text}
            onChange={(v) => setState({ business_characterization_text: v })}
            placeholder="e.g., Based on the functional analysis, PT [Company] is characterized as a Limited Risk Distributor..."
          />
        </div>
      </SectionCard>
    </div>
  );
}
