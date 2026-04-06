import React from "react";
import { Plus, Trash2 } from "lucide-react";
import clsx from "clsx";

interface Column<T> {
  key: keyof T;
  label: string;
  type?: "text" | "textarea" | "number";
  placeholder?: string;
  width?: string;
}

interface Props<T extends Record<string, unknown>> {
  rows: T[];
  columns: Column<T>[];
  onChange: (rows: T[]) => void;
  addLabel?: string;
  minRows?: number;
  className?: string;
}

export function DynamicTable<T extends Record<string, unknown>>({
  rows,
  columns,
  onChange,
  addLabel = "Add Row",
  minRows = 1,
  className,
}: Props<T>) {
  const addRow = () => {
    const empty = Object.fromEntries(columns.map((c) => [c.key, ""])) as T;
    onChange([...rows, empty]);
  };

  const removeRow = (idx: number) => {
    onChange(rows.filter((_, i) => i !== idx));
  };

  const updateCell = (idx: number, key: keyof T, value: string) => {
    const updated = rows.map((r, i) =>
      i === idx ? { ...r, [key]: value } : r,
    );
    onChange(updated);
  };

  return (
    <div className={clsx("space-y-2", className)}>
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase w-10">
                #
              </th>
              {columns.map((col) => (
                <th
                  key={String(col.key)}
                  className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase"
                  style={{ width: col.width }}
                >
                  {col.label}
                </th>
              ))}
              <th className="w-10 px-2 py-2" />
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {rows.map((row, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="px-3 py-2 text-sm text-gray-400 text-center font-medium">
                  {idx + 1}
                </td>
                {columns.map((col) => (
                  <td key={String(col.key)} className="px-3 py-1.5">
                    {col.type === "textarea" ? (
                      <textarea
                        rows={2}
                        className="w-full text-sm border border-gray-200 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-green-500 resize-none"
                        value={String(row[col.key] ?? "")}
                        placeholder={col.placeholder}
                        onChange={(e) => updateCell(idx, col.key, e.target.value)}
                      />
                    ) : (
                      <input
                        type={col.type ?? "text"}
                        className="w-full text-sm border border-gray-200 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-green-500"
                        value={String(row[col.key] ?? "")}
                        placeholder={col.placeholder}
                        onChange={(e) => updateCell(idx, col.key, e.target.value)}
                      />
                    )}
                  </td>
                ))}
                <td className="px-2 py-1.5 text-center">
                  <button
                    type="button"
                    disabled={rows.length <= minRows}
                    onClick={() => removeRow(idx)}
                    className="p-1 rounded text-gray-400 hover:text-red-500 hover:bg-red-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button
        type="button"
        onClick={addRow}
        className="inline-flex items-center gap-1.5 text-sm text-brand-green hover:text-brand-dark font-medium px-3 py-1.5 rounded-md hover:bg-green-50 transition-colors"
      >
        <Plus className="w-4 h-4" />
        {addLabel}
      </button>
    </div>
  );
}
