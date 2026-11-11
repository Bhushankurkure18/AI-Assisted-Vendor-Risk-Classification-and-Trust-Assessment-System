import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getVendors, createVendor } from '../services/api';
import RiskBadge from '../components/RiskBadge';
import { Plus, Building2, Search, X } from 'lucide-react';

export default function VendorManagement() {
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Form state
  const [formData, setFormData] = useState({
    vendor_name: '',
    revenue: 5000000,
    debt: 1000000,
    financial_score: 35.0,
    security_score: 40.0,
    compliance_score: 30.0,
    operational_score: 35.0,
    reputation_score: 25.0,
  });

  const loadVendors = () => {
    setLoading(true);
    getVendors()
      .then(data => setVendors(data || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadVendors();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createVendor({
        vendor_name: formData.vendor_name,
        revenue: Number(formData.revenue),
        debt: Number(formData.debt),
        financial_score: Number(formData.financial_score),
        security_score: Number(formData.security_score),
        compliance_score: Number(formData.compliance_score),
        operational_score: Number(formData.operational_score),
        reputation_score: Number(formData.reputation_score),
      });
      setShowModal(false);
      loadVendors();
    } catch (err) {
      alert('Failed to register vendor: ' + (err.response?.data?.detail || err.message));
    }
  };

  const filtered = vendors.filter(v =>
    v.vendor_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Vendor Management</h1>
          <p className="text-xs text-slate-500 mt-0.5">Register, inspect, and evaluate enterprise vendor profiles</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold rounded-lg shadow-sm transition"
        >
          <Plus className="w-4 h-4 mr-1.5" /> Register Vendor
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
        <input
          type="text"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          placeholder="Search vendors by name..."
          className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-sky-500"
        />
      </div>

      {/* Vendor Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Loading vendors...</div>
        ) : filtered.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-sm">No matching vendors found.</div>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
              <tr>
                <th className="px-6 py-3">Vendor</th>
                <th className="px-6 py-3">Revenue ($)</th>
                <th className="px-6 py-3">Debt ($)</th>
                <th className="px-6 py-3">Scores (Fin/Sec/Comp/Ops/Rep)</th>
                <th className="px-6 py-3">Risk Level</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {filtered.map(v => (
                <tr key={v.vendor_id} className="hover:bg-slate-50">
                  <td className="px-6 py-3.5 font-medium text-slate-900 flex items-center space-x-2">
                    <Building2 className="w-4 h-4 text-slate-400" />
                    <div>
                      <div>{v.vendor_name}</div>
                      <div className="text-xs text-slate-400 font-mono">ID: {v.vendor_id}</div>
                    </div>
                  </td>
                  <td className="px-6 py-3.5 text-slate-600">${Number(v.revenue || 0).toLocaleString()}</td>
                  <td className="px-6 py-3.5 text-slate-600">${Number(v.debt || 0).toLocaleString()}</td>
                  <td className="px-6 py-3.5 text-xs text-slate-600 font-mono">
                    {v.financial_score?.toFixed(0)} / {v.security_score?.toFixed(0)} / {v.compliance_score?.toFixed(0)} / {v.operational_score?.toFixed(0)} / {v.reputation_score?.toFixed(0)}
                  </td>
                  <td className="px-6 py-3.5">
                    <RiskBadge level={v.risk_level} />
                  </td>
                  <td className="px-6 py-3.5 text-right">
                    <Link
                      to={`/vendors/${v.vendor_id}`}
                      className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-md transition"
                    >
                      View & Assess &rarr;
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Register Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6 space-y-4">
            <div className="flex justify-between items-center border-b pb-3">
              <h3 className="font-semibold text-slate-800 text-base">Register New Vendor</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Vendor Name</label>
                <input
                  type="text"
                  required
                  value={formData.vendor_name}
                  onChange={e => setFormData({ ...formData, vendor_name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-sky-500"
                  placeholder="e.g. Apex Cloud Solutions Inc."
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Annual Revenue ($)</label>
                  <input
                    type="number"
                    value={formData.revenue}
                    onChange={e => setFormData({ ...formData, revenue: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Total Debt ($)</label>
                  <input
                    type="number"
                    value={formData.debt}
                    onChange={e => setFormData({ ...formData, debt: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
              </div>

              <div className="text-xs font-semibold text-slate-600 pt-2 border-t">Baseline Dimension Scores (0 - 100)</div>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block text-[11px] text-slate-500">Financial</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={formData.financial_score}
                    onChange={e => setFormData({ ...formData, financial_score: e.target.value })}
                    className="w-full px-2 py-1.5 border rounded text-xs"
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-slate-500">Security</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={formData.security_score}
                    onChange={e => setFormData({ ...formData, security_score: e.target.value })}
                    className="w-full px-2 py-1.5 border rounded text-xs"
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-slate-500">Compliance</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={formData.compliance_score}
                    onChange={e => setFormData({ ...formData, compliance_score: e.target.value })}
                    className="w-full px-2 py-1.5 border rounded text-xs"
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-slate-500">Operational</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={formData.operational_score}
                    onChange={e => setFormData({ ...formData, operational_score: e.target.value })}
                    className="w-full px-2 py-1.5 border rounded text-xs"
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-slate-500">Reputation</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={formData.reputation_score}
                    onChange={e => setFormData({ ...formData, reputation_score: e.target.value })}
                    className="w-full px-2 py-1.5 border rounded text-xs"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-lg text-xs font-semibold"
                >
                  Save Vendor
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

