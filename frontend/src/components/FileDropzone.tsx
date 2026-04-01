import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { X } from "lucide-react";
import clsx from "clsx";

interface FileItem {
  file: File;
  valid: boolean;
  sizeLabel: string;
  error?: string;
}

interface Props {
  files: FileItem[];
  onChange: (files: FileItem[]) => void;
  accept?: Record<string, string[]>;
  maxSizeMB?: number;
  multiple?: boolean;
}

function formatSize(bytes: number): string {
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export function FileDropzone({
  files,
  onChange,
  accept = {
    "application/pdf": [".pdf"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    "text/plain": [".txt"],
  },
  maxSizeMB = 20,
  multiple = true,
}: Props) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      const items: FileItem[] = accepted.map((f) => {
        const mb = f.size / 1024 / 1024;
        const valid = mb <= maxSizeMB;
        return {
          file: f,
          valid,
          sizeLabel: formatSize(f.size),
          error: valid ? undefined : `Exceeds ${maxSizeMB} MB limit`,
        };
      });
      onChange([...files, ...items]);
    },
    [files, maxSizeMB, onChange],
  );

  const remove = (idx: number) => {
    onChange(files.filter((_, i) => i !== idx));
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    multiple,
  });

  return (
    <div className="space-y-3">
      <div
        {...getRootProps()}
        className={clsx(
          "border-2 border-dashed rounded-xl px-6 py-10 text-center cursor-pointer transition-colors",
          isDragActive
            ? "border-brand-green bg-green-50"
            : "border-gray-300 hover:border-brand-green hover:bg-gray-50",
        )}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <p className="text-brand-green font-medium">Drop files here…</p>
        ) : (
          <>
            <p className="text-gray-600 font-medium">Drag & drop files here</p>
            <p className="text-sm text-gray-400 mt-1">
              PDF, DOCX, XLSX, TXT — max {maxSizeMB} MB each
            </p>
            <button
              type="button"
              className="mt-3 px-4 py-1.5 bg-white border border-gray-300 text-sm rounded-lg hover:bg-gray-50 transition-colors"
            >
              Browse Files
            </button>
          </>
        )}
      </div>

      {files.length > 0 && (
        <ul className="space-y-1.5">
          {files.map((item, idx) => (
            <li
              key={idx}
              className={clsx(
                "flex items-center gap-3 px-3 py-2 rounded-lg border text-sm",
                item.valid
                  ? "border-green-200 bg-green-50"
                  : "border-red-200 bg-red-50",
              )}
            >
              <span className="flex-1 truncate font-medium">{item.file.name}</span>
              <span className="text-gray-500 text-xs">{item.sizeLabel}</span>
              {item.error && (
                <span className="text-red-500 text-xs">{item.error}</span>
              )}
              <button
                type="button"
                onClick={() => remove(idx)}
                className="p-0.5 hover:text-red-500 text-gray-400 transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
