import React, { useEffect, useState } from "react";
import { PlusCircle, FolderOpen, Trash2, Clock } from "lucide-react";
import { listProjects, createProject, getProject, deleteProject } from "../api/projects";
import { useProjectStore } from "../store/projectStore";
import type { ProjectListItem } from "../types";

interface Props {
  onProjectSelected: () => void;
}

export function ProjectDashboard({ onProjectSelected }: Props) {
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
      <header className="bg-brand-grey text-white px-8 py-5 flex items-center gap-4">
        <div className="flex items-center gap-3 bg-white rounded-lg p-2">
          <img src="/rsm-logo.png" alt="RSM" className="h-8 w-auto" />
        </div>
        <div>
          <h1 className="font-bold text-lg leading-tight">TP Local File Generator</h1>
          <p className="text-xs text-white/70">PMK-172 · 2023 Compliant</p>
        </div>
      </header>

      {/* Content */}
      <main className="flex-1 px-8 py-8 max-w-5xl w-full mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Projects</h2>
            <p className="text-sm text-gray-500 mt-0.5">Select an existing project or create a new one</p>
          </div>
          <button
            onClick={() => { setShowModal(true); setNewName(""); }}
            className="flex items-center gap-2 px-4 py-2.5 bg-brand-green text-white text-sm font-medium rounded-lg hover:bg-brand-dark transition-colors"
          >
            <PlusCircle className="w-4 h-4" />
            New Project
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-16">
            <div className="w-8 h-8 border-4 border-brand-green/30 border-t-brand-green rounded-full animate-spin" />
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-xl border border-dashed border-gray-300">
            <FolderOpen className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 font-medium">No projects yet</p>
            <p className="text-sm text-gray-400 mt-1">Click "New Project" to get started</p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((p) => (
              <div
                key={p.id}
                className="bg-white rounded-xl border border-gray-200 p-5 hover:border-brand-green/40 hover:shadow-sm transition-all group"
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-gray-800 text-sm leading-snug line-clamp-2 flex-1 pr-2">
                    {p.name || "Untitled Project"}
                  </h3>
                  <button
                    onClick={() => setDeleteConfirm(p.id)}
                    className="text-gray-300 hover:text-red-400 transition-colors flex-shrink-0 opacity-0 group-hover:opacity-100"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex items-center gap-1 text-xs text-gray-400 mb-4">
                  <Clock className="w-3 h-3" />
                  <span>Updated {formatDate(p.updated_at)}</span>
                </div>
                <button
                  onClick={() => handleOpen(p.id)}
                  className="w-full py-2 text-xs font-medium bg-gray-50 hover:bg-brand-green hover:text-white text-gray-600 rounded-lg border border-gray-200 hover:border-brand-green transition-all"
                >
                  Open Project
                </button>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* New Project Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-bold text-gray-800 mb-1">New Project</h3>
            <p className="text-sm text-gray-500 mb-4">Give your project a name to get started</p>
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") handleCreate(); }}
              placeholder="e.g. PT Sumber Makmur 2024"
              autoFocus
              className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-green/50 focus:border-brand-green mb-4"
            />
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreate}
                disabled={!newName.trim() || creating}
                className="px-4 py-2 text-sm font-medium bg-brand-green text-white rounded-lg hover:bg-brand-dark disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {creating ? "Creating…" : "Create Project"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirm Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-sm">
            <h3 className="text-lg font-bold text-gray-800 mb-2">Delete Project?</h3>
            <p className="text-sm text-gray-500 mb-5">This action cannot be undone.</p>
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteConfirm)}
                className="px-4 py-2 text-sm font-medium bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
