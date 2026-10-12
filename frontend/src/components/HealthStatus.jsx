import React from 'react';
import { Database, Server, RefreshCw, Cpu, Clock, CheckCircle, XCircle } from 'lucide-react';

export default function HealthStatus({ healthData, isLoading, onRefresh, error }) {
  return (
    <div className="card health-card">
      <div className="card-header">
        <div className="header-title">
          <Server className="icon-primary" size={20} />
          <h3>System & Database Health</h3>
        </div>
        <button 
          onClick={onRefresh} 
          disabled={isLoading}
          className="btn-refresh"
          title="Refresh health check"
        >
          <RefreshCw size={16} className={isLoading ? 'spinning' : ''} />
          <span>{isLoading ? 'Checking...' : 'Refresh'}</span>
        </button>
      </div>

      {error ? (
        <div className="error-banner">
          <XCircle size={18} />
          <div>
            <strong>Connection Failed:</strong> {error}
            <p className="error-hint">Ensure FastAPI backend is running at <code>http://127.0.0.1:8000</code></p>
          </div>
        </div>
      ) : (
        <div className="health-grid">
          <div className="metric-box">
            <div className="metric-label">
              <Server size={16} />
              <span>FastAPI Backend</span>
            </div>
            <div className="metric-value status-online">
              <span className="dot pulse"></span>
              {healthData?.status ? healthData.status.toUpperCase() : 'ONLINE'}
            </div>
            <span className="metric-sub">{healthData?.app_name || 'ScamShield AI'}</span>
          </div>

          <div className="metric-box">
            <div className="metric-label">
              <Database size={16} />
              <span>SQLite Database</span>
            </div>
            <div className="metric-value status-online">
              <CheckCircle size={18} className="text-emerald" />
              <span>{healthData?.database || 'Connected'}</span>
            </div>
            <span className="metric-sub">SQLite Local Storage</span>
          </div>

          <div className="metric-box">
            <div className="metric-label">
              <Cpu size={16} />
              <span>Environment</span>
            </div>
            <div className="metric-value">
              <span className="badge-env">{healthData?.environment || 'development'}</span>
            </div>
            <span className="metric-sub">API v{healthData?.version || '1.0.0'}</span>
          </div>

          <div className="metric-box">
            <div className="metric-label">
              <Clock size={16} />
              <span>Server Timestamp</span>
            </div>
            <div className="metric-value timestamp">
              {healthData?.timestamp ? new Date(healthData.timestamp).toLocaleTimeString() : '--:--:--'}
            </div>
            <span className="metric-sub">
              {healthData?.timestamp ? new Date(healthData.timestamp).toLocaleDateString() : 'Syncing...'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
