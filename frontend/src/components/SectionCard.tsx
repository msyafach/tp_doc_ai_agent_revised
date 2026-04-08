import React from "react";
import clsx from "clsx";

interface Props {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export function SectionCard({ title, children, className }: Props) {
  return (
    <div className={clsx("bg-white rounded-2xl border border-gray-100 p-8 shadow-sm", className)}>
      {title && (
        <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
          <div className="w-1 h-5 bg-brand-green rounded-full" />
          {title}
        </h3>
      )}
      {children}
    </div>
  );
}
