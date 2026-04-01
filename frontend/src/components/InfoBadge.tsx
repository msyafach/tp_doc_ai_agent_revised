import React from "react";
import clsx from "clsx";

type Variant = "manual" | "template" | "ai" | "optional";

const VARIANTS: Record<Variant, { bg: string; text: string; label: string }> = {
  manual:   { bg: "bg-blue-50 border-[#0096C6]/30",   text: "text-[#006B8F]",  label: "Manual Input"     },
  template: { bg: "bg-green-50 border-[#508C4F]/30",  text: "text-[#3D6B3C]", label: "Template"         },
  ai:       { bg: "bg-blue-50/80 border-[#0096C6]/20",text: "text-[#006B8F]", label: "AI Agent"          },
  optional: { bg: "bg-gray-50 border-gray-200",       text: "text-brand-grey", label: "Optional Step"    },
};

interface Props {
  variant: Variant;
  description?: string;
}

export function InfoBadge({ variant, description }: Props) {
  const v = VARIANTS[variant];
  return (
    <div className={clsx("border rounded-lg px-4 py-3 text-sm", v.bg, v.text)}>
      <span>
        <strong>{v.label}</strong>
        {description && ` — ${description}`}
      </span>
    </div>
  );
}
