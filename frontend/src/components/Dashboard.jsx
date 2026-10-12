import React, { useState, useEffect } from 'react';
import { 
  MessageSquare, 
  Globe, 
  ArrowRight, 
  AlertCircle,
  RotateCw,
  ExternalLink
} from 'lucide-react';
import { getDashboardStats } from '../services/api';

export default function Dashboard({ onNavigate }) {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);

  const fetchStats = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const response = await getDashboardStats();
      if (response.success) {
        setStats(response.data);
      } else {
        setErrorMessage(response.error);
      }
    } catch (err) {
      setErrorMessage(err.message || 'Failed to connect to analytics service');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const formatDate = (isoString) => {
    if (!isoString) return 'Just now';
    try {
      const scanDate = new Date(isoString);
      const now = new Date();
      const diffMs = now - scanDate;
      const diffMins = Math.floor(diffMs / (1000 * 60));
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

      if (diffMins < 2) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays === 1) return 'Yesterday';
      if (diffDays < 7) return `${diffDays}d ago`;

      return scanDate.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return isoString;
    }
  };

  const getRiskBadgeClass = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'badge-danger';
      case 'medium':
        return 'badge-warning';
      case 'low':
      default:
        return 'badge-safe';
    }
  };

  const getResultLabel = (prediction, riskLevel) => {
    if (prediction?.toLowerCase() === 'scam' || riskLevel?.toLowerCase() === 'critical' || riskLevel?.toLowerCase() === 'high') {
      return 'Suspicious';
    }
    if (riskLevel?.toLowerCase() === 'medium') {
      return 'Caution';
    }
    return 'Safe';
  };

  const getResultBadgeClass = (resultLabel) => {
    if (resultLabel === 'Suspicious') return 'badge-danger';
    if (resultLabel === 'Caution') return 'badge-warning';
    return 'badge-safe';
  };

  return (
    <div className="dashboard-container">
      {/* 1. TOP HEADER & PRIMARY ACTIONS */}
      <section className="dashboard-hero">
        <div className="hero-content">
          <h1 className="hero-title">ScamShield AI</h1>
          <p className="hero-subtitle">
            Check suspicious messages and links before you interact with them.
          </p>
        </div>
        <div className="hero-actions">
          <button 
            type="button" 
            className="btn btn-primary"
            onClick={() => onNavigate('message')}
          >
            <MessageSquare size={16} />
            <span>Scan a Message</span>
          </button>
          <button 
            type="button" 
            className="btn btn-secondary"
            onClick={() => onNavigate('url')}
          >
            <Globe size={16} />
            <span>Check a URL</span>
          </button>
        </div>
      </section>

      {/* ERROR NOTICE (IF ANY) */}
      {errorMessage && (
        <div className="alert-banner alert-warning">
          <AlertCircle size={18} />
          <div className="alert-content">
            <strong>Unable to load live statistics:</strong> {errorMessage}
            <button type="button" className="btn-link" onClick={fetchStats}>
              Retry
            </button>
          </div>
        </div>
      )}

      {/* 2. SIMPLE STATISTIC CARDS */}
      {stats && (
        <section className="stats-row">
          <div className="stat-card">
            <span className="stat-label">Total Scans</span>
            <div className="stat-value">{stats.total_scans}</div>
            <span className="stat-detail">
              {stats.message_scans} messages, {stats.url_scans} URLs
            </span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Threats Detected</span>
            <div className="stat-value text-danger">{stats.total_threats}</div>
            <span className="stat-detail">
              {stats.total_scans > 0 
                ? `${Math.round((stats.total_threats / stats.total_scans) * 100)}% of scans flagged` 
                : 'No threats recorded'}
            </span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Safe Scans</span>
            <div className="stat-value text-safe">{stats.low_risk_scans}</div>
            <span className="stat-detail">
              {stats.total_scans > 0 
                ? `${Math.round((stats.low_risk_scans / stats.total_scans) * 100)}% verified clean` 
                : 'No safe scans yet'}
            </span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Average Risk Score</span>
            <div className="stat-value">{stats.average_risk_score}<span className="stat-denom">/100</span></div>
            <span className="stat-detail">
              Across all recorded scans
            </span>
          </div>
        </section>
      )}

      {/* 3. RISK DISTRIBUTION (SIMPLE, SUBTLE COLORS) */}
      {stats && stats.risk_distribution && stats.total_scans > 0 && (
        <section className="section-block">
          <div className="section-header">
            <h2 className="section-title">Risk Distribution</h2>
            <span className="section-meta">{stats.total_scans} total scans</span>
          </div>

          <div className="risk-distribution-container">
            {/* Multi-segment clean bar */}
            <div className="risk-progress-bar">
              {stats.risk_distribution.map((item, idx) => {
                if (item.percentage === 0) return null;
                const segmentColor = 
                  item.level === 'Low' ? '#16a34a' :
                  item.level === 'Medium' ? '#d97706' :
                  item.level === 'High' ? '#ea580c' : '#dc2626';

                return (
                  <div 
                    key={idx}
                    className="risk-segment"
                    style={{ width: `${item.percentage}%`, backgroundColor: segmentColor }}
                    title={`${item.level} Risk: ${item.count} (${item.percentage}%)`}
                  />
                );
              })}
            </div>

            {/* Clean 4-column legend */}
            <div className="risk-legend-grid">
              {stats.risk_distribution.map((item, idx) => (
                <div key={idx} className="risk-legend-item">
                  <div className="legend-label-row">
                    <span 
                      className="legend-dot"
                      style={{
                        backgroundColor: 
                          item.level === 'Low' ? '#16a34a' :
                          item.level === 'Medium' ? '#d97706' :
                          item.level === 'High' ? '#ea580c' : '#dc2626'
                      }}
                    />
                    <span className="legend-name">{item.level} Risk</span>
                  </div>
                  <div className="legend-count-row">
                    <span className="legend-count">{item.count}</span>
                    <span className="legend-percentage">({item.percentage}%)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* 4. RECENT SCANS TABLE (MAIN FOCUS AREA) */}
      <section className="section-block">
        <div className="section-header">
          <div>
            <h2 className="section-title">Recent Scans</h2>
            <p className="section-subtitle">The latest messages and URLs evaluated by the system.</p>
          </div>
          {stats && stats.recent_scans && stats.recent_scans.length > 0 && (
            <button 
              type="button" 
              className="btn btn-subtle"
              onClick={() => onNavigate('history')}
            >
              <span>View all history</span>
              <ArrowRight size={14} />
            </button>
          )}
        </div>

        {(!stats || !stats.recent_scans || stats.recent_scans.length === 0) ? (
          <div className="empty-state-box">
            <p className="empty-title">No scans recorded yet</p>
            <p className="empty-desc">
              Scan a suspicious SMS, email, WhatsApp message, or link to get started.
            </p>
            <div className="empty-actions">
              <button 
                type="button" 
                className="btn btn-primary"
                onClick={() => onNavigate('message')}
              >
                Scan a Message
              </button>
            </div>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="clean-table">
              <thead>
                <tr>
                  <th style={{ width: '100px' }}>Type</th>
                  <th>Result</th>
                  <th style={{ width: '110px' }}>Risk</th>
                  <th>Category</th>
                  <th style={{ width: '130px', textAlign: 'right' }}>Date</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_scans.map((s) => {
                  const resultLabel = getResultLabel(s.prediction, s.risk_level);
                  const resultBadgeClass = getResultBadgeClass(resultLabel);

                  return (
                    <tr 
                      key={s.id} 
                      className="table-row-clickable"
                      onClick={() => onNavigate('history')}
                    >
                      <td>
                        <span className="type-tag">
                          {s.scan_type === 'url' ? 'URL' : 'Message'}
                        </span>
                      </td>
                      <td>
                        <span className={`status-badge ${resultBadgeClass}`}>
                          {resultLabel}
                        </span>
                      </td>
                      <td>
                        <span className="risk-score-text">
                          <strong>{Math.round(s.risk_score)}</strong>/100
                        </span>
                      </td>
                      <td>
                        <div className="category-cell">
                          <span className="category-title">{s.category || '—'}</span>
                          {s.input_preview && (
                            <span className="input-snippet truncate" title={s.input_preview}>
                              {s.input_preview}
                            </span>
                          )}
                        </div>
                      </td>
                      <td style={{ textAlign: 'right' }} className="date-cell">
                        {formatDate(s.timestamp)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
