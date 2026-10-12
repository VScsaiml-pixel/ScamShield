import React from 'react';
import { Layers, Database, Cpu, Compass, CheckCircle2, Circle } from 'lucide-react';

export default function ArchitectureCard() {
  const steps = [
    { title: 'Phase 1: Project Setup & Health Verification', status: 'completed', desc: 'React + Vite, FastAPI, SQLite models, Health check API' },
    { title: 'Phase 2: NLP/ML Dataset & Baseline Model', status: 'next', desc: 'SMS/Email scam dataset, TF-IDF vectorization, Logistic Regression classifier' },
    { title: 'Phase 3: Prediction API & Rule-Based Engine', status: 'upcoming', desc: 'Urgency heuristics, credential checks, risk score (0-100), category mapping' },
    { title: 'Phase 4: Full Interactive Frontend Scanner', status: 'upcoming', desc: 'Results screen, explainable warning indicators, safety recommendations' },
    { title: 'Phase 5: Scan History, Auth & Dashboard Stats', status: 'upcoming', desc: 'SQLite storage, previous scan logs, user feedback mechanism' },
    { title: 'Phase 6: Passive URL Feature Analyzer', status: 'upcoming', desc: 'HTTPS, subdomain inspection, suspicious TLD detection' },
  ];

  return (
    <div className="card architecture-card">
      <div className="card-header">
        <div className="header-title">
          <Compass className="icon-primary" size={20} />
          <h3>System Architecture & Implementation Roadmap</h3>
        </div>
      </div>

      <div className="architecture-grid">
        <div className="arch-layer">
          <div className="layer-badge">Presentation</div>
          <h4>Frontend</h4>
          <p>React 19 + Vite</p>
          <span className="layer-note">Dashboard UI, real-time health indicator, explainability cards</span>
        </div>

        <div className="arch-arrow">➔</div>

        <div className="arch-layer">
          <div className="layer-badge">Service</div>
          <h4>REST Backend</h4>
          <p>Python 3.13 + FastAPI</p>
          <span className="layer-note">Input validation, CORS middleware, REST endpoints</span>
        </div>

        <div className="arch-arrow">➔</div>

        <div className="arch-layer">
          <div className="layer-badge">Intelligence</div>
          <h4>ML & Rules Engine</h4>
          <p>Scikit-Learn + TF-IDF</p>
          <span className="layer-note">Feature extraction, probability scoring, rule-based indicators</span>
        </div>

        <div className="arch-arrow">➔</div>

        <div className="arch-layer">
          <div className="layer-badge">Persistence</div>
          <h4>Database</h4>
          <p>SQLite + SQLAlchemy</p>
          <span className="layer-note">Users, Scans, Indicators, Feedback tables</span>
        </div>
      </div>

      <div className="roadmap-container">
        <h4 className="roadmap-title">Project Milestones:</h4>
        <div className="roadmap-list">
          {steps.map((s, idx) => (
            <div key={idx} className={`roadmap-item ${s.status}`}>
              <div className="item-icon">
                {s.status === 'completed' ? (
                  <CheckCircle2 size={16} className="text-emerald" />
                ) : s.status === 'next' ? (
                  <Circle size={16} className="text-cyan pulse" />
                ) : (
                  <Circle size={16} className="text-muted" />
                )}
              </div>
              <div className="item-content">
                <span className="item-title">{s.title}</span>
                <span className="item-desc">{s.desc}</span>
              </div>
              <span className={`status-tag ${s.status}`}>
                {s.status === 'completed' ? 'Active' : s.status === 'next' ? 'Next Up' : 'Planned'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
