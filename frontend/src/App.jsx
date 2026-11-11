import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import VendorManagement from './pages/VendorManagement';
import VendorDetail from './pages/VendorDetail';
import { LayoutDashboard, Users, Shield } from 'lucide-react';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex bg-slate-50">
        {/* Sidebar */}
        <aside className="w-64 bg-slate-900 text-white flex flex-col justify-between shrink-0">
          <div>
            <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
              <div className="p-2 bg-sky-500 rounded-lg text-white">
                <Shield className="w-6 h-6" />
              </div>
              <div>
                <div className="font-bold text-sm leading-tight text-white">Vendor Risk AI</div>
                <div className="text-[10px] text-sky-400 font-mono">Phase 2 Multi-Agent</div>
              </div>
            </div>

            <nav className="p-4 space-y-1">
              <Link
                to="/"
                className="flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition"
              >
                <LayoutDashboard className="w-4 h-4 text-sky-400" />
                <span>Executive Dashboard</span>
              </Link>
              <Link
                to="/vendors"
                className="flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 transition"
              >
                <Users className="w-4 h-4 text-emerald-400" />
                <span>Vendor Directory</span>
              </Link>
            </nav>
          </div>

          <div className="p-4 border-t border-slate-800 text-[11px] text-slate-400">
            <div className="font-semibold text-slate-300">VIT Pune IT Dept</div>
            <div>Academic Year 2026–2027</div>
            <div className="text-[10px] text-slate-500 mt-1">MFG006 + Multi-Agent RAG</div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col overflow-y-auto">
          <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between">
            <div className="text-xs font-semibold text-slate-500">
              AI-Assisted Vendor Risk Classification & Trust Assessment System
            </div>
            <div className="flex items-center space-x-3">
              <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-sky-50 text-sky-700 border border-sky-200">
                FastAPI v1.0 • Connected
              </span>
            </div>
          </header>

          <div className="p-8 max-w-7xl w-full mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/vendors" element={<VendorManagement />} />
              <Route path="/vendors/:id" element={<VendorDetail />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}
