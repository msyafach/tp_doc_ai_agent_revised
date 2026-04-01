import React from "react";
import { FormField } from "../components/FormField";
import { InfoBadge } from "../components/InfoBadge";
import { SectionCard } from "../components/SectionCard";
import { useProjectStore } from "../store/projectStore";

export function Step9NonFinancial() {
  const { state, setState } = useProjectStore();

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Non-Financial Events</h1>
        <InfoBadge variant="manual" description="Describe any non-financial events affecting pricing" />
      </div>

      <SectionCard>
        <FormField
          label="Non-Financial Events / Occurrences / Facts"
          multiline
          rows={8}
          value={state.non_financial_events}
          onChange={(v) => setState({ non_financial_events: v })}
          placeholder="Describe any significant non-financial events that affected pricing or profit levels in the fiscal year. Leave blank if none."
        />
        <p className="text-xs text-gray-400 mt-2">
          Examples: new product launches, market disruptions, COVID-19 impacts, regulatory changes, major contracts won/lost.
        </p>
      </SectionCard>
    </div>
  );
}
