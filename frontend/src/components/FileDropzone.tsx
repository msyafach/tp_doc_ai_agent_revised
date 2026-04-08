import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { X, ChevronDown, PlusCircle } from "lucide-react";
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
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={clsx(
          "border-2 border-dashed rounded-2xl px-8 py-14 text-center cursor-pointer transition-all duration-300",
          isDragActive
            ? "border-brand-green bg-green-50/50 shadow-inner scale-[0.99]"
            : "border-gray-200 hover:border-brand-blue/40 hover:bg-brand-blue/5 hover:shadow-sm",
        )}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <div className="flex flex-col items-center gap-2 animate-in zoom-in-95">
            <div className="w-12 h-12 bg-brand-green text-white rounded-full flex items-center justify-center shadow-lg shadow-brand-green/20">
              <ChevronDown className="w-6 h-6" />
            </div>
            <p className="text-brand-green font-black uppercase tracking-widest text-xs mt-2">Release to upload</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <div className="w-12 h-12 bg-gray-50 text-gray-400 rounded-full flex items-center justify-center mb-2 group-hover:bg-brand-blue/10 group-hover:text-brand-blue transition-colors">
              <PlusCircle className="w-6 h-6" />
            </div>
            <p className="text-gray-900 font-bold text-base">Drag & drop source files here</p>
            <p className="text-sm text-gray-400 font-medium mt-1">
              PDF, DOCX, XLSX, TXT up to {maxSizeMB} MB
            </p>
            <button
              type="button"
              className="mt-6 px-8 py-2.5 bg-white border border-gray-200 text-xs font-black uppercase tracking-widest text-gray-600 rounded-xl hover:bg-gray-50 hover:border-gray-300 hover:shadow-sm transition-all active:scale-95"
            >
              Browse Local Files
            </button>
          </div>
        )}
      </div>

      {files.length > 0 && (
        <div className="grid gap-2 sm:grid-cols-2">
          {files.map((item, idx) => (
            <div
              key={idx}
              className={clsx(
                "flex items-center gap-4 px-4 py-3 rounded-xl border transition-all animate-in slide-in-from-left-2",
                item.valid ? "bg-white border-gray-100 shadow-sm" : "bg-red-50 border-red-100 text-red-700"
              )}
            >
              <div className={clsx(
                "w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 font-black text-[10px] uppercase",
                item.valid ? "bg-gray-50 text-gray-400" : "bg-red-100 text-red-500"
              )}>
                {item.file.name.split(".").pop()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-gray-900 truncate">{item.file.name}</p>
                <p className={clsx(
                  "text-[10px] font-black uppercase tracking-widest",
                  item.valid ? "text-gray-400" : "text-red-500"
                )}>
                  {item.sizeLabel} {item.error && `· ${item.error}`}
                </p>
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); remove(idx); }}
                className="p-2 hover:bg-gray-100 rounded-lg text-gray-300 hover:text-red-500 transition-all"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
