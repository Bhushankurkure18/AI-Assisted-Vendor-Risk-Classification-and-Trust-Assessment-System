"""
Script to generate an Industry-Level Architecture Document as an Executive PDF.
Uses Microsoft Edge headless rendering for pixel-perfect vector graphics and modern CSS.
"""
import os
import subprocess
import sys

def build_html_content() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AI-Assisted Vendor Risk Classification & Trust Assessment System - Industry Architecture</title>
<style>
  @page {
    size: A4 portrait;
    margin: 14mm 14mm 14mm 14mm;
    @bottom-right {
      content: "Page " counter(page);
      font-size: 8pt;
      color: #64748b;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    @bottom-left {
      content: "Confidential - Enterprise Vendor Risk Architecture Specification";
      font-size: 8pt;
      color: #94a3b8;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.45;
    font-size: 9pt;
  }

  .page-break {
    page-break-before: always;
  }

  /* Header / Cover banner */
  .header-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #0369a1 100%);
    color: #ffffff;
    padding: 22px 26px;
    border-radius: 8px;
    margin-bottom: 16px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
  }

  .header-banner .badge {
    display: inline-block;
    background: rgba(255, 255, 255, 0.18);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: #38bdf8;
    font-size: 7pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    padding: 3px 8px;
    border-radius: 9999px;
    margin-bottom: 8px;
  }

  .header-banner h1 {
    font-size: 18pt;
    font-weight: 800;
    line-height: 1.2;
    letter-spacing: -0.4px;
    margin-bottom: 5px;
    color: #f8fafc;
  }

  .header-banner .subtitle {
    font-size: 9.5pt;
    color: #cbd5e1;
    font-weight: 400;
    margin-bottom: 12px;
  }

  .meta-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.18);
    font-size: 8pt;
  }

  .meta-item .meta-label {
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 6.5pt;
    margin-bottom: 2px;
  }

  .meta-item .meta-value {
    color: #ffffff;
    font-weight: 600;
  }

  /* Section Styling */
  .section-title {
    font-size: 12pt;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 2px solid #2563eb;
    padding-bottom: 4px;
    margin-top: 14px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .section-title::before {
    content: "";
    display: inline-block;
    width: 5px;
    height: 15px;
    background: #2563eb;
    border-radius: 2px;
  }

  p {
    margin-bottom: 8px;
    color: #334155;
    text-align: justify;
    font-size: 8.8pt;
  }

  /* Grid Layouts */
  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 10px;
  }

  .grid-4 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin-bottom: 10px;
  }

  /* Cards */
  .card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px 10px;
  }

  .card-header {
    font-weight: 700;
    font-size: 8.5pt;
    color: #1e3a8a;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .card-body {
    font-size: 7.8pt;
    color: #475569;
    line-height: 1.35;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 6px;
    margin-bottom: 10px;
    font-size: 8pt;
  }

  th {
    background: #0f172a;
    color: #ffffff;
    text-align: left;
    padding: 5px 8px;
    font-weight: 600;
    border: 1px solid #0f172a;
    font-size: 7.8pt;
  }

  td {
    padding: 5px 8px;
    border: 1px solid #e2e8f0;
    color: #334155;
    font-size: 7.8pt;
  }

  tr:nth-child(even) td {
    background-color: #f8fafc;
  }

  .pill {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 6.8pt;
  }

  .pill-blue { background: #dbeafe; color: #1e40af; }
  .pill-green { background: #dcfce7; color: #166534; }
  .pill-amber { background: #fef3c7; color: #92400e; }
  .pill-red { background: #fee2e2; color: #991b1b; }
  .pill-purple { background: #f3e8ff; color: #6b21a8; }

  /* Diagram Container */
  .diagram-container {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px;
    margin: 8px 0 10px 0;
    text-align: center;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
  }

  .diagram-caption {
    font-size: 7.5pt;
    color: #64748b;
    margin-top: 5px;
    font-style: italic;
  }

  /* Alert / Callout */
  .callout {
    background: #eff6ff;
    border-left: 3px solid #2563eb;
    padding: 7px 10px;
    border-radius: 0 5px 5px 0;
    margin-bottom: 8px;
    font-size: 8.2pt;
    color: #1e40af;
  }
</style>
</head>
<body>

  <!-- ==================== PAGE 1: COVER & EXECUTIVE OVERVIEW ==================== -->
  <div class="header-banner">
    <div class="badge">Enterprise Technical Architecture Whitepaper</div>
    <h1>AI-Assisted Vendor Risk Classification &amp; Trust Assessment System</h1>
    <div class="subtitle">Multi-Tier Architecture, Dual-Engine Decisioning, and High-Throughput Cloud Infrastructure</div>
    <div class="meta-grid">
      <div class="meta-item">
        <div class="meta-label">System Architecture</div>
        <div class="meta-value">Microservices / ASGI / Clean Arch</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Dual Engine</div>
        <div class="meta-value">Rules (5D) + ML (RF &amp; XGB)</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Compliance Target</div>
        <div class="meta-value">SOC2 Type II, ISO 27001, GDPR</div>
      </div>
      <div class="meta-item">
        <div class="meta-label">Target Environment</div>
        <div class="meta-value">Kubernetes / Docker / PostgreSQL</div>
      </div>
    </div>
  </div>

  <div class="section-title">1. Executive Summary &amp; System Scope</div>
  <p>
    Modern enterprise procurement and supply-chain operations engage hundreds of third-party vendors for software-as-a-service (SaaS), cloud hosting, logistics, and data processing. Traditional Third-Party Risk Management (TPRM) relies on periodic, manual questionnaires and subjective auditor scoring—leading to inconsistent compliance evaluations, unmonitored vendor drift, and audit vulnerabilities.
  </p>
  <p>
    This platform delivers an <strong>industry-grade, automated, explainable vendor risk assessment system</strong>. It bridges strict regulatory requirements by deploying a <strong>Dual-Engine Framework</strong>: a deterministic 5-factor rule scoring engine that guarantees 100% auditable traceability, synchronized alongside supervised machine-learning classifiers (Random Forest and XGBoost) to detect subtle, non-linear correlations across multi-dimensional vendor telemetry.
  </p>

  <div class="grid-4">
    <div class="card">
      <div class="card-header"><span class="pill pill-blue">Ingress</span> Zero-Trust</div>
      <div class="card-body">WAF edge protection, TLS 1.3, Kong Gateway, JWT verification, and Pydantic v2 boundary sanitization.</div>
    </div>
    <div class="card">
      <div class="card-header"><span class="pill pill-green">Intelligence</span> Dual Core</div>
      <div class="card-body">Deterministic 5D weighted rule matrix + Random Forest and XGBoost machine-learning classifiers.</div>
    </div>
    <div class="card">
      <div class="card-header"><span class="pill pill-purple">Persistence</span> HA Relational</div>
      <div class="card-body">PostgreSQL 16 cluster with connection pooling (PgBouncer), Redis caching, and resilient SQLite fallback.</div>
    </div>
    <div class="card">
      <div class="card-header"><span class="pill pill-amber">Observability</span> Telemetry</div>
      <div class="card-body">Prometheus metrics, Grafana dashboards, OpenTelemetry distributed tracing, and immutable audit logs.</div>
    </div>
  </div>

  <div class="section-title">Key Architectural Service Level Objectives (SLOs)</div>
  <table>
    <thead>
      <tr>
        <th style="width: 25%;">System Metric / SLO</th>
        <th style="width: 20%;">Target Threshold</th>
        <th style="width: 55%;">Implementation &amp; Architectural Safeguard</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>End-to-End Latency (P99)</strong></td>
        <td><code>&lt; 85 ms</code></td>
        <td>FastAPI async ASGI core, in-memory Joblib ML inference, and Redis caching for repeated evaluations.</td>
      </tr>
      <tr>
        <td><strong>Assessment Throughput</strong></td>
        <td><code>500+ req/sec</code></td>
        <td>Stateless application container tier with Kubernetes Horizontal Pod Autoscaler (HPA) and PgBouncer connection pooling.</td>
      </tr>
      <tr>
        <td><strong>Model F1-Score &amp; Accuracy</strong></td>
        <td><code>&gt; 94.0%</code></td>
        <td>Ensemble bagging (Random Forest) and gradient boosting (XGBoost) trained on balanced multi-factor synthetic data.</td>
      </tr>
      <tr>
        <td><strong>Regulatory Auditability</strong></td>
        <td><code>100% Traceable</code></td>
        <td>Deterministic rule engine provides transparent mathematical breakdown for every risk decision with zero black-box bias.</td>
      </tr>
      <tr>
        <td><strong>System Availability SLA</strong></td>
        <td><code>99.99% Uptime</code></td>
        <td>Multi-AZ cloud deployment with automated failover and graceful local SQLite persistence fallback.</td>
      </tr>
    </tbody>
  </table>

  <!-- ==================== PAGE 2: HIGH-LEVEL ARCHITECTURE DIAGRAM & SPEC ==================== -->
  <div class="page-break"></div>

  <div class="section-title">2. High-Level Enterprise Architecture Diagram</div>
  <p>
    The system follows a strict multi-tier decoupled topology separating the ingress and presentation layer from the high-throughput ASGI application core, dual scoring engines, and relational storage.
  </p>

  <!-- SVG Architecture Diagram (High-Fidelity Vector Graphics) -->
  <div class="diagram-container">
    <svg viewBox="0 0 880 500" width="100%" height="360" xmlns="http://www.w3.org/2000/svg" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
      <defs>
        <linearGradient id="gradIngress" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#eff6ff"/><stop offset="100%" stop-color="#dbeafe"/>
        </linearGradient>
        <linearGradient id="gradApp" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#f0fdf4"/><stop offset="100%" stop-color="#dcfce7"/>
        </linearGradient>
        <linearGradient id="gradCore" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#f5f3ff"/><stop offset="100%" stop-color="#ede9fe"/>
        </linearGradient>
        <linearGradient id="gradData" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#fffbeb"/><stop offset="100%" stop-color="#fef3c7"/>
        </linearGradient>
        <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 8 5 L 0 9 z" fill="#3b82f6" />
        </marker>
      </defs>

      <!-- TIER 1: CLIENT & INGRESS -->
      <rect x="15" y="15" width="850" height="70" rx="8" fill="url(#gradIngress)" stroke="#93c5fd" stroke-width="1.5"/>
      <text x="30" y="32" font-size="10" font-weight="bold" fill="#1e40af">TIER 1: CLIENT &amp; INGRESS LAYER (Edge / DMZ)</text>

      <rect x="30" y="42" width="130" height="32" rx="4" fill="#ffffff" stroke="#60a5fa" stroke-width="1"/>
      <text x="95" y="58" font-size="8.5" font-weight="bold" fill="#0f172a" text-anchor="middle">React / Tailwind UI</text>
      <text x="95" y="68" font-size="7" fill="#64748b" text-anchor="middle">SPA Dashboard</text>

      <rect x="175" y="42" width="130" height="32" rx="4" fill="#ffffff" stroke="#60a5fa" stroke-width="1"/>
      <text x="240" y="58" font-size="8.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Swagger / OpenAPI</text>
      <text x="240" y="68" font-size="7" fill="#64748b" text-anchor="middle">Interactive /docs API</text>

      <rect x="320" y="42" width="130" height="32" rx="4" fill="#ffffff" stroke="#60a5fa" stroke-width="1"/>
      <text x="385" y="58" font-size="8.5" font-weight="bold" fill="#0f172a" text-anchor="middle">ERP / ServiceNow</text>
      <text x="385" y="68" font-size="7" fill="#64748b" text-anchor="middle">Procurement Ingestion</text>

      <rect x="490" y="42" width="160" height="32" rx="4" fill="#1e293b" stroke="#334155" stroke-width="1"/>
      <text x="570" y="58" font-size="8.5" font-weight="bold" fill="#38bdf8" text-anchor="middle">Cloudflare WAF / CDN</text>
      <text x="570" y="68" font-size="7" fill="#94a3b8" text-anchor="middle">DDoS / TLS 1.3 Termination</text>

      <rect x="665" y="42" width="185" height="32" rx="4" fill="#2563eb" stroke="#1d4ed8" stroke-width="1"/>
      <text x="757" y="58" font-size="8.5" font-weight="bold" fill="#ffffff" text-anchor="middle">Kong API Gateway</text>
      <text x="757" y="68" font-size="7" fill="#bfdbfe" text-anchor="middle">Rate Limiting • JWT Auth • CORS</text>

      <path d="M 450 58 L 485 58" stroke="#3b82f6" stroke-width="1.5" marker-end="url(#arrow)"/>
      <path d="M 650 58 L 660 58" stroke="#3b82f6" stroke-width="1.5" marker-end="url(#arrow)"/>

      <!-- CONNECTOR TIER 1 -> TIER 2 -->
      <path d="M 757 74 L 757 105 L 440 105 L 440 115" stroke="#3b82f6" stroke-width="1.5" fill="none" marker-end="url(#arrow)"/>

      <!-- TIER 2: APPLICATION & API LAYER -->
      <rect x="15" y="115" width="850" height="80" rx="8" fill="url(#gradApp)" stroke="#86efac" stroke-width="1.5"/>
      <text x="30" y="132" font-size="10" font-weight="bold" fill="#166534">TIER 2: REST API &amp; APPLICATION LAYER (FastAPI ASGI Core)</text>

      <rect x="30" y="142" width="170" height="42" rx="4" fill="#ffffff" stroke="#4ade80" stroke-width="1"/>
      <text x="115" y="159" font-size="8.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Vendor Controller</text>
      <text x="115" y="173" font-size="7" fill="#16a34a" text-anchor="middle">POST /api/v1/vendors (CRUD)</text>

      <rect x="215" y="142" width="185" height="42" rx="4" fill="#ffffff" stroke="#4ade80" stroke-width="1"/>
      <text x="307" y="159" font-size="8.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Assessment Controller</text>
      <text x="307" y="173" font-size="7" fill="#16a34a" text-anchor="middle">POST /api/v1/assessments/{id}</text>

      <rect x="415" y="142" width="195" height="42" rx="4" fill="#ffffff" stroke="#4ade80" stroke-width="1"/>
      <text x="512" y="159" font-size="8.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Pydantic v2 DTO Validator</text>
      <text x="512" y="173" font-size="7" fill="#475569" text-anchor="middle">Strict Type &amp; Boundary Sanitization</text>

      <rect x="625" y="142" width="225" height="42" rx="4" fill="#ffffff" stroke="#4ade80" stroke-width="1"/>
      <text x="737" y="159" font-size="8.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Preprocessing Service</text>
      <text x="737" y="173" font-size="7" fill="#475569" text-anchor="middle">Feature Scaling &amp; Normalization</text>

      <!-- CONNECTOR TIER 2 -> TIER 3 -->
      <path d="M 512 184 L 512 215" stroke="#3b82f6" stroke-width="1.5" marker-end="url(#arrow)"/>

      <!-- TIER 3: INTELLIGENCE & DUAL-ENGINE CORE -->
      <rect x="15" y="215" width="850" height="150" rx="8" fill="url(#gradCore)" stroke="#c4b5fd" stroke-width="1.5"/>
      <text x="30" y="232" font-size="10" font-weight="bold" fill="#5b21b6">TIER 3: DUAL-ENGINE DECISION &amp; PREDICTIVE INTELLIGENCE CORE</text>

      <!-- Sub-Engine 1: Rule Engine -->
      <rect x="30" y="242" width="370" height="110" rx="6" fill="#ffffff" stroke="#8b5cf6" stroke-width="1"/>
      <text x="45" y="258" font-size="9" font-weight="bold" fill="#6b21a8">1. Deterministic Rule-Based Engine</text>
      <text x="45" y="271" font-size="7.5" fill="#64748b">Transparent, Auditable, Weighted Scoring Matrix</text>

      <rect x="45" y="280" width="60" height="30" rx="3" fill="#ede9fe"/>
      <text x="75" y="293" font-size="7.5" font-weight="bold" fill="#5b21b6" text-anchor="middle">Financial</text>
      <text x="75" y="304" font-size="6.5" fill="#6b21a8" text-anchor="middle">Weight 25%</text>

      <rect x="112" y="280" width="60" height="30" rx="3" fill="#ede9fe"/>
      <text x="142" y="293" font-size="7.5" font-weight="bold" fill="#5b21b6" text-anchor="middle">Security</text>
      <text x="142" y="304" font-size="6.5" fill="#6b21a8" text-anchor="middle">Weight 25%</text>

      <rect x="179" y="280" width="65" height="30" rx="3" fill="#ede9fe"/>
      <text x="211" y="293" font-size="7.5" font-weight="bold" fill="#5b21b6" text-anchor="middle">Compliance</text>
      <text x="211" y="304" font-size="6.5" fill="#6b21a8" text-anchor="middle">Weight 20%</text>

      <rect x="251" y="280" width="65" height="30" rx="3" fill="#ede9fe"/>
      <text x="283" y="293" font-size="7.5" font-weight="bold" fill="#5b21b6" text-anchor="middle">Operations</text>
      <text x="283" y="304" font-size="6.5" fill="#6b21a8" text-anchor="middle">Weight 20%</text>

      <rect x="323" y="280" width="65" height="30" rx="3" fill="#ede9fe"/>
      <text x="355" y="293" font-size="7.5" font-weight="bold" fill="#5b21b6" text-anchor="middle">Reputation</text>
      <text x="355" y="304" font-size="6.5" fill="#6b21a8" text-anchor="middle">Weight 10%</text>

      <rect x="45" y="318" width="343" height="22" rx="3" fill="#0f172a"/>
      <text x="216" y="333" font-size="7.5" font-weight="bold" fill="#38bdf8" text-anchor="middle">Score (0-100) -> Banding: LOW [0-39] | MEDIUM [40-69] | HIGH [70-100]</text>

      <!-- Sub-Engine 2: ML Engine -->
      <rect x="415" y="242" width="250" height="110" rx="6" fill="#ffffff" stroke="#8b5cf6" stroke-width="1"/>
      <text x="430" y="258" font-size="9" font-weight="bold" fill="#6b21a8">2. Supervised ML Classifiers</text>
      <text x="430" y="271" font-size="7.5" fill="#64748b">Real-Time Serialized Model Runtime</text>

      <rect x="430" y="280" width="105" height="30" rx="3" fill="#dbeafe"/>
      <text x="482" y="293" font-size="7.5" font-weight="bold" fill="#1e40af" text-anchor="middle">Random Forest</text>
      <text x="482" y="304" font-size="6.5" fill="#2563eb" text-anchor="middle">100 Trees Ensemble</text>

      <rect x="545" y="280" width="105" height="30" rx="3" fill="#dbeafe"/>
      <text x="597" y="293" font-size="7.5" font-weight="bold" fill="#1e40af" text-anchor="middle">XGBoost Engine</text>
      <text x="597" y="304" font-size="6.5" fill="#2563eb" text-anchor="middle">Gradient Boosted Trees</text>

      <rect x="430" y="318" width="220" height="22" rx="3" fill="#f1f5f9"/>
      <text x="540" y="333" font-size="7.5" fill="#334155" text-anchor="middle">Inference Output: Risk Class + Probabilities</text>

      <!-- Decision Arbiter & Explainer -->
      <rect x="680" y="242" width="170" height="110" rx="6" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>
      <text x="765" y="262" font-size="8.5" font-weight="bold" fill="#f8fafc" text-anchor="middle">Risk Arbiter &amp; Report</text>
      <text x="765" y="276" font-size="7" fill="#94a3b8" text-anchor="middle">Cross-Verification Engine</text>

      <rect x="692" y="288" width="146" height="52" rx="4" fill="#1e293b"/>
      <text x="765" y="302" font-size="7" fill="#38bdf8" text-anchor="middle">• Discrepancy Detection</text>
      <text x="765" y="316" font-size="7" fill="#4ade80" text-anchor="middle">• Explainable Feature Rank</text>
      <text x="765" y="330" font-size="7" fill="#fbbf24" text-anchor="middle">• Immutable Audit Record</text>

      <!-- CONNECTOR TIER 3 -> TIER 4 -->
      <path d="M 440 365 L 440 385" stroke="#3b82f6" stroke-width="1.5" marker-end="url(#arrow)"/>

      <!-- TIER 4: PERSISTENCE & STORAGE -->
      <rect x="15" y="385" width="850" height="100" rx="8" fill="url(#gradData)" stroke="#fde68a" stroke-width="1.5"/>
      <text x="30" y="402" font-size="10" font-weight="bold" fill="#92400e">TIER 4: ENTERPRISE PERSISTENCE, CACHING &amp; STORAGE</text>

      <!-- PostgreSQL -->
      <rect x="30" y="412" width="260" height="60" rx="4" fill="#ffffff" stroke="#f59e0b" stroke-width="1"/>
      <text x="160" y="428" font-size="8.5" font-weight="bold" fill="#0f172a" text-anchor="middle">PostgreSQL 16 Primary Cluster</text>
      <text x="160" y="442" font-size="7.5" fill="#475569" text-anchor="middle">`vendors` &amp; `assessments` Relational Tables</text>
      <text x="160" y="456" font-size="7" fill="#16a34a" text-anchor="middle">Managed Connection Pool (PgBouncer / SQLAlchemy)</text>

      <!-- Redis Cache -->
      <rect x="305" y="412" width="170" height="60" rx="4" fill="#ffffff" stroke="#f59e0b" stroke-width="1"/>
      <text x="390" y="428" font-size="8.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Redis In-Memory Cache</text>
      <text x="390" y="442" font-size="7.5" fill="#475569" text-anchor="middle">Sub-ms Assessment Caching</text>
      <text x="390" y="456" font-size="7" fill="#0284c7" text-anchor="middle">Session State &amp; Rate Limits</text>

      <!-- Object Store / Model Registry -->
      <rect x="490" y="412" width="180" height="60" rx="4" fill="#ffffff" stroke="#f59e0b" stroke-width="1"/>
      <text x="580" y="428" font-size="8.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Model &amp; Document Registry</text>
      <text x="580" y="442" font-size="7.5" fill="#475569" text-anchor="middle">AWS S3 / models/*.pkl</text>
      <text x="580" y="456" font-size="7" fill="#6b21a8" text-anchor="middle">Versioned Model Artifacts</text>

      <!-- Resilient SQLite -->
      <rect x="685" y="412" width="165" height="60" rx="4" fill="#ffffff" stroke="#f59e0b" stroke-width="1"/>
      <text x="767" y="428" font-size="8.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Resilient Local Fallback</text>
      <text x="767" y="442" font-size="7.5" fill="#475569" text-anchor="middle">SQLite Engine (vendor_risk.db)</text>
      <text x="767" y="456" font-size="7" fill="#d97706" text-anchor="middle">Zero-Downtime Offline Mode</text>
    </svg>
    <div class="diagram-caption">Figure 1.1: Complete Multi-Tier Cloud-Native Architecture for Vendor Risk Assessment System</div>
  </div>

  <!-- ==================== PAGE 3: EXECUTION PIPELINE & SEQUENCE ==================== -->
  <div class="page-break"></div>

  <div class="section-title">3. End-to-End Real-Time Assessment Pipeline</div>
  <p>
    When an enterprise procurement analyst or automated webhook requests a risk assessment, the request transitions through a deterministic, high-throughput pipeline designed for sub-100ms response times and strict audit logging.
  </p>

  <!-- Flowchart SVG Diagram -->
  <div class="diagram-container">
    <svg viewBox="0 0 880 230" width="100%" height="200" xmlns="http://www.w3.org/2000/svg" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
      <defs>
        <marker id="arr" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 8 5 L 0 9 z" fill="#2563eb" />
        </marker>
      </defs>

      <!-- Step 1 -->
      <rect x="20" y="20" width="115" height="70" rx="6" fill="#eff6ff" stroke="#3b82f6" stroke-width="1.5"/>
      <text x="77" y="40" font-size="8.5" font-weight="bold" fill="#1e40af" text-anchor="middle">1. Request Ingress</text>
      <text x="77" y="55" font-size="7" fill="#334155" text-anchor="middle">POST /assessments</text>
      <text x="77" y="67" font-size="7" fill="#64748b" text-anchor="middle">Auth &amp; Schema Check</text>

      <path d="M 135 55 L 155 55" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arr)"/>

      <!-- Step 2 -->
      <rect x="160" y="20" width="115" height="70" rx="6" fill="#f8fafc" stroke="#64748b" stroke-width="1.5"/>
      <text x="217" y="40" font-size="8.5" font-weight="bold" fill="#0f172a" text-anchor="middle">2. Profile Query</text>
      <text x="217" y="55" font-size="7" fill="#334155" text-anchor="middle">Fetch Vendor Profile</text>
      <text x="217" y="67" font-size="7" fill="#64748b" text-anchor="middle">PostgreSQL / Cache</text>

      <path d="M 275 55 L 295 55" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arr)"/>

      <!-- Step 3 -->
      <rect x="300" y="20" width="120" height="70" rx="6" fill="#f0fdf4" stroke="#22c55e" stroke-width="1.5"/>
      <text x="360" y="40" font-size="8.5" font-weight="bold" fill="#166534" text-anchor="middle">3. Preprocessing</text>
      <text x="360" y="55" font-size="7" fill="#334155" text-anchor="middle">Feature Vectorization</text>
      <text x="360" y="67" font-size="7" fill="#64748b" text-anchor="middle">Debt-to-Rev, Scaling</text>

      <path d="M 420 55 L 440 55" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arr)"/>

      <!-- Parallel Execution Box -->
      <rect x="445" y="10" width="180" height="95" rx="6" fill="#f5f3ff" stroke="#8b5cf6" stroke-width="1.5" stroke-dasharray="4"/>
      <text x="535" y="26" font-size="8" font-weight="bold" fill="#6b21a8" text-anchor="middle">4. DUAL SCORER (PARALLEL)</text>

      <rect x="455" y="35" width="160" height="28" rx="4" fill="#ffffff" stroke="#a78bfa" stroke-width="1"/>
      <text x="535" y="49" font-size="7.5" font-weight="bold" fill="#5b21b6" text-anchor="middle">4A. Deterministic Rule Scorer</text>
      <text x="535" y="58" font-size="6.5" fill="#64748b" text-anchor="middle">5 Dimensions Weighted (0-100)</text>

      <rect x="455" y="68" width="160" height="28" rx="4" fill="#ffffff" stroke="#a78bfa" stroke-width="1"/>
      <text x="535" y="82" font-size="7.5" font-weight="bold" fill="#5b21b6" text-anchor="middle">4B. ML Classifier (RF/XGB)</text>
      <text x="535" y="91" font-size="6.5" fill="#64748b" text-anchor="middle">Predicted Risk Level &amp; Conf.</text>

      <path d="M 625 55 L 645 55" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arr)"/>

      <!-- Step 5 -->
      <rect x="650" y="20" width="105" height="70" rx="6" fill="#fffbeb" stroke="#f59e0b" stroke-width="1.5"/>
      <text x="702" y="40" font-size="8.5" font-weight="bold" fill="#92400e" text-anchor="middle">5. Risk Arbiter</text>
      <text x="702" y="55" font-size="7" fill="#334155" text-anchor="middle">Cross-Validation</text>
      <text x="702" y="67" font-size="7" fill="#64748b" text-anchor="middle">Explainability SHAP</text>

      <path d="M 755 55 L 775 55" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arr)"/>

      <!-- Step 6 -->
      <rect x="780" y="20" width="85" height="70" rx="6" fill="#0f172a" stroke="#1e293b" stroke-width="1.5"/>
      <text x="822" y="40" font-size="8.5" font-weight="bold" fill="#38bdf8" text-anchor="middle">6. Persistence</text>
      <text x="822" y="55" font-size="7" fill="#ffffff" text-anchor="middle">Commit to DB</text>
      <text x="822" y="67" font-size="7" fill="#94a3b8" text-anchor="middle">Audit Record</text>

      <!-- Return Flow -->
      <path d="M 822 90 L 822 135 L 77 135 L 77 90" stroke="#059669" stroke-width="1.5" stroke-dasharray="3" fill="none" marker-end="url(#arr)"/>
      <text x="440" y="128" font-size="7.5" font-weight="bold" fill="#059669" text-anchor="middle">HTTP 201 Created: Full Risk Dossier JSON (Score, Category, Explainability, Recommendations)</text>
    </svg>
    <div class="diagram-caption">Figure 1.2: End-to-End Real-Time Assessment Workflow with Parallel Dual-Engine Execution</div>
  </div>

  <div class="section-title">4. Deep Dive: The 5-Dimension Risk Formulation</div>
  <p>
    Compliance frameworks (NIST SP 800-161, ISO 27001, and SOC2) forbid black-box decision models without reproducible scoring baselines. The deterministic engine evaluates each vendor against a strict mathematical formula:
  </p>

  <div class="callout">
    <strong>Weighted Score Formula:</strong> 
    <code>Risk_Score = 0.25·(100 - S_fin) + 0.25·(100 - S_sec) + 0.20·(100 - S_comp) + 0.20·(100 - S_ops) + 0.10·(100 - S_rep)</code>
  </div>

  <table>
    <thead>
      <tr>
        <th style="width: 15%;">Dimension</th>
        <th style="width: 10%;">Weight</th>
        <th style="width: 35%;">Evaluation Metrics &amp; Audit Inputs</th>
        <th style="width: 40%;">Risk Impact &amp; Mitigation Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Financial</strong></td>
        <td><span class="pill pill-blue">25%</span></td>
        <td>Debt-to-Revenue ratio, solvency, working capital, credit default risk.</td>
        <td>High debt flags insolvency hazard. Triggers escrow requirement or delayed milestone payments.</td>
      </tr>
      <tr>
        <td><strong>Security</strong></td>
        <td><span class="pill pill-red">25%</span></td>
        <td>SOC2 Type II attestation, ISO 27001, static/dynamic pentesting, AES-256 encryption.</td>
        <td>Unpatched vulnerabilities or missing certs trigger mandatory security remediations.</td>
      </tr>
      <tr>
        <td><strong>Compliance</strong></td>
        <td><span class="pill pill-purple">20%</span></td>
        <td>GDPR, HIPAA, CCPA compliance, regulatory fines, third-party audit history.</td>
        <td>Non-compliance mandates data processing agreements (DPA) and legal review.</td>
      </tr>
      <tr>
        <td><strong>Operational</strong></td>
        <td><span class="pill pill-amber">20%</span></td>
        <td>Historical SLA uptime, Disaster Recovery (DR) RPO/RTO, failover tests.</td>
        <td>SLA breach history requires financial penalty clauses and redundant multi-vendor routing.</td>
      </tr>
      <tr>
        <td><strong>Reputation</strong></td>
        <td><span class="pill pill-green">10%</span></td>
        <td>Adverse media scanning, ongoing litigation, executive integrity audits.</td>
        <td>Severe litigation results in procurement disqualification or executive steering review.</td>
      </tr>
    </tbody>
  </table>

  <!-- ==================== PAGE 4: ML ARCHITECTURE & CLUSTER TOPOLOGY ==================== -->
  <div class="page-break"></div>

  <div class="section-title">5. Machine Learning Architecture &amp; Empirical Comparison</div>
  <p>
    The ML tier benchmarks multiple supervised algorithms to discover hidden multi-factor risk combinations that deterministic linear models miss. The models are trained on a balanced synthetic distribution representing enterprise vendors.
  </p>

  <div class="grid-2">
    <div class="card">
      <div class="card-header">
        <span class="pill pill-blue">Algorithm 1</span> Random Forest Classifier
      </div>
      <div class="card-body">
        <strong>Characteristics:</strong> Bagging ensemble of 100 de-correlated decision trees.<br/>
        <strong>Strengths:</strong> Zero risk of overfitting on tabular data, highly resilient to feature collinearity, fast parallel CPU training.<br/>
        <strong>Application:</strong> Serves as the primary enterprise baseline for stable, monotonic risk classification.
      </div>
    </div>
    <div class="card">
      <div class="card-header">
        <span class="pill pill-green">Algorithm 2</span> XGBoost Classifier
      </div>
      <div class="card-body">
        <strong>Characteristics:</strong> Gradient boosted decision trees optimized via second-order Taylor expansion.<br/>
        <strong>Strengths:</strong> Superior decision boundary precision, built-in L1/L2 regularization, exceptional handling of skewed distributions.<br/>
        <strong>Application:</strong> Deployed for high-accuracy outlier identification and borderline vendor categorization.
      </div>
    </div>
  </div>

  <div class="section-title">6. Production Kubernetes &amp; Cloud Deployment Topology</div>
  <p>
    The diagram below illustrates the production deployment blueprint across cloud availability zones (AWS / Azure / GCP) with automated horizontal autoscaling and database read-replicas.
  </p>

  <div class="diagram-container">
    <svg viewBox="0 0 880 320" width="100%" height="250" xmlns="http://www.w3.org/2000/svg" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
      <!-- Cluster Boundary -->
      <rect x="15" y="15" width="850" height="290" rx="8" fill="#f8fafc" stroke="#0f172a" stroke-width="1.5" stroke-dasharray="6"/>
      <text x="35" y="35" font-size="10" font-weight="bold" fill="#0f172a">ENTERPRISE KUBERNETES CLUSTER (EKS / GKE) - HIGH AVAILABILITY ZONE</text>

      <!-- Ingress Node -->
      <rect x="35" y="55" width="180" height="70" rx="6" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>
      <text x="125" y="75" font-size="8.5" font-weight="bold" fill="#1e40af" text-anchor="middle">Ingress Controller</text>
      <text x="125" y="88" font-size="7.5" fill="#334155" text-anchor="middle">Nginx Ingress / Traefik</text>
      <text x="125" y="100" font-size="7" fill="#64748b" text-anchor="middle">SSL Offloading • Path Routing</text>

      <!-- Horizontal Autoscaling FastAPI Pods -->
      <rect x="255" y="50" width="370" height="115" rx="6" fill="#f0fdf4" stroke="#16a34a" stroke-width="1.5"/>
      <text x="440" y="68" font-size="8.5" font-weight="bold" fill="#166534" text-anchor="middle">FastAPI Application Deployment (HPA: 3 to 10 Pods)</text>

      <rect x="270" y="80" width="105" height="70" rx="4" fill="#ffffff" stroke="#4ade80" stroke-width="1"/>
      <text x="322" y="98" font-size="7.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Pod 1 (Uvicorn)</text>
      <text x="322" y="110" font-size="6.5" fill="#16a34a" text-anchor="middle">REST API + Engine</text>
      <text x="322" y="122" font-size="6.5" fill="#64748b" text-anchor="middle">Joblib In-Memory</text>

      <rect x="388" y="80" width="105" height="70" rx="4" fill="#ffffff" stroke="#4ade80" stroke-width="1"/>
      <text x="440" y="98" font-size="7.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Pod 2 (Uvicorn)</text>
      <text x="440" y="110" font-size="6.5" fill="#16a34a" text-anchor="middle">REST API + Engine</text>
      <text x="440" y="122" font-size="6.5" fill="#64748b" text-anchor="middle">Joblib In-Memory</text>

      <rect x="505" y="80" width="105" height="70" rx="4" fill="#ffffff" stroke="#4ade80" stroke-width="1"/>
      <text x="557" y="98" font-size="7.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Pod N (Autoscaled)</text>
      <text x="557" y="110" font-size="6.5" fill="#16a34a" text-anchor="middle">REST API + Engine</text>
      <text x="557" y="122" font-size="6.5" fill="#64748b" text-anchor="middle">Joblib In-Memory</text>

      <!-- Redis Cluster -->
      <rect x="665" y="55" width="180" height="70" rx="6" fill="#fffbeb" stroke="#d97706" stroke-width="1.5"/>
      <text x="755" y="75" font-size="8.5" font-weight="bold" fill="#b45309" text-anchor="middle">Redis Cluster / Sentinel</text>
      <text x="755" y="88" font-size="7.5" fill="#334155" text-anchor="middle">In-Memory Cache (3 Nodes)</text>
      <text x="755" y="100" font-size="7" fill="#64748b" text-anchor="middle">Rate Limiting &amp; Fast Lookups</text>

      <!-- Database Subsystem -->
      <rect x="35" y="190" width="590" height="100" rx="6" fill="#ede9fe" stroke="#7c3aed" stroke-width="1.5"/>
      <text x="55" y="208" font-size="8.5" font-weight="bold" fill="#5b21b6">PostgreSQL High Availability &amp; Connection Pooling</text>

      <rect x="55" y="218" width="160" height="60" rx="4" fill="#ffffff" stroke="#a78bfa" stroke-width="1"/>
      <text x="135" y="235" font-size="8" font-weight="bold" fill="#0f172a" text-anchor="middle">PgBouncer Pooler</text>
      <text x="135" y="248" font-size="7" fill="#5b21b6" text-anchor="middle">Active Connection Pooling</text>
      <text x="135" y="260" font-size="6.5" fill="#64748b" text-anchor="middle">Transaction Multiplexing</text>

      <rect x="235" y="218" width="180" height="60" rx="4" fill="#ffffff" stroke="#a78bfa" stroke-width="1"/>
      <text x="325" y="235" font-size="8" font-weight="bold" fill="#0f172a" text-anchor="middle">PostgreSQL Primary (Write)</text>
      <text x="325" y="248" font-size="7" fill="#16a34a" text-anchor="middle">ACID Transactions &amp; Audit Logs</text>
      <text x="325" y="260" font-size="6.5" fill="#64748b" text-anchor="middle">Streaming Replication</text>

      <rect x="435" y="218" width="175" height="60" rx="4" fill="#ffffff" stroke="#a78bfa" stroke-width="1"/>
      <text x="522" y="235" font-size="8" font-weight="bold" fill="#0f172a" text-anchor="middle">PostgreSQL Replica (Read)</text>
      <text x="522" y="248" font-size="7" fill="#0284c7" text-anchor="middle">Read-Heavy Analytics &amp; Reports</text>
      <text x="522" y="260" font-size="6.5" fill="#64748b" text-anchor="middle">Read Queries Offload</text>

      <!-- Prometheus & Monitoring -->
      <rect x="665" y="190" width="180" height="100" rx="6" fill="#f1f5f9" stroke="#475569" stroke-width="1.5"/>
      <text x="755" y="210" font-size="8.5" font-weight="bold" fill="#0f172a" text-anchor="middle">Observability &amp; SRE</text>
      <text x="755" y="228" font-size="7.5" fill="#475569" text-anchor="middle">• Prometheus Time-Series</text>
      <text x="755" y="242" font-size="7.5" fill="#475569" text-anchor="middle">• Grafana Dashboards</text>
      <text x="755" y="256" font-size="7.5" fill="#475569" text-anchor="middle">• OpenTelemetry Traces</text>
      <text x="755" y="270" font-size="7.5" fill="#475569" text-anchor="middle">• ELK Centralized Logs</text>
    </svg>
    <div class="diagram-caption">Figure 1.3: Cloud-Native Production Topology (Kubernetes Pods, PgBouncer, Read-Replicas, Observability)</div>
  </div>

  <div class="section-title">7. Governance, Security &amp; Compliance Standards</div>
  <table>
    <thead>
      <tr>
        <th style="width: 20%;">Control Objective</th>
        <th style="width: 25%;">Regulatory Standard</th>
        <th style="width: 55%;">System Implementation</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Data Encryption</strong></td>
        <td>NIST SP 800-53 / SOC2 Type II</td>
        <td>TLS 1.3 for all HTTP REST traffic; AES-256 for PostgreSQL volume encryption at rest.</td>
      </tr>
      <tr>
        <td><strong>Access &amp; Authorization</strong></td>
        <td>OAuth2.0 / Enterprise RBAC</td>
        <td>Role-Based Access Control (Analyst, Compliance Officer, System Admin) with short-lived JWT tokens.</td>
      </tr>
      <tr>
        <td><strong>Audit Traceability</strong></td>
        <td>ISO 27001 / GDPR Article 30</td>
        <td>Every assessment creates an immutable record linking vendor profile, scores, and exact model version.</td>
      </tr>
      <tr>
        <td><strong>Model Explainability</strong></td>
        <td>EU AI Act / IEEE Ethically Aligned</td>
        <td>Deterministic breakdown ensures compliance auditors can verify why a vendor was classified as HIGH risk.</td>
      </tr>
    </tbody>
  </table>

</body>
</html>
"""

def main():
    print("Generating HTML content for architecture document...")
    html_content = build_html_content()
    
    html_path = os.path.abspath("architecture_specification.html")
    pdf_path = os.path.abspath("Vendor_Risk_System_Architecture_Industry_Level.pdf")
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Saved HTML to: {html_path}")
    
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    edge_cmd = None
    for p in edge_paths:
        if os.path.exists(p):
            edge_cmd = p
            break
            
    if not edge_cmd:
        print("Error: Microsoft Edge executable not found.")
        sys.exit(1)
        
    print(f"Found Edge: {edge_cmd}")
    print("Compiling PDF via Headless Edge...")
    
    cmd = [
        edge_cmd,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f"SUCCESS: Generated PDF successfully!")
        print(f"Path: {pdf_path}")
        print(f"Size: {size_kb:.2f} KB")
    else:
        print(f"Failed to generate PDF. Subprocess output:\n{result.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    main()
