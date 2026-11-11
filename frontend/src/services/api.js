import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
});

export const getVendors = () => api.get('/api/v1/vendors').then(res => res.data);
export const getVendor = (id) => api.get(`/api/v1/vendors/${id}`).then(res => res.data);
export const createVendor = (data) => api.post('/api/v1/vendors', data).then(res => res.data);

// Document Ingestion & Chunking
export const getVendorDocuments = (vendorId) =>
  api.get(`/api/v1/documents/vendor/${vendorId}`).then(res => res.data);

export const uploadDocument = (vendorId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post(`/api/v1/documents/upload/${vendorId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(res => res.data);
};

export const chunkDocument = (vendorId, documentId) =>
  api.post(`/api/v1/documents/${vendorId}/${documentId}/chunk`).then(res => res.data);

// RAG Retrieval
export const askVendorDocumentation = (vendorId, question, topK = 5) =>
  api.post(`/api/v1/rag/vendors/${vendorId}/ask`, { question, top_k: topK }).then(res => res.data);

// Phase 2 Multi-Agent AI Assessment
export const runAIAssessment = (vendorId, question, alpha = 0.5, beta = 0.5) =>
  api.post(`/api/v1/assessments/ai/vendors/${vendorId}/run`, {
    question: question || "Provide comprehensive risk assessment",
    alpha,
    beta,
  }).then(res => res.data);

export const getLatestAIAssessment = (vendorId) =>
  api.get(`/api/v1/assessments/ai/vendors/${vendorId}/latest`).then(res => res.data);

export const getAIAssessmentHistory = (vendorId) =>
  api.get(`/api/v1/assessments/ai/vendors/${vendorId}/history`).then(res => res.data);

export default api;

