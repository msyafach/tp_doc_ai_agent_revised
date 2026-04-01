import React from "react";
import clsx from "clsx";

interface Props {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

export function SectionCard({ title, children, className }: Props) {
  return (
    <div className={clsx("bg-white rounded-xl border border-gray-200 p-6", className)}>
      {title && (
        <h3 className="text-base font-semibold text-gray-800 mb-4">{title}</h3>
      )}
      {children}
    </div>
  );
}
