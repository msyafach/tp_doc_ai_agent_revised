import React, { useEffect, useState } from "react";
import { UserPlus, Trash2, Shield, User as UserIcon } from "lucide-react";
import { getUsersApi, createUserApi, deleteUserApi } from "../api/auth";
import type { UserListItem } from "../api/auth";
import { useAuthStore } from "../store/authStore";

export function AdminUsersPage() {
  const currentUser = useAuthStore((s) => s.user);
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);
  const [form, setForm] = useState({ username: "", password: "", email: "", is_staff: false });
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const fetchUsers = async () => {
    try {
      setUsers(await getUsersApi());
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchUsers(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    setSubmitting(true);
    try {
      await createUserApi(form);
      setShowForm(false);
      setForm({ username: "", password: "", email: "", is_staff: false });
      await fetchUsers();
    } catch (err: any) {
      setFormError(err?.response?.data?.detail || "Failed to create user.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteUserApi(id);
      setUsers((prev) => prev.filter((u) => u.id !== id));
    } catch (err: any) {
      alert(err?.response?.data?.detail || "Failed to delete user.");
    }
    setDeleteConfirm(null);
  };

  const formatDate = (iso: string | null) => {
    if (!iso) return "Never";
    return new Date(iso).toLocaleDateString("en-GB", {
      day: "2-digit", month: "short", year: "numeric",
    });
  };

  return (
    <div className="px-8 py-10 max-w-4xl w-full mx-auto">
      {/* Header */}
      <div className="flex items-end justify-between mb-8 border-b border-gray-200 pb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-3">
            <Shield className="w-6 h-6 text-brand-blue" />
            User Management
          </h2>
          <p className="text-sm text-gray-500 mt-1">Manage platform users and admin access</p>
        </div>
        <button
          onClick={() => { setShowForm(true); setFormError(""); }}
          className="flex items-center gap-2 px-5 py-2.5 bg-brand-green text-white text-sm font-bold rounded-xl hover:bg-brand-dark transition-all shadow-lg shadow-brand-green/20 active:scale-95"
        >
          <UserPlus className="w-4 h-4" />
          ADD USER
        </button>
      </div>

      {/* User list */}
      {loading ? (
        <div className="flex justify-center py-20">
          <div className="w-10 h-10 border-4 border-brand-green/20 border-t-brand-green rounded-full animate-spin" />
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="text-left px-6 py-3.5 text-xs font-bold text-gray-400 uppercase tracking-wider">User</th>
                <th className="text-left px-6 py-3.5 text-xs font-bold text-gray-400 uppercase tracking-wider">Email</th>
                <th className="text-left px-6 py-3.5 text-xs font-bold text-gray-400 uppercase tracking-wider">Role</th>
                <th className="text-left px-6 py-3.5 text-xs font-bold text-gray-400 uppercase tracking-wider">Last Login</th>
                <th className="px-6 py-3.5" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50/50 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${u.is_staff ? "bg-brand-blue/10 text-brand-blue" : "bg-gray-100 text-gray-500"}`}>
                        {u.username[0]?.toUpperCase()}
                      </div>
                      <span className="font-semibold text-gray-800">{u.username}</span>
                      {u.id === currentUser?.id && (
                        <span className="text-[10px] font-bold text-brand-green bg-green-50 px-2 py-0.5 rounded-full border border-green-100">YOU</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-gray-500">{u.email || "—"}</td>
                  <td className="px-6 py-4">
                    {u.is_staff ? (
                      <span className="inline-flex items-center gap-1 text-xs font-bold text-brand-blue bg-brand-blue/10 px-2.5 py-1 rounded-full">
                        <Shield className="w-3 h-3" /> Admin
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs font-bold text-gray-500 bg-gray-100 px-2.5 py-1 rounded-full">
                        <UserIcon className="w-3 h-3" /> User
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-gray-400 text-xs">{formatDate(u.last_login)}</td>
                  <td className="px-6 py-4 text-right">
                    {u.id !== currentUser?.id && (
                      <button
                        onClick={() => setDeleteConfirm(u.id)}
                        className="text-gray-300 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100 p-1"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {users.length === 0 && (
            <div className="text-center py-12 text-gray-400 text-sm">No users found.</div>
          )}
        </div>
      )}

      {/* Add user modal */}
      {showForm && (
        <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md border border-gray-100">
            <div className="w-12 h-12 bg-brand-green/10 rounded-xl flex items-center justify-center mb-6">
              <UserPlus className="w-6 h-6 text-brand-green" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-1">Add New User</h3>
            <p className="text-sm text-gray-400 mb-6">Create a new platform account.</p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5">Username</label>
                <input
                  type="text" required autoFocus
                  value={form.username}
                  onChange={(e) => setForm({ ...form, username: e.target.value })}
                  className="w-full border-2 border-gray-100 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-brand-green/50 focus:ring-4 focus:ring-brand-green/5 transition-all"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5">Password</label>
                <input
                  type="password" required minLength={6}
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  placeholder="Min. 6 characters"
                  className="w-full border-2 border-gray-100 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-brand-green/50 focus:ring-4 focus:ring-brand-green/5 transition-all"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5">Email (optional)</label>
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full border-2 border-gray-100 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-brand-green/50 focus:ring-4 focus:ring-brand-green/5 transition-all"
                />
              </div>
              <label className="flex items-center gap-3 cursor-pointer py-1">
                <input
                  type="checkbox"
                  checked={form.is_staff}
                  onChange={(e) => setForm({ ...form, is_staff: e.target.checked })}
                  className="w-4 h-4 rounded accent-brand-green"
                />
                <span className="text-sm font-medium text-gray-700">Grant admin access</span>
              </label>

              {formError && (
                <div className="rounded-xl bg-red-50 border border-red-100 px-4 py-3 text-sm text-red-600 font-medium">
                  {formError}
                </div>
              )}

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="flex-1 px-4 py-3 text-sm font-bold text-gray-500 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                >
                  CANCEL
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 px-4 py-3 text-sm font-bold bg-brand-green text-white rounded-xl hover:bg-brand-dark disabled:opacity-50 transition-all shadow-lg shadow-brand-green/20"
                >
                  {submitting ? "CREATING…" : "CREATE USER"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete confirm modal */}
      {deleteConfirm !== null && (
        <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-sm border border-gray-100">
            <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center mb-6">
              <Trash2 className="w-6 h-6 text-red-500" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Delete User?</h3>
            <p className="text-sm text-gray-500 mb-8">This action cannot be undone.</p>
            <div className="flex gap-3">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="flex-1 px-4 py-3 text-sm font-bold text-gray-500 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
              >
                CANCEL
              </button>
              <button
                onClick={() => handleDelete(deleteConfirm)}
                className="flex-1 px-4 py-3 text-sm font-bold bg-red-500 text-white rounded-xl hover:bg-red-600 transition-all shadow-lg shadow-red-500/20"
              >
                DELETE
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
