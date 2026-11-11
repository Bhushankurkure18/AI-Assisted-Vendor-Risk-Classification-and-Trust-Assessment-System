import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  getVendor,
  getVendorDocuments,
  uploadDocument,
  chunkDocument,
  runAIAssessment,
  getLatestAIAssessment,
  askVendorDocumentation,
} from '../services/api';
import RiskBadge from '../components/RiskBadge';
import RiskRadarChart from '../components/RiskRadarChart';
import DocumentCard from '../components/DocumentCard';
import EvidenceCard from '../components/EvidenceCard';
import {
  Building2,
  Upload,
  Bot,
  MessageSquare,
  FileText,
  ShieldCheck,
  Cpu,
  ArrowLeft,
  CheckCircle,
} from 'lucide-react';

export default function VendorDetail() {
  const { id } = useParams();
  const [vendor, setVendor] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [assessment, setAssessment] = useState(null);
  const [activeTab, setActiveTab] = useState('assessment');

  // Question answering state
  const [question, setQuestion] = useState('');
  const [ragResult, setRagResult] = useState(null);
  const [asking, setAsking] = useState(false);

  // Assessment run state
  const [runningAssessment, setRunningAssessment] = useState(false);
  const [uploading, setUploading] = useState(false);

  const loadData = async () => {
    try {
      const v = await getVendor(id);
      setVendor(v);

      const docs = await getVendorDocuments(id);
      setDocuments(docs || []);

      try {
        const latestAss = await getLatestAIAssessment(id);
        setAssessment(latestAss);
      } catch (err) {
        // No assessment yet
        setAssessment(null);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await uploadDocument(id, file);
      await loadData();
    } catch (err) {
      alert('Upload failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
    }
  };

  const handleChunk = async (docId) => {
    try {
      await chunkDocument(id, docId);
      alert('Document tokenized into chunks and embedded in ChromaDB vector store!');
      await loadData();
    } catch (err) {
      alert('Chunking failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleRunAssessment = async () => {
    setRunningAssessment(true);
    try {
      const res = await runAIAssessment(id, "Comprehensive multi-agent risk assessment");
      setAssessment(res);
    } catch (err) {
      alert('AI assessment failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setRunningAssessment(false);
    }
  };

  const handleAskQuestion = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setAsking(true);
    try {
      const res = await askVendorDocumentation(id, question);
      setRagResult(res);
    } catch (err) {
      alert('Query failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setAsking(false);
    }
  };

  if (!vendor) {
    return <div className="p-8 text-center text-slate-500">Loading vendor details...</div>;
  }

  const radarScores = assessment
    ? {
        financial: assessment.financial_score,
        cybersecurity: assessment.cybersecurity_score,
        compliance: assessment.compliance_score,
        operational: assessment.operational_score,
        reputation: assessment.reputation_score,
      }
    : {
        financial: vendor.financial_score,
        cybersecurity: vendor.security_score,
        compliance: vendor.compliance_score,
        operational: vendor.operational_score,
        reputation: vendor.reputation_score,
      };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Link to="/vendors" className="p-2 bg-white border border-slate-200 rounded-lg hover:bg-slate-50">
            <ArrowLeft className="w-4 h-4 text-slate-600" />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-xl font-bold text-slate-900">{vendor.vendor_name}</h1>
              <RiskBadge level={assessment ? assessment.risk_level : vendor.risk_level} />
            </div>
            <div className="text-xs text-slate-500 flex items-center space-x-3 mt-1">
              <span>Vendor ID: #{vendor.vendor_id}</span>
              <span>•</span>
              <span>Revenue: ${Number(vendor.revenue || 0).toLocaleString()}</span>
              <span>•</span>
              <span>Debt: ${Number(vendor.debt || 0).toLocaleString()}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <label className="cursor-pointer inline-flex items-center px-3 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-lg shadow-sm">
            <Upload className="w-4 h-4 mr-1.5 text-sky-600" />
            {uploading ? 'Uploading...' : 'Upload Document'}
            <input type="file" onChange={handleUpload} className="hidden" accept=".pdf,.docx,.txt,.csv" />
          </label>

          <button
            onClick={handleRunAssessment}
            disabled={runningAssessment}
            className="inline-flex items-center px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold rounded-lg shadow-sm transition disabled:opacity-50"
          >
            <Bot className="w-4 h-4 mr-1.5" />
            {runningAssessment ? 'Running LangGraph Agents...' : 'Run Multi-Agent Assessment'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 space-x-6 text-sm font-semibold">
        <button
          onClick={() => setActiveTab('assessment')}
          className={`pb-3 flex items-center space-x-2 ${
            activeTab === 'assessment'
              ? 'text-sky-600 border-b-2 border-sky-600'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <Cpu className="w-4 h-4" />
          <span>AI Risk Assessment</span>
        </button>
        <button
          onClick={() => setActiveTab('documents')}
          className={`pb-3 flex items-center space-x-2 ${
            activeTab === 'documents'
              ? 'text-sky-600 border-b-2 border-sky-600'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Documents & Chunks ({documents.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('rag')}
          className={`pb-3 flex items-center space-x-2 ${
            activeTab === 'rag'
              ? 'text-sky-600 border-b-2 border-sky-600'
              : 'text-slate-500 hover:text-slate-800'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          <span>Ask Documents (RAG)</span>
        </button>
      </div>

      {/* Tab: Assessment */}
      {activeTab === 'assessment' && (
        <div className="space-y-6">
          {/* Top Score Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-xl border border-slate-200">
              <div className="text-xs text-slate-500 font-medium">Final Classification</div>
              <div className="text-2xl font-bold mt-1 text-slate-900">
                {assessment ? assessment.risk_level : vendor.risk_level}
              </div>
              <div className="text-xs text-slate-400 mt-0.5">
                Composite Score: {assessment ? assessment.final_score.toFixed(1) : '—'} / 100
              </div>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200">
              <div className="text-xs text-slate-500 font-medium">Phase 1 Quantitative Score</div>
              <div className="text-2xl font-bold mt-1 text-slate-700">
                {assessment ? assessment.phase1_score.toFixed(1) : '—'}
              </div>
              <div className="text-xs text-slate-400 mt-0.5">ML + Rule-based baseline (50%)</div>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200">
              <div className="text-xs text-slate-500 font-medium">Phase 2 Multi-Agent Score</div>
              <div className="text-2xl font-bold mt-1 text-sky-600">
                {assessment ? assessment.phase2_score.toFixed(1) : '—'}
              </div>
              <div className="text-xs text-slate-400 mt-0.5">5 Risk Dimension Agents (50%)</div>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200">
              <div className="text-xs text-slate-500 font-medium">Verification Status</div>
              <div className="text-2xl font-bold mt-1 text-emerald-600">
                {assessment ? assessment.verification_status : 'Pending'}
              </div>
              <div className="text-xs text-slate-400 mt-0.5">
                Confidence: {assessment ? `${(assessment.overall_confidence * 100).toFixed(0)}%` : '—'}
              </div>
            </div>
          </div>

          {/* Radar Chart & Details */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-sm font-semibold text-slate-800 mb-4">5-Dimension Risk Radar</h3>
              <RiskRadarChart scores={radarScores} />
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
              <h3 className="text-sm font-semibold text-slate-800">Agent Reasoning & Evidence Traceability</h3>
              {assessment?.answer ? (
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 text-xs leading-relaxed font-mono whitespace-pre-wrap text-slate-700">
                  {assessment.answer}
                </div>
              ) : (
                <div className="text-xs text-slate-400 p-8 text-center border border-dashed rounded-lg">
                  No multi-agent assessment executed yet. Click "Run Multi-Agent Assessment" to trigger LangGraph workflow.
                </div>
              )}
            </div>
          </div>

          {/* Individual Agent Findings */}
          {assessment?.findings && assessment.findings.length > 0 && (
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
              <h3 className="text-sm font-semibold text-slate-800">Specialized Agent Findings</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {assessment.findings.map((f, i) => (
                  <div key={i} className="border border-slate-200 rounded-lg p-3 space-y-2 bg-slate-50/50">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-xs text-slate-800">{f.agent_name}</span>
                      <RiskBadge level={f.risk_level} />
                    </div>
                    <div className="text-xs text-slate-600">Score: {f.score.toFixed(1)} / 100</div>
                    <p className="text-[11px] text-slate-500 leading-relaxed">{f.reasoning_summary}</p>
                    {f.evidence_references && f.evidence_references.length > 0 && (
                      <div className="pt-2 border-t border-slate-200">
                        <span className="text-[10px] text-slate-400 font-semibold uppercase">Evidence Cited:</span>
                        <div className="text-[10px] text-sky-700 truncate mt-0.5">
                          {f.evidence_references[0].filename} (p. {f.evidence_references[0].page_number})
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab: Documents */}
      {activeTab === 'documents' && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-semibold text-slate-800">Uploaded Vendor Documents</h3>
            <span className="text-xs text-slate-500">Supports PDF, DOCX, TXT, CSV (OCR enabled)</span>
          </div>

          {documents.length === 0 ? (
            <div className="bg-white p-12 text-center rounded-xl border border-dashed border-slate-200">
              <FileText className="w-8 h-8 mx-auto text-slate-300 mb-2" />
              <p className="text-sm font-medium text-slate-600">No documents uploaded yet</p>
              <p className="text-xs text-slate-400 mt-1">Upload audit reports, security whitepapers, or SLAs above.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {documents.map(doc => (
                <DocumentCard key={doc.document_id} doc={doc} onChunk={handleChunk} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab: RAG Question Answering */}
      {activeTab === 'rag' && (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
          <div>
            <h3 className="text-sm font-semibold text-slate-800">Evidence-Grounded RAG Assistant</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Queries only authentic document chunks in ChromaDB. Explanations cite exact files and page numbers.
            </p>
          </div>

          <form onSubmit={handleAskQuestion} className="space-y-3">
            <div className="flex space-x-2">
              <input
                type="text"
                value={question}
                onChange={e => setQuestion(e.target.value)}
                placeholder="e.g. Does the vendor hold ISO 27001 or SOC2 compliance?"
                className="flex-1 px-4 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-sky-500"
              />
              <button
                type="submit"
                disabled={asking}
                className="px-5 py-2 bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold rounded-lg disabled:opacity-50"
              >
                {asking ? 'Retrieving Evidence...' : 'Query'}
              </button>
            </div>
          </form>

          {ragResult && (
            <div className="space-y-4 pt-4 border-t border-slate-100">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-700">Answer</span>
                <span className="text-xs text-slate-400">
                  Status: {ragResult.status} (Confidence: {(ragResult.confidence * 100).toFixed(0)}%)
                </span>
              </div>

              <div className="bg-sky-50/50 border border-sky-100 p-4 rounded-lg text-xs leading-relaxed text-slate-800 whitespace-pre-wrap">
                {ragResult.answer}
              </div>

              {ragResult.evidence && ragResult.evidence.length > 0 && (
                <div className="space-y-2">
                  <div className="text-xs font-semibold text-slate-600">Retrieved Evidence Citations ({ragResult.evidence.length})</div>
                  <div className="space-y-2">
                    {ragResult.evidence.map((ev, idx) => (
                      <EvidenceCard key={idx} evidence={ev} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

