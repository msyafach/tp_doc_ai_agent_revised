import React, { useState } from "react";
import { loginApi } from "../api/auth";
import { useAuthStore } from "../store/authStore";

interface Props {
  onLogin: () => void;
}

export function LoginPage({ onLogin }: Props) {
  const { login } = useAuthStore();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { access, refresh, user } = await loginApi(username, password);
      login(access, refresh, user);
      onLogin();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Invalid username or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen mesh-gradient grainy-texture flex flex-col items-center justify-center px-4 overflow-hidden relative">
      {/* Card */}
      <div className="w-full max-w-sm bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl shadow-gray-200/40 border border-white/50 p-10 relative z-10 transition-all duration-500">
        {/* Logo */}
        <div className="flex justify-center mb-10 transform hover:scale-105 transition-transform duration-300">
          <img src="/rsm-logo.png" alt="RSM Logo" className="h-14 w-auto object-contain" />
        </div>

        {/* Heading */}
        <div className="text-center mb-10">
          <h1 className="text-2xl font-black text-gray-900 tracking-tight leading-tight">
            RSM AI <span className="text-brand-green">Tax Platform</span>
          </h1>
          <p className="mt-2 text-xs font-bold text-gray-400 uppercase tracking-widest">Secure Document Portal</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="block text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] ml-1">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoFocus
              required
              className="w-full border-2 border-gray-100/50 bg-gray-50/50 rounded-2xl px-5 py-3.5 text-sm font-medium text-gray-800 placeholder-gray-300 focus:outline-none focus:border-brand-green/30 focus:bg-white focus:ring-4 focus:ring-brand-green/5 transition-all"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] ml-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full border-2 border-gray-100/50 bg-gray-50/50 rounded-2xl px-5 py-3.5 text-sm font-medium text-gray-800 placeholder-gray-300 focus:outline-none focus:border-brand-green/30 focus:bg-white focus:ring-4 focus:ring-brand-green/5 transition-all"
            />
          </div>

          {error && (
            <div className="rounded-2xl bg-red-50 border border-red-100 px-5 py-4 text-xs text-red-600 font-bold flex items-center gap-2 animate-in slide-in-from-top-2">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !username.trim() || !password.trim()}
            className="w-full py-4 text-xs font-black bg-brand-green text-white rounded-2xl hover:bg-brand-dark disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-xl shadow-brand-green/20 active:scale-[0.98] uppercase tracking-[0.2em] mt-2"
          >
            {loading ? "Authenticating..." : "SIGN IN TO PORTAL"}
          </button>
        </form>
      </div>

      {/* Footer */}
      <div className="mt-12 text-center relative z-10">
        <p className="text-[10px] font-black text-gray-400 uppercase tracking-[0.3em]">
          &copy; {new Date().getFullYear()} RSM Indonesia · Professional Services Automation
        </p>
      </div>
    </div>
  );
}
