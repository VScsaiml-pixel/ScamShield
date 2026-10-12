import React, { useState, useEffect } from 'react';
import { 
  Trash2, 
  RotateCw, 
  Search, 
  X, 
  AlertCircle,
  Copy, 
  Check,
  ExternalLink
} from 'lucide-react';
import { getScanHistory, getScanById, deleteScanById, clearAllScans } from '../services/api';

export default function ScanHistory() {
  const [scans, setScans] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState(null);
  
  // Filter states
  const [typeFilter, setTypeFilter] = useState('all'); // 'all' | 'message' | 'url'
  const [searchQuery, setSearchQuery] = useState('');
  
  // Modal detail state
  const [selectedScan, setSelectedScan] = useState(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [copiedReport, setCopiedReport] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  const fetchHistory = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const params = {};
      if (typeFilter !== 'all') {
        params.scan_type = typeFilter;
      }
      const response = await getScanHistory(params);
      if (response.success) {
        setScans(response.data.scans || []);
        setTotalCount(response.data.total || 0);
      } else {
        setErrorMessage(response.error);
      }
    } catch (err) {
      setErrorMessage(err.message || 'Failed to fetch scan history.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [typeFilter]);

  const handleOpenDetail = async (scanId) => {
    setIsLoadingDetail(true);
    try {
      const response = await getScanById(scanId);
      if (response.success) {
        setSelectedScan(response.data);
      } else {
        alert(response.error || 'Failed to load scan details');
      }
    } catch (err) {
      alert(err.message || 'Error fetching scan details');
    } finally {
      setIsLoadingDetail(false);
    }
  };

  const handleDeleteOne = async (e, scanId) => {
    e.stopPropagation();
    if (!window.confirm(`Are you sure you want to delete scan record #${scanId}?`)) {
      return;
    }
    setIsDeleting(true);
    try {
      const res = await deleteScanById(scanId);
      if (res.success) {
        if (selectedScan && selectedScan.id === scanId) {
          setSelectedScan(null);
        }
        await fetchHistory();
      } else {
        alert(res.error || 'Failed to delete scan record');
      }
    } catch (err) {
      alert(err.message || 'Failed to delete');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleClearAll = async () => {
    setIsDeleting(true);
    try {
      const res = await clearAllScans();
      if (res.success) {
        setShowClearConfirm(false);
        setSelectedScan(null);
        await fetchHistory();
      } else {
        alert(res.error || 'Failed to clear history');
      }
    } catch (err) {
      alert(err.message || 'Failed to clear history');
    } finally {
      setIsDeleting(false);
    }
  };

  const formatDate = (isoString) => {
    if (!isoString) return 'Just now';
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
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

  const filteredScans = scans.filter(s => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      (s.category && s.category.toLowerCase().includes(q)) ||
      (s.input_preview && s.input_preview.toLowerCase().includes(q)) ||
      (s.risk_level && s.risk_level.toLowerCase().includes(q))
    );
  });

  return (
    <div className="history-page">
      {/* 1. HEADER */}
      <div className="history-header">
        <div>
          <h1 className="page-title">Scan History</h1>
          <p className="page-subtitle">
            All previously analyzed messages and URLs stored securely in your local database.
          </p>
        </div>

        {totalCount > 0 && (
          <div className="history-top-actions">
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={fetchHistory}
              disabled={isLoading}
              title="Refresh scan history"
            >
              <RotateCw size={14} className={isLoading ? 'spinning' : ''} />
              <span>Refresh</span>
            </button>
            <button
              type="button"
              className="btn btn-danger-outline btn-sm"
              onClick={() => setShowClearConfirm(true)}
              disabled={isDeleting}
            >
              <Trash2 size={14} />
              <span>Clear History</span>
            </button>
          </div>
        )}
      </div>

      {/* 2. FILTER & SEARCH BAR */}
      <div className="history-controls-bar">
        <div className="filter-pill-group">
          <button 
            type="button" 
            className={`filter-tab ${typeFilter === 'all' ? 'active' : ''}`}
            onClick={() => setTypeFilter('all')}
          >
            All Scans ({totalCount})
          </button>
          <button 
            type="button" 
            className={`filter-tab ${typeFilter === 'message' ? 'active' : ''}`}
            onClick={() => setTypeFilter('message')}
          >
            Messages
          </button>
          <button 
            type="button" 
            className={`filter-tab ${typeFilter === 'url' ? 'active' : ''}`}
            onClick={() => setTypeFilter('url')}
          >
            URLs
          </button>
        </div>

        <div className="search-bar">
          <Search size={15} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search by category, preview text..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* ERROR NOTICE */}
      {errorMessage && (
        <div className="alert-banner alert-warning">
          <AlertCircle size={16} />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* 3. SCANS TABLE */}
      {isLoading ? (
        <div className="loading-state-box">
          <p>Loading scan history...</p>
        </div>
      ) : filteredScans.length === 0 ? (
        <div className="empty-state-box">
          <p className="empty-title">No scan records found</p>
          <p className="empty-desc">
            {searchQuery 
              ? "No scan records match your search query." 
              : "Scan records will appear here automatically when messages or URLs are analyzed."}
          </p>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="clean-table">
            <thead>
              <tr>
                <th style={{ width: '130px' }}>Date</th>
                <th style={{ width: '90px' }}>Type</th>
                <th style={{ width: '100px' }}>Risk Score</th>
                <th style={{ width: '110px' }}>Risk Level</th>
                <th>Category</th>
                <th style={{ width: '80px', textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredScans.map((s) => {
                const badgeClass = getRiskBadgeClass(s.risk_level);

                return (
                  <tr 
                    key={s.id} 
                    className="table-row-clickable"
                    onClick={() => handleOpenDetail(s.id)}
                  >
                    <td className="date-cell">{formatDate(s.timestamp)}</td>
                    <td>
                      <span className="type-tag">
                        {s.scan_type === 'url' ? 'URL' : 'Message'}
                      </span>
                    </td>
                    <td>
                      <span className="risk-score-text">
                        <strong>{Math.round(s.risk_score)}</strong>/100
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge ${badgeClass}`}>
                        {s.risk_level}
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
                    <td style={{ textAlign: 'right' }}>
                      <button 
                        type="button" 
                        className="btn btn-subtle btn-sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenDetail(s.id);
                        }}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* 4. CLEAR HISTORY CONFIRMATION MODAL */}
      {showClearConfirm && (
        <div className="modal-overlay" onClick={() => setShowClearConfirm(false)}>
          <div className="modal-container modal-sm" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Clear Scan History?</h3>
              <button 
                type="button" 
                className="btn-icon" 
                onClick={() => setShowClearConfirm(false)}
              >
                <X size={18} />
              </button>
            </div>
            <div className="modal-body">
              <p>
                Are you sure you want to permanently delete all {totalCount} scan records from the local SQLite database? This cannot be undone.
              </p>
            </div>
            <div className="modal-footer">
              <button 
                type="button" 
                className="btn btn-secondary" 
                onClick={() => setShowClearConfirm(false)}
              >
                Cancel
              </button>
              <button 
                type="button" 
                className="btn btn-danger" 
                onClick={handleClearAll}
                disabled={isDeleting}
              >
                {isDeleting ? "Deleting..." : "Yes, Clear History"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 5. SCAN DETAIL MODAL */}
      {selectedScan && (
        <div className="modal-overlay" onClick={() => setSelectedScan(null)}>
          <div className="modal-container modal-md" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <span className="modal-meta">
                  Scan Record #{selectedScan.id} • {selectedScan.scan_type?.toUpperCase()}
                </span>
                <h3 className="modal-title">
                  {selectedScan.category || "General Classification"}
                </h3>
              </div>
              <button 
                type="button" 
                className="btn-icon" 
                onClick={() => setSelectedScan(null)}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body">
              {/* METRIC ROW */}
              <div className="modal-score-banner">
                <div>
                  <span className="score-banner-label">Evaluated Risk:</span>
                  <div className="score-banner-val">
                    <strong>{Math.round(selectedScan.risk_score)}</strong>/100
                    <span className={`status-badge ${getRiskBadgeClass(selectedScan.risk_level)} ml-2`}>
                      {selectedScan.risk_level}
                    </span>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span className="score-banner-label">Analyzed On:</span>
                  <div className="score-banner-date">{formatDate(selectedScan.timestamp)}</div>
                </div>
              </div>

              {/* INPUT PREVIEW */}
              <div className="modal-section">
                <h4 className="modal-section-title">Analyzed Content:</h4>
                <div className="input-preview-box">
                  {selectedScan.input_preview}
                </div>
              </div>

              {/* WARNING SIGNS / INDICATORS */}
              <div className="modal-section">
                <h4 className="modal-section-title">Detected Indicators:</h4>
                {selectedScan.indicators && selectedScan.indicators.length > 0 ? (
                  <ul className="report-bullet-list">
                    {selectedScan.indicators.map((ind, idx) => (
                      <li key={idx} className="report-bullet-item">
                        <strong>{ind.indicator}</strong>: {ind.description || ind.evidence}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="report-clean-text">No high-risk indicators were flagged.</p>
                )}
              </div>

              {/* RECOMMENDATIONS */}
              <div className="modal-section">
                <h4 className="modal-section-title">Recommendations:</h4>
                {selectedScan.recommendations && selectedScan.recommendations.length > 0 ? (
                  <ul className="report-bullet-list">
                    {selectedScan.recommendations.map((rec, idx) => (
                      <li key={idx} className="report-bullet-item">
                        {rec}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="report-clean-text">Exercise standard caution with unsolicited requests.</p>
                )}
              </div>
            </div>

            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-danger-outline btn-sm"
                onClick={(e) => handleDeleteOne(e, selectedScan.id)}
              >
                Delete Record
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => setSelectedScan(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
