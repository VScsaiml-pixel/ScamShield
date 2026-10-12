import React, { useState } from 'react';
import { 
  Globe, 
  AlertTriangle, 
  CheckCircle2, 
  AlertCircle, 
  Copy, 
  Check, 
  RotateCcw,
  ExternalLink
} from 'lucide-react';
import { analyzeURL } from '../services/api';

const URL_PRESETS = [
  {
    label: "Fake SBI KYC Portal",
    url: "http://sbi-kyc-verify.xyz/login.php"
  },
  {
    label: "Raw IP Banking Link",
    url: "http://192.168.1.105:8080/secure/bank/login"
  },
  {
    label: "Suspicious APK Download",
    url: "http://indiapost-parcel-tracking.top/download/update.apk"
  },
  {
    label: "Shortened Reward URL",
    url: "https://bit.ly/claim-free-cashback-reward"
  },
  {
    label: "Official State Bank of India",
    url: "https://www.onlinesbi.sbi"
  },
  {
    label: "Official Google Search",
    url: "https://www.google.com"
  }
];

export default function URLScanner() {
  const [inputUrl, setInputUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [copiedReport, setCopiedReport] = useState(false);

  const handleScan = async () => {
    const trimmed = inputUrl.trim();

    if (!trimmed) {
      setErrorMessage("Please enter or paste a URL before scanning.");
      return;
    }

    if (trimmed.length < 3 || (!trimmed.includes('.') && !trimmed.includes('localhost'))) {
      setErrorMessage("Please enter a valid URL or domain (e.g. example.com or https://example.com).");
      return;
    }

    setErrorMessage(null);
    setIsAnalyzing(true);

    try {
      const response = await analyzeURL(trimmed);
      if (response.success) {
        setAnalysisResult(response.data);
      } else {
        setErrorMessage(response.error || "URL analysis failed. Please verify the URL string.");
      }
    } catch (err) {
      setErrorMessage(err.message || "Network error. Unable to connect to backend.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setInputUrl('');
    setAnalysisResult(null);
    setErrorMessage(null);
  };

  const copyReportToClipboard = () => {
    if (!analysisResult) return;
    const reportText = `SCAMSHIELD AI LINK ANALYSIS REPORT
URL: ${analysisResult.url}
Risk: ${analysisResult.risk_level.toUpperCase()} (${Math.round(analysisResult.risk_score)}/100)

Suspicious Indicators:
${analysisResult.suspicious_indicators?.map(i => `• ${i.indicator}: ${i.description}`).join('\n') || '• No suspicious indicators detected.'}

Recommendation:
${analysisResult.recommendation || 'Proceed with standard caution.'}
`;

    navigator.clipboard.writeText(reportText);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2000);
  };

  const getRiskReportTheme = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical':
      case 'high':
        return {
          bannerClass: 'report-theme-danger',
          badgeText: `${level.toUpperCase()} RISK`,
          badgeClass: 'badge-danger'
        };
      case 'medium':
        return {
          bannerClass: 'report-theme-warning',
          badgeText: 'MEDIUM RISK',
          badgeClass: 'badge-warning'
        };
      case 'low':
      default:
        return {
          bannerClass: 'report-theme-safe',
          badgeText: 'LOW RISK',
          badgeClass: 'badge-safe'
        };
    }
  };

  return (
    <div className="scanner-page">
      {/* 1. HEADER */}
      <div className="page-header">
        <h1 className="page-title">Check a suspicious link</h1>
        <p className="page-subtitle">
          Paste a URL to analyze its structure and potential risk indicators.
        </p>
      </div>

      {/* 2. DEMO PRESETS */}
      <div className="presets-wrapper">
        <span className="presets-label">Try a sample link:</span>
        <div className="presets-list">
          {URL_PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              className="preset-btn"
              onClick={() => {
                setInputUrl(p.url);
                setAnalysisResult(null);
                setErrorMessage(null);
              }}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* 3. INPUT FORM */}
      <div className="scanner-form-container">
        <div className="input-group">
          <input
            type="text"
            className="scanner-input"
            placeholder="https://example.com/..."
            value={inputUrl}
            onChange={(e) => {
              setInputUrl(e.target.value);
              if (errorMessage) setErrorMessage(null);
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleScan();
            }}
          />
          {inputUrl && (
            <button 
              type="button" 
              className="btn-text input-clear-btn"
              onClick={handleClear}
            >
              Clear
            </button>
          )}
        </div>

        {errorMessage && (
          <div className="alert-banner alert-warning">
            <AlertCircle size={16} />
            <span>{errorMessage}</span>
          </div>
        )}

        <div className="scanner-actions">
          <button
            type="button"
            className="btn btn-primary btn-lg"
            onClick={handleScan}
            disabled={isAnalyzing || !inputUrl.trim()}
          >
            {isAnalyzing ? "Analyzing URL..." : "Analyze URL"}
          </button>
        </div>
      </div>

      {/* 4. SECURITY REPORT RESULT */}
      {analysisResult && (
        <div className="security-report-card">
          {(() => {
            const theme = getRiskReportTheme(analysisResult.risk_level);
            const isThreat = analysisResult.risk_level === 'High' || analysisResult.risk_level === 'Critical';

            return (
              <>
                {/* REPORT HEADER */}
                <div className={`report-header ${theme.bannerClass}`}>
                  <div className="report-header-left">
                    <span className={`status-badge ${theme.badgeClass}`}>
                      {theme.badgeText}
                    </span>
                    <span className="report-analyzed-url truncate" title={analysisResult.url}>
                      {analysisResult.url}
                    </span>
                  </div>
                  <div className="report-header-right">
                    <div className="report-score-box">
                      <span className="report-score-num">
                        {Math.round(analysisResult.risk_score)}
                      </span>
                      <span className="report-score-denom">/100</span>
                    </div>
                  </div>
                </div>

                {/* REPORT BODY */}
                <div className="report-body">
                  {/* SUSPICIOUS INDICATORS */}
                  <div className="report-section">
                    <h3 className="report-section-title">
                      {isThreat ? "Suspicious Indicators:" : "URL Analysis Findings:"}
                    </h3>
                    
                    {analysisResult.suspicious_indicators && analysisResult.suspicious_indicators.length > 0 ? (
                      <ul className="report-bullet-list">
                        {analysisResult.suspicious_indicators.map((ind, idx) => (
                          <li key={idx} className="report-bullet-item">
                            <strong>{ind.indicator}</strong>: {ind.description}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="report-clean-text">
                        No deceptive domain structure, raw IP address, suspicious TLD, or credential harvesting keywords were found in this URL string.
                      </p>
                    )}
                  </div>

                  {/* RECOMMENDATION */}
                  <div className="report-section">
                    <h3 className="report-section-title">Recommendation:</h3>
                    <p className="report-recommendation-text">
                      {analysisResult.recommendation}
                    </p>
                  </div>

                  {/* EXPLANATION */}
                  {analysisResult.explanation && (
                    <div className="report-summary-box">
                      <span className="summary-title">Summary:</span>
                      <p className="summary-text">{analysisResult.explanation}</p>
                    </div>
                  )}

                  {/* ACTIONS */}
                  <div className="report-footer-actions">
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={copyReportToClipboard}
                    >
                      {copiedReport ? <Check size={14} className="text-safe" /> : <Copy size={14} />}
                      <span>{copiedReport ? "Report Copied" : "Copy Report"}</span>
                    </button>
                    <button
                      type="button"
                      className="btn btn-subtle btn-sm"
                      onClick={handleClear}
                    >
                      <RotateCcw size={14} />
                      <span>Check Another Link</span>
                    </button>
                  </div>
                </div>
              </>
            );
          })()}
        </div>
      )}
    </div>
  );
}
