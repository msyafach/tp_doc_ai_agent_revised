import React from "react";
import clsx from "clsx";

type Variant = "manual" | "template" | "ai" | "optional";

const VARIANTS: Record<Variant, { bg: string; text: string; label: string; icon?: string }> = {
  manual:   { bg: "bg-brand-blue/5 border-brand-blue/10",   text: "text-brand-blue",  label: "Manual Entry"     },
  template: { bg: "bg-brand-green/5 border-brand-green/10",  text: "text-brand-green", label: "Template"         },
  ai:       { bg: "bg-purple-50 border-purple-100",          text: "text-purple-700",  label: "AI Extraction"    },
  optional: { bg: "bg-gray-50 border-gray-100",            text: "text-gray-500",    label: "Optional Step"    },
};

interface Props {
  variant: Variant;
  description?: string;
}

export function InfoBadge({ variant, description }: Props) {
  const v = VARIANTS[variant];
  return (
    <div className={clsx("border-l-4 rounded-r-xl px-5 py-4 text-sm shadow-sm flex flex-col gap-1", v.bg, v.text, "border-current")}>
      <span className="font-black uppercase tracking-[0.2em] text-[10px]">
        {v.label}
      </span>
      {description && (
        <p className="font-medium leading-relaxed opacity-90">
          {description}
        </p>
      )}
    </div>
  );
}
