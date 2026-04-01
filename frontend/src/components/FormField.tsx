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
  "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition";

export function FormField(props: Props) {
  const { label, required, hint, error, className } = props;

  return (
    <div className={clsx("flex flex-col gap-1", className)}>
      <label className="text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
      </label>

      {props.multiline ? (
        <textarea
          rows={props.rows ?? 4}
          className={clsx(inputClass, "resize-y", error && "border-red-400")}
          value={props.value}
          placeholder={props.placeholder}
          onChange={(e) => props.onChange(e.target.value)}
        />
      ) : (
        <input
          type={props.type ?? "text"}
          className={clsx(inputClass, error && "border-red-400")}
          value={props.value}
          placeholder={props.placeholder}
          onChange={(e) => props.onChange(e.target.value)}
        />
      )}

      {hint && <p className="text-xs text-gray-400">{hint}</p>}
      {error && <p className="text-xs text-red-500">{error}</p>}
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
    <div className={clsx("flex flex-col gap-1", className)}>
      <label className="text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
      </label>
      <select
        className={clsx(inputClass, "bg-white", error && "border-red-400")}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
      {hint && <p className="text-xs text-gray-400">{hint}</p>}
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
