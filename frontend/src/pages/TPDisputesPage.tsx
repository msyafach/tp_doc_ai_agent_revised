import React, { useEffect, useState } from "react";
import { Info, Pencil, Trash2, LogOut, ChevronLeft, Scale, X, Save, Loader2, Upload, Plus, FileSpreadsheet, ChevronRight } from "lucide-react";
import {
  listTPDisputes, updateTPDispute, deleteTPDispute, uploadTPDisputes,
  type TPDispute, type TPDisputeInput, type TPDisputeUploadResult,
} from "../api/tpDisputes";

interface Props {
  onLogout: () => void;
  onBack: () => void;
  username: string;
}

const FIELD_LABELS: Record<keyof TPDisputeInput, string> = {
  verdict_number: "No. Putusan",
  name: "Nama",
  verdict: "Amar Putusan",
  dispute: "Pokok Sengketa",
  legal_basis: "Dasar Hukum",
  djp: "Menurut DJP",
  taxpayer: "Menurut Wajib Pajak",
  assembly_decision: "Keputusan Majelis",
};

export function TPDisputesPage({ onLogout, onBack, username }: Props) {
  const [rows, setRows] = useState<TPDispute[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewing, setViewing] = useState<TPDispute | null>(null);
  const [editing, setEditing] = useState<TPDispute | null>(null);
  const [deleting, setDeleting] = useState<TPDispute | null>(null);
  const [uploading, setUploading] = useState(false);
  const [page, setPage] = useState(1);

  const PAGE_SIZE = 10;
  const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const pageRows = rows.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);

  useEffect(() => {
    if (page > totalPages) setPage(totalPages);
  }, [totalPages, page]);

  const refresh = async () => {
    setLoading(true);
    try {
      setRows(await listTPDisputes());
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { refresh(); }, []);

  const handleDelete = async () => {
    if (!deleting) return;
    try {
      await deleteTPDispute(deleting.id);
      setRows((prev) => prev.filter((r) => r.id !== deleting.id));
    } catch {
      alert("Gagal menghapus data.");
    } finally {
      setDeleting(null);
    }
  };

  const truncate = (s: string, n = 80) =>
    s && s.length > n ? s.slice(0, n).trimEnd() + "…" : s;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-12 py-8 flex flex-col items-center text-center shadow-sm relative">
        <div className="absolute top-4 right-6 flex items-center gap-2">
          {username && (
            <span className="text-xs font-semibold text-gray-400 px-3 py-1.5 bg-gray-50 rounded-full border border-gray-100">
              {username}
            </span>
          )}
          <button
            onClick={onLogout}
            className="flex items-center gap-1.5 text-xs font-semibold text-red-500 bg-red-50 px-3 py-1.5 rounded-full border border-red-100 hover:bg-red-100 transition-all"
          >
            <LogOut className="w-3.5 h-3.5" /> Sign Out
          </button>
        </div>

        <button
          onClick={onBack}
          className="absolute top-4 left-6 flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-brand-blue transition-colors"
        >
          <ChevronLeft className="w-4 h-4" /> Back
        </button>

        <h1 className="font-extrabold text-2xl text-gray-900 tracking-tight flex items-center gap-3">
          <Scale className="w-7 h-7 text-brand-blue" />
          Database <span className="text-brand-green">Putusan TP</span>
        </h1>
        <p className="mt-1 text-xs font-semibold text-gray-400 uppercase tracking-[0.2em]">
          Transfer Pricing Dispute Records
        </p>
      </header>

      {/* Content */}
      <main className="flex-1 px-8 py-10 max-w-7xl w-full mx-auto">
        <div className="mb-5 flex justify-end">
          <button
            onClick={() => setUploading(true)}
            className="flex items-center gap-2 px-4 py-2.5 text-sm font-semibold bg-brand-green text-white rounded-lg hover:bg-brand-dark shadow-md shadow-brand-green/20 transition-all active:scale-95"
          >
            <Plus className="w-4 h-4" /> Tambah
          </button>
        </div>

        <div className="bg-white rounded-2xl border border-gray-100 shadow-xl shadow-gray-200/40 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-20 text-gray-400 text-sm">
              <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Memuat data…
            </div>
          ) : rows.length === 0 ? (
            <div className="py-20 text-center text-gray-400 text-sm">
              Belum ada data putusan.
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200 text-[11px] font-bold text-gray-500 uppercase tracking-wider">
                  <th className="px-6 py-4 text-left w-56">No. Putusan</th>
                  <th className="px-6 py-4 text-left w-48">Nama</th>
                  <th className="px-6 py-4 text-left">Amar Putusan</th>
                  <th className="px-6 py-4 text-left">Pokok Sengketa</th>
                  <th className="px-6 py-4 text-center w-32">Aksi</th>
                </tr>
              </thead>
              <tbody>
                {pageRows.map((r) => (
                  <tr key={r.id} className="border-b border-gray-100 hover:bg-gray-50/50 transition-colors">
                    <td className="px-6 py-4 font-mono text-xs text-gray-700">{r.verdict_number}</td>
                    <td className="px-6 py-4 text-gray-800 font-medium">{r.name || "—"}</td>
                    <td className="px-6 py-4 text-gray-600">{truncate(r.verdict) || "—"}</td>
                    <td className="px-6 py-4 text-gray-600">{truncate(r.dispute) || "—"}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-center gap-1">
                        <IconButton title="Keterangan Lengkap" onClick={() => setViewing(r)} color="blue">
                          <Info className="w-4 h-4" />
                        </IconButton>
                        <IconButton title="Edit" onClick={() => setEditing(r)} color="green">
                          <Pencil className="w-4 h-4" />
                        </IconButton>
                        <IconButton title="Delete" onClick={() => setDeleting(r)} color="red">
                          <Trash2 className="w-4 h-4" />
                        </IconButton>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {rows.length > PAGE_SIZE && (
          <div className="mt-5 flex items-center justify-between text-xs">
            <span className="text-gray-500">
              Menampilkan{" "}
              <span className="font-semibold text-gray-700">{(safePage - 1) * PAGE_SIZE + 1}</span>
              {"–"}
              <span className="font-semibold text-gray-700">{Math.min(safePage * PAGE_SIZE, rows.length)}</span>
              {" dari "}
              <span className="font-semibold text-gray-700">{rows.length}</span>
              {" data"}
            </span>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={safePage === 1}
                className="flex items-center gap-1 px-3 py-1.5 font-semibold text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-3.5 h-3.5" /> Prev
              </button>
              <span className="px-3 py-1.5 font-semibold text-gray-700">
                {safePage} / {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={safePage === totalPages}
                className="flex items-center gap-1 px-3 py-1.5 font-semibold text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Next <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}
      </main>

      {uploading && (
        <UploadDialog
          onClose={() => setUploading(false)}
          onDone={() => { setUploading(false); refresh(); }}
        />
      )}

      {viewing && <DetailDialog row={viewing} onClose={() => setViewing(null)} />}
      {editing && (
        <EditDialog
          row={editing}
          onClose={() => setEditing(null)}
          onSaved={(updated) => {
            setRows((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
            setEditing(null);
          }}
        />
      )}
      {deleting && (
        <ConfirmDialog
          title="Hapus Data?"
          message={`Yakin ingin menghapus putusan ${deleting.verdict_number}? Tindakan ini tidak dapat dibatalkan.`}
          onCancel={() => setDeleting(null)}
          onConfirm={handleDelete}
        />
      )}
    </div>
  );
}

// ─── Components ──────────────────────────────────────────────────────────────

function IconButton({
  children, onClick, title, color,
}: {
  children: React.ReactNode;
  onClick: () => void;
  title: string;
  color: "blue" | "green" | "red";
}) {
  const cls = {
    blue: "text-brand-blue hover:bg-brand-blue/10",
    green: "text-brand-green hover:bg-brand-green/10",
    red: "text-red-500 hover:bg-red-50",
  }[color];
  return (
    <button
      onClick={onClick}
      title={title}
      aria-label={title}
      className={`p-2 rounded-lg transition-colors ${cls}`}
    >
      {children}
    </button>
  );
}

function DialogShell({
  title, onClose, children, footer, wide,
}: {
  title: string;
  onClose: () => void;
  children: React.ReactNode;
  footer?: React.ReactNode;
  wide?: boolean;
}) {
  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className={`bg-white rounded-2xl shadow-2xl w-full ${wide ? "max-w-3xl" : "max-w-md"} max-h-[90vh] flex flex-col`}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="text-base font-bold text-gray-800">{title}</h2>
          <button onClick={onClose} className="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-50">
            <X className="w-4 h-4" />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-6 py-5">{children}</div>
        {footer && <div className="px-6 py-4 border-t border-gray-100 bg-gray-50/50 flex justify-end gap-2">{footer}</div>}
      </div>
    </div>
  );
}

function DetailDialog({ row, onClose }: { row: TPDispute; onClose: () => void }) {
  const Field = ({ label, value }: { label: string; value: string }) => (
    <div>
      <dt className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">{label}</dt>
      <dd className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">{value || "—"}</dd>
    </div>
  );
  return (
    <DialogShell title={`Detail Putusan — ${row.verdict_number}`} onClose={onClose} wide>
      <dl className="space-y-5">
        <Field label="No. Putusan" value={row.verdict_number} />
        <Field label="Nama" value={row.name} />
        <Field label="Amar Putusan" value={row.verdict} />
        <Field label="Pokok Sengketa" value={row.dispute} />
        <div className="border-t border-gray-100 pt-5 grid grid-cols-1 md:grid-cols-2 gap-5">
          <Field label="Dasar Hukum" value={row.legal_basis} />
          <Field label="Keputusan Majelis" value={row.assembly_decision} />
          <Field label="Menurut DJP" value={row.djp} />
          <Field label="Menurut Wajib Pajak" value={row.taxpayer} />
        </div>
      </dl>
    </DialogShell>
  );
}

function EditDialog({
  row, onClose, onSaved,
}: {
  row: TPDispute;
  onClose: () => void;
  onSaved: (updated: TPDispute) => void;
}) {
  const [form, setForm] = useState<TPDisputeInput>({
    name: row.name,
    verdict_number: row.verdict_number,
    verdict: row.verdict,
    dispute: row.dispute,
    legal_basis: row.legal_basis,
    djp: row.djp,
    taxpayer: row.taxpayer,
    assembly_decision: row.assembly_decision,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = (k: keyof TPDisputeInput) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      const updated = await updateTPDispute(row.id, form);
      onSaved(updated);
    } catch (e: any) {
      const detail = e?.response?.data?.verdict_number?.[0] || e?.response?.data?.detail || "Gagal menyimpan.";
      setError(String(detail));
      setSaving(false);
    }
  };

  return (
    <DialogShell
      title={`Edit Putusan — ${row.verdict_number}`}
      onClose={onClose}
      wide
      footer={
        <>
          <button onClick={onClose} className="px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-100 rounded-lg">
            Batal
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 text-sm font-semibold bg-brand-green text-white rounded-lg hover:bg-brand-dark disabled:opacity-50"
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            Simpan
          </button>
        </>
      }
    >
      {error && (
        <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-100 text-sm text-red-700">{error}</div>
      )}
      <div className="space-y-4">
        {(Object.keys(FIELD_LABELS) as (keyof TPDisputeInput)[]).map((key) => {
          const isLong = ["verdict", "dispute", "legal_basis", "djp", "taxpayer", "assembly_decision"].includes(key);
          return (
            <div key={key}>
              <label className="block text-[11px] font-bold text-gray-500 uppercase tracking-wider mb-1.5">
                {FIELD_LABELS[key]}
              </label>
              {isLong ? (
                <textarea
                  value={form[key]}
                  onChange={set(key)}
                  rows={3}
                  className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-brand-blue focus:ring-1 focus:ring-brand-blue"
                />
              ) : (
                <input
                  type="text"
                  value={form[key]}
                  onChange={set(key)}
                  className="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-brand-blue focus:ring-1 focus:ring-brand-blue"
                />
              )}
            </div>
          );
        })}
      </div>
    </DialogShell>
  );
}

function UploadDialog({
  onClose, onDone,
}: {
  onClose: () => void;
  onDone: () => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<TPDisputeUploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const pickFile = (f: File | undefined | null) => {
    if (!f) return;
    const lower = f.name.toLowerCase();
    if (!lower.endsWith(".xlsx") && !lower.endsWith(".xlsm") && !lower.endsWith(".csv")) {
      setError("Format tidak didukung. Gunakan .xlsx atau .csv.");
      return;
    }
    setError(null);
    setFile(f);
  };

  const handleUpload = async () => {
    if (!file) return;
    setBusy(true);
    setError(null);
    try {
      const res = await uploadTPDisputes(file);
      setResult(res);
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Upload gagal.");
    } finally {
      setBusy(false);
    }
  };

  if (result) {
    return (
      <DialogShell
        title="Upload Selesai"
        onClose={onDone}
        footer={
          <button onClick={onDone} className="px-4 py-2 text-sm font-semibold bg-brand-green text-white rounded-lg hover:bg-brand-dark">
            Tutup
          </button>
        }
      >
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 rounded-lg bg-green-50 border border-green-100">
            <span className="text-sm font-medium text-green-800">Berhasil ditambahkan</span>
            <span className="text-lg font-bold text-green-700">{result.created}</span>
          </div>
          <div className="flex items-center justify-between p-3 rounded-lg bg-amber-50 border border-amber-100">
            <span className="text-sm font-medium text-amber-800">Dilewati (duplikat No. Putusan)</span>
            <span className="text-lg font-bold text-amber-700">{result.skipped}</span>
          </div>
          {result.errors.length > 0 && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-100">
              <p className="text-xs font-bold text-red-700 uppercase tracking-wider mb-2">Peringatan</p>
              <ul className="text-xs text-red-700 space-y-1 list-disc list-inside">
                {result.errors.slice(0, 10).map((e, i) => <li key={i}>{e}</li>)}
                {result.errors.length > 10 && <li>…dan {result.errors.length - 10} lainnya</li>}
              </ul>
            </div>
          )}
        </div>
      </DialogShell>
    );
  }

  return (
    <DialogShell
      title="Tambah dari Excel / CSV"
      onClose={onClose}
      footer={
        <>
          <button onClick={onClose} className="px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-100 rounded-lg">
            Batal
          </button>
          <button
            onClick={handleUpload}
            disabled={!file || busy}
            className="flex items-center gap-2 px-4 py-2 text-sm font-semibold bg-brand-green text-white rounded-lg hover:bg-brand-dark disabled:opacity-50"
          >
            {busy ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            Upload
          </button>
        </>
      }
    >
      <p className="text-sm text-gray-600 mb-4">
        Upload file <span className="font-semibold">.xlsx</span> atau <span className="font-semibold">.csv</span>.
        Baris dengan <span className="font-mono text-xs bg-gray-100 px-1.5 py-0.5 rounded">verdict_number</span> yang sama dengan data existing akan dilewati secara otomatis.
      </p>

      <label
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          pickFile(e.dataTransfer.files?.[0]);
        }}
        className={`flex flex-col items-center justify-center border-2 border-dashed rounded-xl py-10 px-4 cursor-pointer transition-colors ${
          dragOver ? "border-brand-green bg-brand-green/5" : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
        }`}
      >
        <FileSpreadsheet className="w-10 h-10 text-gray-400 mb-2" />
        <span className="text-sm font-medium text-gray-700">
          {file ? file.name : "Klik atau drop file di sini"}
        </span>
        <span className="text-xs text-gray-400 mt-1">.xlsx, .xlsm, atau .csv</span>
        <input
          type="file"
          accept=".xlsx,.xlsm,.csv"
          className="hidden"
          onChange={(e) => pickFile(e.target.files?.[0])}
        />
      </label>

      <details className="mt-5 text-xs text-gray-500">
        <summary className="cursor-pointer font-semibold hover:text-gray-700">Format kolom yang diharapkan</summary>
        <div className="mt-2 leading-relaxed">
          Baris pertama harus berisi header kolom. Kolom <code className="bg-gray-100 px-1 rounded">verdict_number</code> (atau <code className="bg-gray-100 px-1 rounded">No. Putusan</code>) wajib ada.
          Kolom lain yang dikenali: <code>name</code>/Nama, <code>verdict</code>/Amar Putusan, <code>dispute</code>/Pokok Sengketa, <code>legal_basis</code>/Dasar Hukum, <code>djp</code>/Menurut DJP, <code>taxpayer</code>/Menurut Wajib Pajak, <code>assembly_decision</code>/Keputusan Majelis.
        </div>
      </details>

      {error && (
        <div className="mt-4 p-3 rounded-lg bg-red-50 border border-red-100 text-sm text-red-700">{error}</div>
      )}
    </DialogShell>
  );
}

function ConfirmDialog({
  title, message, onCancel, onConfirm,
}: {
  title: string;
  message: string;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  return (
    <DialogShell
      title={title}
      onClose={onCancel}
      footer={
        <>
          <button onClick={onCancel} className="px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-100 rounded-lg">
            Batal
          </button>
          <button onClick={onConfirm} className="px-4 py-2 text-sm font-semibold bg-red-500 text-white rounded-lg hover:bg-red-600">
            Hapus
          </button>
        </>
      }
    >
      <p className="text-sm text-gray-600 leading-relaxed">{message}</p>
    </DialogShell>
  );
}