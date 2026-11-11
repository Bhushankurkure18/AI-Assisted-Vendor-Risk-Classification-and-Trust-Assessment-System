import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getVendors } from '../services/api';
import RiskBadge from '../components/RiskBadge';
import { Building2, ShieldCheck, AlertCircle, TrendingUp, Users } from 'lucide-react';

export default function Dashboard() {
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getVendors()
      .then(data => setVendors(data || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const total = vendors.length;
  const lowCount = vendors.filter(v => v.risk_level === 'LOW').length;
  const medCount = vendors.filter(v => v.risk_level === 'MEDIUM').length;
  const highCount = vendors.filter(v => v.risk_level === 'HIGH').length;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-sky-900 via-sky-800 to-indigo-900 rounded-2xl p-6 text-white shadow-md">
        <h1 className="text-2xl font-bold">AI-Assisted Vendor Risk Classification & Trust Platform</h1>
        <p className="text-sky-200 text-sm mt-1">
          Academic Engineering Prototype • VIT Pune IT Dept (2026–2027) • Multi-Agent RAG & Quantitative ML Pipeline
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="p-3 bg-sky-50 text-sky-600 rounded-lg">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-800">{total}</div>
            <div className="text-xs text-slate-500 font-medium">Total Registered Vendors</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-emerald-700">{lowCount}</div>
            <div className="text-xs text-slate-500 font-medium">Low Risk Vendors</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="p-3 bg-amber-50 text-amber-600 rounded-lg">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-amber-700">{medCount}</div>
            <div className="text-xs text-slate-500 font-medium">Medium Risk Vendors</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="p-3 bg-rose-50 text-rose-600 rounded-lg">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-rose-700">{highCount}</div>
            <div className="text-xs text-slate-500 font-medium">High Risk Vendors</div>
          </div>
        </div>
      </div>

      {/* Vendor Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center">
          <h2 className="text-base font-semibold text-slate-800">Monitored Vendors</h2>
          <Link
            to="/vendors"
            className="text-xs font-semibold text-sky-600 hover:text-sky-800"
          >
            Manage Vendors &rarr;
          </Link>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Loading vendor registry...</div>
        ) : vendors.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">No vendors found. Register one in Vendor Management.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3">ID</th>
                  <th className="px-6 py-3">Vendor Name</th>
                  <th className="px-6 py-3">Financial</th>
                  <th className="px-6 py-3">Security</th>
                  <th className="px-6 py-3">Compliance</th>
                  <th className="px-6 py-3">Operational</th>
                  <th className="px-6 py-3">Risk Level</th>
                  <th className="px-6 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {vendors.map(v => (
                  <tr key={v.vendor_id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-3.5 font-mono text-xs text-slate-500">#{v.vendor_id}</td>
                    <td className="px-6 py-3.5 font-medium text-slate-900 flex items-center space-x-2">
                      <Building2 className="w-4 h-4 text-slate-400" />
                      <span>{v.vendor_name}</span>
                    </td>
                    <td className="px-6 py-3.5 text-slate-600">{v.financial_score?.toFixed(1)}</td>
                    <td className="px-6 py-3.5 text-slate-600">{v.security_score?.toFixed(1)}</td>
                    <td className="px-6 py-3.5 text-slate-600">{v.compliance_score?.toFixed(1)}</td>
                    <td className="px-6 py-3.5 text-slate-600">{v.operational_score?.toFixed(1)}</td>
                    <td className="px-6 py-3.5">
                      <RiskBadge level={v.risk_level} />
                    </td>
                    <td className="px-6 py-3.5 text-right">
                      <Link
                        to={`/vendors/${v.vendor_id}`}
                        className="inline-flex items-center text-xs font-semibold text-sky-600 hover:text-sky-800"
                      >
                        Deep Risk Analysis &rarr;
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

