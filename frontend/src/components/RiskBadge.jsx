import React from 'react';

export default function RiskBadge({ level }) {
  const norm = (level || 'UNKNOWN').toUpperCase();

  let colorClasses = 'bg-slate-100 text-slate-700 border-slate-300';
  if (norm === 'LOW') {
    colorClasses = 'bg-emerald-50 text-emerald-700 border-emerald-300';
  } else if (norm === 'MEDIUM') {
    colorClasses = 'bg-amber-50 text-amber-700 border-amber-300';
  } else if (norm === 'HIGH') {
    colorClasses = 'bg-rose-50 text-rose-700 border-rose-300';
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${colorClasses}`}
    >
      {norm}
    </span>
  );
}

