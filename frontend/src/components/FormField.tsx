import React from "react";
import clsx from "clsx";

interface BaseProps {
  label: string;
  required?: boolean;
  hint?: string;
  error?: string;
  className?: string;
}

interface InputProps extends BaseProps {
  type?: "text" | "password" | "number" | "email";
  value: string | number;
  onChange: (v: string) => void;
  placeholder?: string;
  multiline?: false;
  rows?: never;
}

interface TextareaProps extends BaseProps {
  multiline: true;
  rows?: number;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: never;
}

type Props = InputProps | TextareaProps;

const inputClass =
  "w-full border-2 border-gray-100 rounded-xl px-4 py-3 text-sm font-medium focus:outline-none focus:border-brand-green/40 focus:ring-4 focus:ring-brand-green/5 transition-all bg-gray-50/30 hover:bg-white hover:border-gray-200";

export function FormField(props: Props) {
  const { label, required, hint, error, className } = props;

  return (
    <div className={clsx("flex flex-col gap-1.5", className)}>
      <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      {props.multiline ? (
        <textarea
          rows={props.rows ?? 4}
          className={clsx(inputClass, "resize-y", error && "border-red-200 focus:border-red-300 focus:ring-red-50")}
          value={props.value}
          placeholder={props.placeholder}
          onChange={(e) => props.onChange(e.target.value)}
        />
      ) : (
        <input
          type={props.type ?? "text"}
          className={clsx(inputClass, error && "border-red-200 focus:border-red-300 focus:ring-red-50")}
          value={props.value}
          placeholder={props.placeholder}
          onChange={(e) => props.onChange(e.target.value)}
        />
      )}

      {hint && <p className="text-[11px] text-gray-400 font-medium ml-1">{hint}</p>}
      {error && <p className="text-[11px] text-red-500 font-bold ml-1">{error}</p>}
    </div>
  );
}

// ─── Select ───────────────────────────────────────────────────────────────────

interface SelectProps extends BaseProps {
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}

export function SelectField({ label, required, hint, error, className, value, onChange, options }: SelectProps) {
  return (
    <div className={clsx("flex flex-col gap-1.5", className)}>
      <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      <select
        className={clsx(inputClass, "bg-white", error && "border-red-200 focus:border-red-300 focus:ring-red-50")}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
      {hint && <p className="text-[11px] text-gray-400 font-medium ml-1">{hint}</p>}
      {error && <p className="text-[11px] text-red-500 font-bold ml-1">{error}</p>}
    </div>
  );
}
