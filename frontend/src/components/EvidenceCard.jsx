import React from 'react';
import { BookOpen, MapPin } from 'lucide-react';

export default function EvidenceCard({ evidence }) {
  return (
    <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs">
      <div className="flex items-center justify-between text-slate-500 mb-1.5">
        <span className="font-semibold text-slate-700 flex items-center">
          <BookOpen className="w-3.5 h-3.5 mr-1 text-sky-600" />
          {evidence.filename || 'Source Document'}
        </span>
        <span className="flex items-center text-slate-500 bg-white border border-slate-200 px-1.5 py-0.5 rounded text-[11px]">
          <MapPin className="w-3 h-3 mr-0.5 text-slate-400" />
          Page {evidence.page_number} • {evidence.section}
        </span>
      </div>
      <p className="text-slate-800 italic bg-white p-2.5 rounded border border-slate-100 leading-relaxed font-serif">
        "{evidence.quoted_text}"
      </p>
      {evidence.distance !== undefined && (
        <div className="mt-1.5 text-right text-[10px] text-slate-400">
          Cosine Distance: {Number(evidence.distance).toFixed(3)}
        </div>
      )}
    </div>
  );
}

