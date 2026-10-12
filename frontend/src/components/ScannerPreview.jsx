import React, { useState } from 'react';
import { 
  MessageSquare, 
  Link, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle, 
  AlertCircle, 
  ShieldAlert, 
  Sparkles, 
  ArrowRight,
  RefreshCw,
  ListChecks,
  Activity
} from 'lucide-react';
import { analyzeMessage } from '../services/api';

const SAMPLE_PRESETS = [
  {
    label: "SBI KYC Scam",
    type: "scam",
    text: "Dear SBI customer, your YONO account has been suspended due to pending KYC. Update PAN at http://sbi-kyc-verify.xyz immediately to unblock within 24 hours."
  },
  {
    label: "UPI Cashback Trap",
    type: "scam",
    text: "Congratulations! You have received a cashback refund of Rs 2,500 on PhonePe. Scan this QR code and enter your secret UPI PIN to receive money."
  },
  {
    label: "CBI Digital Arrest",
    type: "scam",
    text: "CBI Cyber Cell: Illegal media was accessed from your IP address. Contact investigating officer on Skype immediately to avoid digital arrest."
  },
  {
    label: "Netflix CVV Theft",
    type: "scam",
    text: "Dear Netflix subscriber, your monthly subscription payment failed. Update your card number, CVV, and expiration date at http://netflix-billing-update.xyz to prevent service cancellation."
  },
  {
    label: "Fake YouTube Job",
    type: "scam",
    text: "Urgent Part-time Work From Home! Earn Rs 3,000 to 5,000 daily by liking YouTube videos. No experience needed. Join Telegram: t.me/fast_earn_india"
  },
  {
    label: "Postal Customs Fee",
    type: "scam",
    text: "India Post: Your package #IND9821 cannot be delivered due to invalid street address. Update address and pay Rs 25 redelivery fee at http://bit.ly/ind-post"
  },
  {
    label: "Suspicious Document Link",
    type: "suspicious",
    text: "Hey, please click this link right now to view the shared document: http://bit.ly/confidential-file"
  },
  {
    label: "Legitimate Bank Alert",
    type: "legit",
    text: "Rs 1,500.00 debited from A/C XX4921 on 07-Oct-26 at Swiggy UPI. Available balance: Rs 24,310.50. - HDFC Bank"
  },
  {
    label: "Legitimate Job Invitation",
    type: "legit",
    text: "Hi Vanshika, thank you for applying to the Software Engineering Intern role at Microsoft. We invite you for a 45-minute technical interview on Thursday."
  },
  {
    label: "Benign Urgent Meeting",
    type: "legit",
    text: "Urgent team meeting rescheduled to 4 PM today in Boardroom B. Please bring project presentation slides."
  }
];

export default function ScannerPreview({ scannerStatus }) {
  const [activeTab, setActiveTab] = useState('text');
  const [inputText, setInputText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);

  const handleAnalyze = async () => {
    if (!inputText.trim()) return;

    setIsAnalyzing(true);
    setAnalysisError(null);

    const res = await analyzeMessage(inputText.trim());
    if (res.success) {
      setAnalysisResult(res.data);
    } else {
      setAnalysisError(res.error);
    }
    setIsAnalyzing(false);
  };

  const loadPreset = (presetText) => {
    setInputText(presetText);
    setAnalysisResult(null);
    setAnalysisError(null);
  };

  const getRiskColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical': return 'risk-critical';
      case 'high': return 'risk-high';
      case 'medium': return 'risk-medium';
      default: return 'risk-low';
    }
  };

  return (
    <div className="card scanner-preview-card">
      <div className="card-header">
        <div className="header-title">
          <ShieldCheck className="icon-primary" size={20} />
          <h3>Explainable AI Scam Scanner</h3>
        </div>
        <div className="tab-pill-group">
          <button
            className={`tab-pill ${activeTab === 'text' ? 'active' : ''}`}
            onClick={() => setActiveTab('text')}
          >
            <MessageSquare size={14} />
            <span>Message Scanner (Active)</span>
          </button>
          <button
            className={`tab-pill ${activeTab === 'url' ? 'active' : ''}`}
            onClick={() => setActiveTab('url')}
          >
            <Link size={14} />
            <span>URL Analyzer (Phase 6)</span>
          </button>
        </div>
      </div>

      <div className="scanner-body">
        {/* Sample presets for quick testing */}
        <div className="preset-container">
          <span className="preset-label">Quick Test Presets (10 PRD Cases):</span>
          <div className="preset-buttons">
            {SAMPLE_PRESETS.map((p, idx) => (
              <button
                key={idx}
                type="button"
                className={`btn-preset ${p.type}`}
                onClick={() => loadPreset(p.text)}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {activeTab === 'text' ? (
          <div className="input-preview-group">
            <label className="input-label">
              <span>Paste Suspicious Message (SMS, WhatsApp, Email, Telegram)</span>
              <span className="label-tip">Hybrid ML + 13 Rule-based Indicators</span>
            </label>
            <textarea
              className="text-preview-input"
              rows={4}
              placeholder="Paste suspicious SMS, WhatsApp, or email message to evaluate..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
            <div className="action-row">
              <button
                className="btn-analyze"
                disabled={!inputText.trim() || isAnalyzing}
                onClick={handleAnalyze}
              >
                {isAnalyzing ? (
                  <>
                    <RefreshCw size={16} className="spinning" />
                    <span>Analyzing Indicators & Risk...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    <span>Scan Message with AI</span>
                    <ArrowRight size={14} />
                  </>
                )}
              </button>
              {inputText && (
                <button
                  className="btn-clear"
                  onClick={() => { setInputText(''); setAnalysisResult(null); }}
                >
                  Clear
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="input-preview-group">
            <label className="input-label">
              <span>Enter Suspicious URL for Safe Static Inspection</span>
              <span className="label-tip">Will be implemented in Phase 6</span>
            </label>
            <input
              type="text"
              className="url-preview-input"
              placeholder="https://sbi-secure-login.suspicious-domain.tk/verify"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
          </div>
        )}

        {analysisError && (
          <div className="error-banner">
            <AlertCircle size={18} />
            <span>{analysisError}</span>
          </div>
        )}

        {/* Real-time Analysis Result Card */}
        {analysisResult && (
          <div className={`result-box ${getRiskColor(analysisResult.risk_level)}`}>
            <div className="result-header">
              <div className="result-badge-group">
                <span className={`prediction-badge ${analysisResult.prediction.toLowerCase()}`}>
                  {analysisResult.prediction === 'Scam' && <ShieldAlert size={16} />}
                  {analysisResult.prediction === 'Suspicious' && <AlertTriangle size={16} />}
                  {analysisResult.prediction === 'Legitimate' && <CheckCircle size={16} />}
                  {analysisResult.prediction}
                </span>
                <span className={`risk-level-badge ${getRiskColor(analysisResult.risk_level)}`}>
                  {analysisResult.risk_level} Risk
                </span>
                <span className="category-pill">{analysisResult.category}</span>
              </div>
              <div className="risk-score-display">
                <span className="score-num">{analysisResult.risk_score}</span>
                <span className="score-max">/100</span>
              </div>
            </div>

            {/* Score progress bar */}
            <div className="score-bar-bg">
              <div 
                className="score-bar-fill" 
                style={{ width: `${Math.min(100, Math.max(5, analysisResult.risk_score))}%` }}
              ></div>
            </div>

            {/* Mathematical Risk Breakdown */}
            {analysisResult.risk_breakdown && (
              <div className="risk-breakdown-row">
                <div className="breakdown-item">
                  <Activity size={13} />
                  <span>ML Model: <strong>{analysisResult.risk_breakdown.ml_contribution} pts</strong></span>
                </div>
                <div className="breakdown-item">
                  <span>Rule Engine: <strong>{analysisResult.risk_breakdown.rule_contribution} pts</strong></span>
                </div>
                {analysisResult.risk_breakdown.synergy_boost > 0 && (
                  <div className="breakdown-item text-rose">
                    <span>Critical Synergy: <strong>+{analysisResult.risk_breakdown.synergy_boost} pts</strong></span>
                  </div>
                )}
                <div className="breakdown-item">
                  <span>Scale: 0-30 Low | 31-60 Med | 61-80 High | 81-100 Critical</span>
                </div>
              </div>
            )}

            {/* Grounded Human-Readable Explanation */}
            <div className="explanation-section">
              <span className="explanation-title">Why this was flagged:</span>
              <p className="result-explanation">"{analysisResult.explanation}"</p>
            </div>

            {/* Warning Indicators with Evidence */}
            {analysisResult.indicators && analysisResult.indicators.length > 0 && (
              <div className="result-indicators">
                <div className="indicator-title">
                  <AlertTriangle size={15} />
                  <span>Grounded Threat Indicators ({analysisResult.indicators.length}):</span>
                </div>
                <div className="indicator-list">
                  {analysisResult.indicators.map((ind, i) => (
                    <div key={i} className={`indicator-item sev-${ind.severity}`}>
                      <div className="ind-header-line">
                        <span className="ind-name">{ind.indicator}</span>
                        {ind.evidence && (
                          <span className="ind-evidence">Matched: {ind.evidence}</span>
                        )}
                        <span className={`ind-sev-tag ${ind.severity}`}>{ind.severity}</span>
                      </div>
                      <span className="ind-desc">{ind.description}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Actionable Recommendations */}
            {analysisResult.recommendations && analysisResult.recommendations.length > 0 && (
              <div className="result-recommendations">
                <div className="recs-title">
                  <ListChecks size={15} />
                  <span>Actionable Safety Guidance:</span>
                </div>
                <ul className="recs-list">
                  {analysisResult.recommendations.map((rec, i) => (
                    <li key={i}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="advisory-subtext">
              * Confidence: {Math.round(analysisResult.confidence * 100)}% • Advisory AI Output (PRD Section 20)
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
