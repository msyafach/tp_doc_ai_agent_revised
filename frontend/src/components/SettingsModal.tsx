import React, { useState } from "react";
import { Eye, EyeOff, X, Check } from "lucide-react";
import { useProjectStore } from "../store/projectStore";
import type { ApiSettings } from "../types";

const GROQ_MODELS = [
  "llama-3.3-70b-versatile",
  "deepseek-r1-distill-llama-70b",
  "llama-3.1-8b-instant",
  "mixtral-8x7b-32768",
];
const OPENAI_MODEL = "gpt-5.4-nano";

const LS_KEY = "tp_api_settings";

interface Props {
  onClose: () => void;
}

export function SettingsModal({ onClose }: Props) {
  const { apiSettings, setApiSettings } = useProjectStore();

  // Local draft state — only committed on Save
  const [draft, setDraft] = useState<ApiSettings>({ ...apiSettings });
  const [showKey, setShowKey] = useState(false);
  const [showTavily, setShowTavily] = useState(false);
  const [showLangsmith, setShowLangsmith] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleProviderChange = (provider: "groq" | "openai") => {
    const defaultModel = provider === "groq" ? GROQ_MODELS[0] : OPENAI_MODEL;
    setDraft((d) => ({ ...d, llm_provider: provider, model: defaultModel }));
  };

  const handleSave = () => {
    setApiSettings(draft);
    localStorage.setItem(LS_KEY, JSON.stringify(draft));
    setSaved(true);
    setTimeout(() => {
      setSaved(false);
      onClose();
    }, 800);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="text-base font-bold text-gray-800">API Settings</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-5">
          {/* Provider */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              LLM Provider
            </label>
            <div className="flex gap-2">
              {(["groq", "openai"] as const).map((p) => (
                <button
                  key={p}
                  onClick={() => handleProviderChange(p)}
                  className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium border transition-all ${
                    draft.llm_provider === p
                      ? "bg-brand-green text-white border-brand-green"
                      : "bg-white text-gray-600 border-gray-300 hover:border-brand-green/50"
                  }`}
                >
                  {p === "groq" ? "Groq (Llama)" : "OpenAI (GPT)"}
                </button>
              ))}
            </div>
          </div>

          {/* Model */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Model
            </label>
            {draft.llm_provider === "groq" ? (
              <select
                value={draft.model}
                onChange={(e) => setDraft((d) => ({ ...d, model: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-brand-green/40 focus:border-brand-green"
              >
                {GROQ_MODELS.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            ) : (
              <div className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-500 bg-gray-50">
                {OPENAI_MODEL}
              </div>
            )}
          </div>

          {/* API Key */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              {draft.llm_provider === "groq" ? "Groq" : "OpenAI"} API Key
            </label>
            <div className="relative">
              <input
                type={showKey ? "text" : "password"}
                value={draft.api_key}
                onChange={(e) => setDraft((d) => ({ ...d, api_key: e.target.value }))}
                placeholder="sk-..."
                className="w-full border border-gray-300 rounded-lg px-3 py-2 pr-10 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-green/40 focus:border-brand-green"
              />
              <button
                type="button"
                onClick={() => setShowKey((v) => !v)}
                className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
              >
                {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Tavily Key */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Tavily API Key
              <span className="ml-1.5 text-xs font-normal text-gray-400">(for web search)</span>
            </label>
            <div className="relative">
              <input
                type={showTavily ? "text" : "password"}
                value={draft.tavily_key}
                onChange={(e) => setDraft((d) => ({ ...d, tavily_key: e.target.value }))}
                placeholder="tvly-..."
                className="w-full border border-gray-300 rounded-lg px-3 py-2 pr-10 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-green/40 focus:border-brand-green"
              />
              <button
                type="button"
                onClick={() => setShowTavily((v) => !v)}
                className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
              >
                {showTavily ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <p className="mt-1.5 text-xs text-gray-400">
              Get a free key at{" "}
              <span className="text-brand-green font-medium">tavily.com</span>
            </p>
          </div>

          {/* LangSmith section */}
          <div className="rounded-lg border border-purple-100 bg-purple-50/50 p-4 space-y-4">
            <div>
              <p className="text-xs font-semibold text-purple-700 uppercase tracking-wide">LangSmith Tracing</p>
              <p className="text-xs text-gray-500 mt-0.5">Optional — logs all agent runs to LangSmith for observability</p>
            </div>

            {/* LangSmith API Key */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                LangSmith API Key
                <span className="ml-1.5 text-xs font-normal text-gray-400">(optional)</span>
              </label>
              <div className="relative">
                <input
                  type={showLangsmith ? "text" : "password"}
                  value={draft.langsmith_api_key}
                  onChange={(e) => setDraft((d) => ({ ...d, langsmith_api_key: e.target.value }))}
                  placeholder="lsv2_..."
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 pr-10 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400/40 focus:border-purple-400"
                />
                <button
                  type="button"
                  onClick={() => setShowLangsmith((v) => !v)}
                  className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
                >
                  {showLangsmith ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* LangSmith Project */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                LangSmith Project Name
              </label>
              <input
                type="text"
                value={draft.langsmith_project}
                onChange={(e) => setDraft((d) => ({ ...d, langsmith_project: e.target.value }))}
                placeholder="tp-local-file-generator"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400/40 focus:border-purple-400"
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-100 flex gap-2 justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-5 py-2 text-sm font-medium bg-brand-green text-white rounded-lg hover:bg-brand-dark transition-colors"
          >
            {saved ? (
              <>
                <Check className="w-4 h-4" />
                Saved!
              </>
            ) : (
              "Save Settings"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
