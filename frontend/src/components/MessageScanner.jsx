import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  CheckCircle2, 
  AlertCircle, 
  Copy, 
  Check, 
  RotateCcw,
  ShieldAlert,
  ShieldCheck,
  Info
} from 'lucide-react';
import { analyzeMessage } from '../services/api';

const MAX_CHARS = 10000;

const SAMPLE_PRESETS = [
  {
    label: "Banking KYC Phish",
    text: "Dear SBI customer, your YONO NetBanking account has been blocked today due to pending KYC update. Click http://sbi-kyc-verify.xyz to update your PAN and unblock within 24 hours."
  },
  {
    label: "UPI Cashback Trap",
    text: "Congratulations! You have received a cashback refund of Rs 2,500 on PhonePe. Scan this QR code and enter your secret UPI PIN to receive money in your account."
  },
  {
    label: "Digital Arrest Scam",
    text: "CBI Cyber Crime Cell: An illegal courier containing narcotics has been seized in Mumbai registered in your name. You are placed under Digital Arrest. Join Skype call immediately."
  },
  {
    label: "YouTube Task Scam",
    text: "Urgent Part-time Work From Home! Earn Rs 3,000 to 5,000 daily by liking YouTube videos and rating hotels. No experience required. Daily payout. Join Telegram: t.me/fast_earn_india"
  },
  {
    label: "Courier Redelivery Fee",
    text: "India Post: Your package #IND9821 cannot be delivered due to incomplete street address. Update address and pay Rs 25 redelivery charge at http://indiapost-update.xyz/pay within 12 hours."
  },
  {
    label: "Legitimate Bank SMS",
    text: "Rs 1,500.00 debited from A/C XX4921 on 07-Oct-26 at Swiggy UPI. Available balance: Rs 24,310.50. - HDFC Bank"
  }
];

export default function MessageScanner({ initialMessage = '' }) {
  const [inputText, setInputText] = useState(initialMessage || '');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [copiedReport, setCopiedReport] = useState(false);

  useEffect(() => {
    if (initialMessage) {
      setInputText(initialMessage);
      setAnalysisResult(null);
      setErrorMessage(null);
    }
  }, [initialMessage]);

  const charCount = inputText.length;
  const isTooLong = charCount > MAX_CHARS;

  const handleScan = async () => {
    const trimmed = inputText.trim();

    if (!trimmed) {
      setErrorMessage("Please paste or type a message before scanning.");
      return;
    }

    if (trimmed.length < 5) {
      setErrorMessage("Message is too short to analyze accurately. Please provide the full message text.");
      return;
    }

    const payloadText = trimmed.length > MAX_CHARS ? trimmed.substring(0, MAX_CHARS) : trimmed;

    setErrorMessage(null);
    setIsAnalyzing(true);

    try {
      const response = await analyzeMessage(payloadText);
      if (response.success) {
        setAnalysisResult(response.data);
      } else {
        setErrorMessage(response.error || "Analysis failed. Please check the backend connection.");
      }
    } catch (err) {
      setErrorMessage(err.message || "Network error. Unable to reach the server.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setInputText('');
    setAnalysisResult(null);
    setErrorMessage(null);
  };

  const copyReportToClipboard = () => {
    if (!analysisResult) return;
    const reportText = `SCAMSHIELD AI SECURITY REPORT
Risk: ${analysisResult.risk_level.toUpperCase()} (${Math.round(analysisResult.risk_score)}/100)
Category: ${analysisResult.category}

Why this looks suspicious:
${analysisResult.indicators?.map(i => `• ${i.indicator}: ${i.description || i.evidence}`).join('\n') || '• No high-risk indicators detected.'}

What you should do:
${analysisResult.recommendations?.map(r => `• ${r}`).join('\n') || '• Proceed with standard caution.'}
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
        <h1 className="page-title">Check a suspicious message</h1>
        <p className="page-subtitle">
          Paste a message below and ScamShield AI will analyze potential warning signs.
        </p>
      </div>

      {/* 2. DEMO SAMPLE PRESETS */}
      <div className="presets-wrapper">
        <span className="presets-label">Try a sample message:</span>
        <div className="presets-list">
          {SAMPLE_PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              className="preset-btn"
              onClick={() => {
                setInputText(p.text);
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
        <div className="textarea-container">
          <textarea
            className="scanner-textarea"
            rows={6}
            placeholder="Paste a suspicious SMS, WhatsApp message, email, job offer, or payment request here..."
            value={inputText}
            onChange={(e) => {
              setInputText(e.target.value);
              if (errorMessage) setErrorMessage(null);
            }}
          />
          <div className="textarea-footer">
            <span className={`char-count ${isTooLong ? 'text-danger' : ''}`}>
              {charCount} / {MAX_CHARS} characters
            </span>
            {inputText && (
              <button 
                type="button" 
                className="btn-text"
                onClick={handleClear}
              >
                Clear input
              </button>
            )}
          </div>
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
            disabled={isAnalyzing || !inputText.trim()}
          >
            {isAnalyzing ? "Analyzing..." : "Analyze Message"}
          </button>
        </div>
      </div>

      {/* 4. SECURITY REPORT RESULT */}
      {analysisResult && (
        <div className="security-report-card">
          {(() => {
            const theme = getRiskReportTheme(analysisResult.risk_level);
            const isThreat = analysisResult.risk_level === 'High' || analysisResult.risk_level === 'Critical' || analysisResult.prediction === 'Scam';

            return (
              <>
                {/* REPORT HEADER */}
                <div className={`report-header ${theme.bannerClass}`}>
                  <div className="report-header-left">
                    <span className={`status-badge ${theme.badgeClass}`}>
                      {theme.badgeText}
                    </span>
                    <h2 className="report-category">
                      {analysisResult.category || "General Classification"}
                    </h2>
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
                  {/* WHY THIS LOOKS SUSPICIOUS */}
                  <div className="report-section">
                    <h3 className="report-section-title">
                      {isThreat ? "Why this looks suspicious:" : "Analysis findings:"}
                    </h3>
                    
                    {analysisResult.indicators && analysisResult.indicators.length > 0 ? (
                      <ul className="report-bullet-list">
                        {analysisResult.indicators.map((ind, idx) => (
                          <li key={idx} className="report-bullet-item">
                            <strong>{ind.indicator}</strong>: {ind.description || ind.evidence}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="report-clean-text">
                        No critical threat indicators, urgent coercion, or credential harvesting patterns were detected in this message.
                      </p>
                    )}
                  </div>

                  {/* WHAT YOU SHOULD DO */}
                  <div className="report-section">
                    <h3 className="report-section-title">What you should do:</h3>
                    {analysisResult.recommendations && analysisResult.recommendations.length > 0 ? (
                      <ul className="report-bullet-list">
                        {analysisResult.recommendations.map((rec, idx) => (
                          <li key={idx} className="report-bullet-item">
                            {rec}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="report-clean-text">
                        Always verify unknown senders before clicking links or sharing personal data.
                      </p>
                    )}
                  </div>

                  {/* SUMMARY EXPLANATION (IF HELPFUL) */}
                  {analysisResult.explanation && (
                    <div className="report-summary-box">
                      <span className="summary-title">Summary:</span>
                      <p className="summary-text">{analysisResult.explanation}</p>
                    </div>
                  )}

                  {/* REPORT ACTIONS */}
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
                      <span>Scan Another Message</span>
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
