import React from "react";
import { DynamicTable } from "../components/DynamicTable";
import { InfoBadge } from "../components/InfoBadge";
import { SectionCard } from "../components/SectionCard";
import { useProjectStore } from "../store/projectStore";
import type { AffiliatedParty } from "../types";

export function Step3AffiliatedParties() {
  const { state, setState } = useProjectStore();

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Affiliated Parties</h1>
        <InfoBadge variant="manual" description="List all related party entities" />
      </div>

      <SectionCard>
        <DynamicTable<AffiliatedParty>
          rows={state.affiliated_parties}
          onChange={(rows) => setState({ affiliated_parties: rows })}
          addLabel="Add Affiliated Party"
          columns={[
            { key: "name",             label: "Company Name",      placeholder: "e.g., Sany Heavy Industry" },
            { key: "country",          label: "Country",           placeholder: "e.g., China", width: "120px" },
            { key: "relationship",     label: "Relationship Type", placeholder: "e.g., Holding company" },
            { key: "transaction_type", label: "Transaction Type",  placeholder: "e.g., Purchase of goods" },
          ]}
        />
      </SectionCard>
    </div>
  );
}
