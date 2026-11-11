import React from 'react';
import { FileText, FileCode, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';

export default function DocumentCard({ doc, onChunk }) {
  const isProcessed = doc.processing_status === 'COMPLETED';
  const isFailed = doc.processing_status === 'FAILED';

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:shadow transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-sky-50 text-sky-600 rounded-lg">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-800 truncate max-w-xs" title={doc.original_filename}>
              {doc.original_filename}
            </h4>
            <div className="flex items-center space-x-2 text-xs text-slate-500 mt-0.5">
              <span>{doc.file_type.toUpperCase()}</span>
              <span>•</span>
              <span>{doc.page_count} page{doc.page_count > 1 ? 's' : ''}</span>
              <span>•</span>
              <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-1.5">
          {isProcessed ? (
            <span className="inline-flex items-center text-xs text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full font-medium border border-emerald-200">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Ready
            </span>
          ) : isFailed ? (
            <span className="inline-flex items-center text-xs text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full font-medium border border-rose-200">
              <AlertTriangle className="w-3.5 h-3.5 mr-1" /> Error
            </span>
          ) : (
            <span className="inline-flex items-center text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full font-medium border border-amber-200">
              <Clock className="w-3.5 h-3.5 mr-1 animate-spin" /> {doc.processing_status}
            </span>
          )}
        </div>
      </div>

      {onChunk && (
        <div className="mt-3 pt-3 border-t border-slate-100 flex justify-end">
          <button
            onClick={() => onChunk(doc.document_id)}
            className="text-xs font-medium text-sky-600 hover:text-sky-800 flex items-center space-x-1"
          >
            <FileCode className="w-3.5 h-3.5" />
            <span>Generate Chunks & Embeddings</span>
          </button>
        </div>
      )}
    </div>
  );
}

