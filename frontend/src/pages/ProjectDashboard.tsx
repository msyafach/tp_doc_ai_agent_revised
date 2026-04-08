import React, { useEffect, useState } from "react";
import { PlusCircle, FolderOpen, Trash2, Clock, LogOut, Shield } from "lucide-react";
import { listProjects, createProject, getProject, deleteProject } from "../api/projects";
import { useProjectStore } from "../store/projectStore";
import type { ProjectListItem } from "../types";

interface Props {
  onProjectSelected: () => void;
  onLogout: () => void;
  isAdmin: boolean;
  username: string;
  onAdminClick: () => void;
}

export function ProjectDashboard({ onProjectSelected, onLogout, isAdmin, username, onAdminClick }: Props) {
  const { setProjectId, setFullState } = useProjectStore();
  const [projects, setProjects] = useState<ProjectListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [newName, setNewName] = useState("");
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const fetchProjects = async () => {
    try {
      const list = await listProjects();
      setProjects(list);
    } catch {
      // backend not ready
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreate = async () => {
    if (!newName.trim()) return;
    setCreating(true);
    try {
      const proj = await createProject(newName.trim());
      setProjectId(proj.id);
      setFullState(proj.state);
      localStorage.setItem("tp_project_id", proj.id);
      setShowModal(false);
      onProjectSelected();
    } catch {
      alert("Failed to create project.");
    }
    setCreating(false);
  };

  const handleOpen = async (id: string) => {
    try {
      const proj = await getProject(id);
      setProjectId(proj.id);
      setFullState(proj.state);
      localStorage.setItem("tp_project_id", proj.id);
      onProjectSelected();
    } catch {
      alert("Failed to load project.");
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteProject(id);
      setProjects((prev) => prev.filter((p) => p.id !== id));
      if (localStorage.getItem("tp_project_id") === id) {
        localStorage.removeItem("tp_project_id");
      }
    } catch {
      alert("Failed to delete project.");
    }
    setDeleteConfirm(null);
  };

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-12 py-10 flex flex-col items-center text-center shadow-sm relative">
        {/* Top-right actions */}
        <div className="absolute top-4 right-6 flex items-center gap-2">
          {username && (
            <span className="text-xs font-semibold text-gray-400 px-3 py-1.5 bg-gray-50 rounded-full border border-gray-100">
              {username}
            </span>
          )}
          {isAdmin && (
            <button
              onClick={onAdminClick}
              className="flex items-center gap-1.5 text-xs font-semibold text-brand-blue bg-brand-blue/10 px-3 py-1.5 rounded-full border border-brand-blue/20 hover:bg-brand-blue/20 transition-all"
            >
              <Shield className="w-3.5 h-3.5" /> Admin
            </button>
          )}
          <button
            onClick={onLogout}
            className="flex items-center gap-1.5 text-xs font-semibold text-red-500 bg-red-50 px-3 py-1.5 rounded-full border border-red-100 hover:bg-red-100 transition-all"
          >
            <LogOut className="w-3.5 h-3.5" /> Sign Out
          </button>
        </div>

        <div className="mb-6 transform hover:scale-105 transition-transform duration-300">
          <img src="/rsm-logo.png" alt="RSM Logo" className="h-16 w-auto object-contain" />
        </div>
        <div className="max-w-2xl">
          <h1 className="font-extrabold text-3xl text-gray-900 tracking-tight leading-tight mb-2">
            RSM AI <span className="text-brand-green font-black">Tax Platform</span>
          </h1>
          <div className="flex items-center justify-center gap-3">
            <span className="h-px w-8 bg-gray-300"></span>
            <p className="text-sm font-semibold text-brand-blue uppercase tracking-[0.2em]">
              PMK-172 · 2023 Compliant
            </p>
            <span className="h-px w-8 bg-gray-300"></span>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="flex-1 px-8 py-12 max-w-6xl w-full mx-auto">
        <div className="flex items-end justify-between mb-10 border-b border-gray-200 pb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-3">
              <FolderOpen className="w-6 h-6 text-brand-blue" />
              Your Projects
            </h2>
            <p className="text-sm text-gray-500 mt-1">Manage and access your transfer pricing documentation projects</p>
          </div>
          <button
            onClick={() => { setShowModal(true); setNewName(""); }}
            className="flex items-center gap-2 px-6 py-3 bg-brand-green text-white text-sm font-bold rounded-xl hover:bg-brand-dark transition-all shadow-lg shadow-brand-green/20 active:scale-95"
          >
            <PlusCircle className="w-5 h-5" />
            NEW PROJECT
          </button>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <div className="w-12 h-12 border-4 border-brand-green/20 border-t-brand-green rounded-full animate-spin" />
            <p className="text-sm font-medium text-gray-400 animate-pulse">Retrieving your projects...</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-24 bg-white rounded-2xl border-2 border-dashed border-gray-200 shadow-sm">
            <div className="bg-gray-50 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
              <FolderOpen className="w-10 h-10 text-gray-300" />
            </div>
            <h3 className="text-xl font-bold text-gray-700 mb-2">No projects found</h3>
            <p className="text-gray-400 max-w-xs mx-auto mb-8">Get started by creating your first transfer pricing project.</p>
            <button
              onClick={() => { setShowModal(true); setNewName(""); }}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 text-white text-sm font-bold rounded-xl hover:bg-black transition-all"
            >
              <PlusCircle className="w-4 h-4" />
              CREATE FIRST PROJECT
            </button>
          </div>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((p) => (
              <div
                key={p.id}
                className="bg-white rounded-2xl border border-gray-100 p-6 hover:border-brand-blue/30 hover:shadow-xl hover:shadow-gray-200/50 transition-all group relative overflow-hidden flex flex-col"
              >
                <div className="absolute top-0 left-0 w-1 h-full bg-brand-blue opacity-0 group-hover:opacity-100 transition-opacity" />
                
                <div className="flex items-start justify-between mb-4">
                  <div className="p-2 bg-gray-50 rounded-lg group-hover:bg-brand-blue/5 transition-colors">
                    <FolderOpen className="w-5 h-5 text-gray-400 group-hover:text-brand-blue transition-colors" />
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); setDeleteConfirm(p.id); }}
                    className="text-gray-300 hover:text-red-500 transition-colors p-1 opacity-0 group-hover:opacity-100"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <h3 className="font-bold text-gray-900 text-lg leading-tight mb-2 group-hover:text-brand-blue transition-colors line-clamp-2">
                  {p.name || "Untitled Project"}
                </h3>

                <div className="flex items-center gap-2 text-xs font-medium text-gray-400 mt-auto pt-4 border-t border-gray-50">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Last updated: {formatDate(p.updated_at)}</span>
                </div>

                <button
                  onClick={() => handleOpen(p.id)}
                  className="mt-6 w-full py-3 text-xs font-bold bg-gray-50 hover:bg-brand-green text-gray-600 hover:text-white rounded-xl border border-gray-200 hover:border-brand-green transition-all uppercase tracking-wider"
                >
                  OPEN PROJECT
                </button>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="py-8 px-8 text-center border-t border-gray-100">
        <p className="text-xs text-gray-400 font-medium">
          &copy; {new Date().getFullYear()} RSM Indonesia · Professional Services Automation
        </p>
      </footer>

      {/* New Project Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md border border-gray-100">
            <div className="w-12 h-12 bg-brand-green/10 rounded-xl flex items-center justify-center mb-6">
              <PlusCircle className="w-6 h-6 text-brand-green" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">New Project</h3>
            <p className="text-sm text-gray-500 mb-8 leading-relaxed">
              Initialize a new transfer pricing local file. You can always rename it later in settings.
            </p>
            
            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2 ml-1">
              Project Name
            </label>
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") handleCreate(); }}
              placeholder="e.g. PT Example Indonesia 2024"
              autoFocus
              className="w-full border-2 border-gray-100 rounded-xl px-4 py-3.5 text-sm font-medium focus:outline-none focus:border-brand-green/50 focus:ring-4 focus:ring-brand-green/5 transition-all mb-8"
            />
            
            <div className="flex gap-3">
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 px-4 py-3.5 text-sm font-bold text-gray-500 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
              >
                CANCEL
              </button>
              <button
                onClick={handleCreate}
                disabled={!newName.trim() || creating}
                className="flex-1 px-4 py-3.5 text-sm font-bold bg-brand-green text-white rounded-xl hover:bg-brand-dark disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-brand-green/20"
              >
                {creating ? "CREATING..." : "CREATE PROJECT"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirm Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-sm border border-gray-100">
            <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center mb-6">
              <Trash2 className="w-6 h-6 text-red-500" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Delete Project?</h3>
            <p className="text-sm text-gray-500 mb-8 leading-relaxed">
              This will permanently remove the project and all its associated data. This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="flex-1 px-4 py-3.5 text-sm font-bold text-gray-500 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
              >
                CANCEL
              </button>
              <button
                onClick={() => handleDelete(deleteConfirm)}
                className="flex-1 px-4 py-3.5 text-sm font-bold bg-red-500 text-white rounded-xl hover:bg-red-600 transition-all shadow-lg shadow-red-500/20"
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
