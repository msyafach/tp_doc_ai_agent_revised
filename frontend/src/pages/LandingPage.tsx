import React from "react";
import { 
  ArrowRight, 
  Sparkles, 
  ShieldCheck, 
  FileText, 
  ChevronRight,
  PlusCircle,
  LayoutDashboard
} from "lucide-react";

interface Props {
  onStart: () => void;
  onNewProject: () => void;
  companyName?: string;
  isAuthenticated?: boolean;
}

export function LandingPage({ onStart, onNewProject, companyName, isAuthenticated }: Props) {
  return (
    <div className="min-h-screen bg-white overflow-x-hidden">
      {/* Navigation Header */}
      <nav className="fixed top-0 left-0 right-0 z-50 px-8 py-6 flex items-center justify-between backdrop-blur-md bg-white/30 border-b border-white/20">
        <div className="flex items-center gap-3">
          <img src="/rsm-logo.png" alt="RSM Logo" className="h-10 w-auto" />
          <div className="h-6 w-px bg-gray-200" />
          <span className="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em]">Tax Platform</span>
        </div>
        
        <div className="flex items-center gap-6">
          {isAuthenticated ? (
            <button
              onClick={onStart}
              className="px-6 py-2.5 bg-gray-900 text-white rounded-xl font-black text-[10px] tracking-widest hover:bg-black transition-all shadow-lg active:scale-95"
            >
              GO TO DASHBOARD
            </button>
          ) : (
            <button
              onClick={onStart}
              className="px-6 py-2.5 bg-brand-green text-white rounded-xl font-black text-[10px] tracking-widest hover:bg-brand-dark transition-all shadow-lg shadow-brand-green/20 active:scale-95"
            >
              SIGN IN
            </button>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-48 px-6 overflow-hidden min-h-[90vh] flex items-center">
        {/* Background Image with Overlay */}
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1497215728101-856f4ea42174?q=80&w=2070&auto=format&fit=crop" 
            alt="Background" 
            className="w-full h-full object-cover opacity-40 scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-white/90 via-white/40 to-white mesh-gradient opacity-60" />
        </div>

        <div className="max-w-7xl mx-auto relative z-10 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-brand-green/10 border border-brand-green/20 mb-10 animate-in fade-in slide-in-from-bottom-4 duration-700 backdrop-blur-sm">
            <Sparkles className="w-4 h-4 text-brand-green" />
            <span className="text-[10px] font-black text-brand-green uppercase tracking-[0.2em]">The Future of Tax Compliance</span>
          </div>
          
          <h1 className="text-6xl md:text-8xl font-black text-gray-900 tracking-tighter leading-[0.95] mb-10 animate-in fade-in slide-in-from-bottom-6 duration-1000">
            Intelligent <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-green via-brand-blue to-brand-green bg-[length:200%_auto] animate-gradient-x">
              Transfer Pricing.
            </span>
          </h1>
          
          <p className="max-w-2xl mx-auto text-lg md:text-xl text-gray-600 font-medium mb-14 leading-relaxed animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-200">
            Generate audit-ready TP Local Files in minutes. Our AI-driven engine automates data extraction and analysis for seamless PMK-172 compliance.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 animate-in fade-in slide-in-from-bottom-10 duration-1000 delay-300">
            <button
              onClick={onStart}
              className="group px-10 py-5 bg-gray-900 text-white rounded-2xl font-black text-xs tracking-[0.2em] hover:bg-black transition-all shadow-2xl shadow-gray-400 flex items-center gap-4 active:scale-95"
            >
              LAUNCH PLATFORM
              <LayoutDashboard className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
            <button
              onClick={onNewProject}
              className="px-10 py-5 bg-white text-brand-green border-2 border-brand-green/20 rounded-2xl font-black text-xs tracking-[0.2em] hover:bg-brand-green hover:text-white transition-all active:scale-95 shadow-xl shadow-brand-green/5 backdrop-blur-md"
            >
              START NEW PROJECT
            </button>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 px-6 bg-white relative z-20 -mt-10 rounded-t-[3rem] border-t border-gray-100 shadow-[0_-20px_50px_rgba(0,0,0,0.02)]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-[10px] font-black text-brand-blue uppercase tracking-[0.4em] mb-4">Core Capabilities</h2>
            <h3 className="text-3xl font-black text-gray-900 tracking-tight">Enterprise-Grade Automation</h3>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<Sparkles className="w-6 h-6" />}
              title="AI Extraction"
              description="Upload your source documents and let our AI agents extract entity info, shareholders, and financial data automatically."
              color="bg-purple-50 text-purple-600"
            />
            <FeatureCard 
              icon={<ShieldCheck className="w-6 h-6" />}
              title="Regulatory Compliance"
              description="Fully aligned with PMK-172 (2023) standards. Every generated file meets Indonesian tax authority requirements."
              color="bg-brand-green/10 text-brand-green"
            />
            <FeatureCard 
              icon={<FileText className="w-6 h-6" />}
              title="Seamless Export"
              description="Review your analysis and export professional documentation formats with a single click."
              color="bg-brand-blue/10 text-brand-blue"
            />
          </div>
        </div>
      </section>

      {/* Trust Banner */}
      <section className="py-16 border-y border-gray-50 bg-gray-50/30">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-8 opacity-60">
          <div className="flex items-center gap-4 grayscale opacity-70">
            <img src="/rsm-logo.png" alt="RSM Logo" className="h-10 w-auto" />
            <div className="h-8 w-px bg-gray-300" />
            <span className="text-sm font-black uppercase tracking-widest text-gray-400">Professional Services</span>
          </div>
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest text-center md:text-right">
            SECURE · PRIVATE · COMPLIANT · RSM INDONESIA
          </p>
        </div>
      </section>

      {/* CTA Footer */}
      <section className="py-32 px-6 text-center overflow-hidden relative">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070&auto=format&fit=crop" 
            alt="Office Building" 
            className="w-full h-full object-cover opacity-10"
          />
          <div className="absolute inset-0 bg-white opacity-80" />
        </div>

        <div className="max-w-4xl mx-auto bg-gray-900 rounded-[3rem] p-16 md:p-24 shadow-2xl relative overflow-hidden group z-10">
          <div className="absolute top-0 right-0 w-96 h-96 bg-brand-green opacity-10 blur-[100px] group-hover:opacity-20 transition-opacity" />
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-brand-blue opacity-10 blur-[100px] group-hover:opacity-20 transition-opacity" />
          
          <h2 className="text-4xl md:text-5xl font-black text-white tracking-tighter mb-8 relative z-10 leading-tight">
            Ready to automate your <br /> documentation?
          </h2>
          <p className="text-gray-400 font-medium text-lg mb-12 relative z-10 max-w-xl mx-auto">
            Experience the precision of AI-driven compliance. Reduce manual analysis time by up to 80%.
          </p>
          <button
            onClick={onStart}
            className="inline-flex items-center gap-3 px-12 py-5 bg-brand-green text-white rounded-2xl font-black text-xs tracking-[0.2em] hover:bg-brand-dark transition-all shadow-2xl shadow-brand-green/30 active:scale-95 relative z-10"
          >
            GET STARTED NOW
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-gray-50 text-center">
        <p className="text-[10px] font-black text-gray-400 uppercase tracking-[0.3em]">
          &copy; {new Date().getFullYear()} RSM Indonesia · Professional Services Automation
        </p>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description, color }: { icon: React.ReactNode, title: string, description: string, color: string }) {
  return (
    <div className="p-8 rounded-[2rem] border border-gray-50 bg-white hover:border-brand-green/20 hover:shadow-2xl hover:shadow-gray-100 transition-all duration-500 group">
      <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-8 transition-transform group-hover:scale-110 duration-500 ${color}`}>
        {icon}
      </div>
      <h4 className="text-xl font-bold text-gray-900 mb-4 tracking-tight">{title}</h4>
      <p className="text-gray-500 font-medium leading-relaxed text-sm">
        {description}
      </p>
    </div>
  );
}
