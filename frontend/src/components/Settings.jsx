import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Download, 
  Trash2, 
  CheckCircle2, 
  AlertCircle,
  X
} from 'lucide-react';
import { getScanHistory, clearAllScans, checkBackendHealth } from '../services/api';

export default function Settings({ onNavigate }) {
  const [totalScans, setTotalScans] = useState(0);
  const [isClearing, setIsClearing] = useState(false);
  const [backendHealth, setBackendHealth] = useState(null);
  const [exporting, setExporting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const loadData = async () => {
    try {
      const historyRes = await getScanHistory();
      if (historyRes.success) {
        setTotalScans(historyRes.data.total || 0);
      }
      const healthRes = await checkBackendHealth();
      if (healthRes.success) {
        setBackendHealth(healthRes.data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleExportJSON = async () => {
    setExporting(true);
    try {
      const res = await getScanHistory({ limit: 500 });
      if (res.success && res.data.scans) {
        const jsonStr = JSON.stringify(res.data.scans, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `scamshield_history_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else {
        alert("Failed to export history data.");
      }
    } catch (err) {
      alert("Error exporting JSON: " + err.message);
    } finally {
      setExporting(false);
    }
  };

  const handleClearHistory = async () => {
    setIsClearing(true);
    try {
      const res = await clearAllScans();
      if (res.success) {
        setShowConfirm(false);
        setTotalScans(0);
      } else {
        alert(res.error || "Failed to clear history.");
      }
    } catch (err) {
      alert("Error clearing history: " + err.message);
    } finally {
      setIsClearing(false);
    }
  };

  return (
    <div className="settings-page">
      <div className="page-header">
        <h1 className="page-title">Settings & System Info</h1>
        <p className="page-subtitle">
          Manage local scan data, export audit reports, and inspect backend service status.
        </p>
      </div>

      <div className="settings-stack">
        {/* 1. SYSTEM STATUS */}
        <div className="settings-card">
          <div className="settings-card-header">
            <h2 className="settings-card-title">Backend Status</h2>
            <p className="settings-card-desc">Current state of the local FastAPI server and SQLite storage.</p>
          </div>

          <div className="settings-info-list">
            <div className="settings-info-row">
              <span className="info-key">API Server</span>
              <span className="info-val">
                {backendHealth?.status === 'healthy' ? (
                  <span className="badge-safe">
                    Online (Port 8000)
                  </span>
                ) : (
                  <span className="badge-danger">
                    Offline
                  </span>
                )}
              </span>
            </div>

            <div className="settings-info-row">
              <span className="info-key">Database</span>
              <span className="info-val">
                SQLite (`backend/data/scamshield.db`)
              </span>
            </div>

            <div className="settings-info-row">
              <span className="info-key">Total Stored Scans</span>
              <span className="info-val font-semibold">{totalScans} records</span>
            </div>

            <div className="settings-info-row">
              <span className="info-key">Model Engine</span>
              <span className="info-val">TF-IDF Vectorizer + Calibrated Logistic Regression + Heuristic Rules</span>
            </div>
          </div>
        </div>

        {/* 2. DATA MANAGEMENT */}
        <div className="settings-card">
          <div className="settings-card-header">
            <h2 className="settings-card-title">Data Management</h2>
            <p className="settings-card-desc">Export or delete your local scan history.</p>
          </div>

          <div className="settings-actions-list">
            <div className="settings-action-item">
              <div>
                <strong>Export Scan History</strong>
                <p>Download all recorded scans in standard JSON format for offline review or grading.</p>
              </div>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={handleExportJSON}
                disabled={exporting || totalScans === 0}
              >
                <Download size={14} />
                <span>{exporting ? "Exporting..." : "Export JSON"}</span>
              </button>
            </div>

            <div className="settings-action-item danger-item">
              <div>
                <strong className="text-danger">Delete All Scan History</strong>
                <p>Permanently remove all scan entries from the local SQLite database.</p>
              </div>
              <button
                type="button"
                className="btn btn-danger-outline btn-sm"
                onClick={() => setShowConfirm(true)}
                disabled={isClearing || totalScans === 0}
              >
                <Trash2 size={14} />
                <span>Clear History</span>
              </button>
            </div>
          </div>
        </div>

        {/* 3. ABOUT PROJECT */}
        <div className="settings-card">
          <div className="settings-card-header">
            <h2 className="settings-card-title">About ScamShield AI</h2>
            <p className="settings-card-desc">College Mini Project demonstration (2026).</p>
          </div>
          <p className="about-text">
            ScamShield AI is an explainable scam and phishing detection tool built to help users evaluate suspicious SMS messages, WhatsApp forwards, emails, and web links. It combines rule-based heuristic threat indicators with calibrated machine learning classification.
          </p>
        </div>
      </div>

      {/* CONFIRM MODAL */}
      {showConfirm && (
        <div className="modal-overlay" onClick={() => setShowConfirm(false)}>
          <div className="modal-container modal-sm" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Clear All History?</h3>
              <button 
                type="button" 
                className="btn-icon" 
                onClick={() => setShowConfirm(false)}
              >
                <X size={18} />
              </button>
            </div>
            <div className="modal-body">
              <p>
                Are you sure you want to permanently delete all {totalScans} scan records? This action cannot be reversed.
              </p>
            </div>
            <div className="modal-footer">
              <button 
                type="button" 
                className="btn btn-secondary btn-sm" 
                onClick={() => setShowConfirm(false)}
              >
                Cancel
              </button>
              <button 
                type="button" 
                className="btn btn-danger btn-sm" 
                onClick={handleClearHistory}
                disabled={isClearing}
              >
                {isClearing ? "Clearing..." : "Yes, Delete All"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
