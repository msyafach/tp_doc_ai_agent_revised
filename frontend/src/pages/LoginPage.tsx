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
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
      {/* Card */}
      <div className="w-full max-w-sm bg-white rounded-2xl shadow-xl shadow-gray-200/60 border border-gray-100 p-10">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <img src="/rsm-logo.png" alt="RSM Logo" className="h-12 w-auto object-contain" />
        </div>

        {/* Heading */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
            RSM AI <span className="text-brand-green">Tax Platform</span>
          </h1>
          <p className="mt-1.5 text-sm text-gray-400 font-medium">Sign in to your account</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5 ml-0.5">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoFocus
              required
              placeholder="Enter username"
              className="w-full border-2 border-gray-100 rounded-xl px-4 py-3 text-sm font-medium text-gray-800 placeholder-gray-300 focus:outline-none focus:border-brand-green/50 focus:ring-4 focus:ring-brand-green/5 transition-all"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1.5 ml-0.5">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter password"
              className="w-full border-2 border-gray-100 rounded-xl px-4 py-3 text-sm font-medium text-gray-800 placeholder-gray-300 focus:outline-none focus:border-brand-green/50 focus:ring-4 focus:ring-brand-green/5 transition-all"
            />
          </div>

          {error && (
            <div className="rounded-xl bg-red-50 border border-red-100 px-4 py-3 text-sm text-red-600 font-medium">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !username.trim() || !password.trim()}
            className="w-full py-3.5 text-sm font-bold bg-brand-green text-white rounded-xl hover:bg-brand-dark disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-brand-green/20 active:scale-[0.98] mt-2"
          >
            {loading ? "Signing in…" : "SIGN IN"}
          </button>
        </form>
      </div>

      {/* Footer */}
      <p className="mt-8 text-xs text-gray-400 font-medium">
        &copy; {new Date().getFullYear()} RSM Indonesia · Professional Services Automation
      </p>
    </div>
  );
}
