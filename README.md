# ScamShield AI — AI-Powered Scam & Phishing Detection Platform

> **College Mini Project | Version 1.0**  
> An explainable cybersecurity platform that analyzes suspicious messages and URLs to estimate scam/phishing risk, identify explainable indicators, classify scam categories, and provide actionable safety recommendations.
> 
> 🌐 **Live Public Demo:** [scamshield-4fae.vercel.app](https://scamshield-4fae.vercel.app/)

---

## 🌐 Live Public Deployment

ScamShield AI is deployed and publicly accessible on Vercel:

- **Live URL:** [scamshield-4fae.vercel.app](https://scamshield-4fae.vercel.app/)
- **GitHub Repository:** [https://github.com/VScsaiml-pixel/ScamShield](https://github.com/VScsaiml-pixel/ScamShield)
- **Deployment Platform:** Vercel (Edge Network)

---

## 1. System Architecture

ScamShield AI utilizes a decoupled 3-tier architecture with a hybrid Machine Learning & Rule-based Explainable AI pipeline:

```
[ User Browser / Client ]
            │
            ▼
[ Frontend: React 19 + Vite ] ── (Port 5173)
            │ HTTP / REST API (or /api Proxy)
            ▼
[ Backend: FastAPI (Python 3.13) ] ── (Port 8000)
       ├── Pydantic Schemas (Input validation & sanitization)
       ├── API Routes (/api/health, /api/scan/status, /api/analyze/message)
       ├── ML Inference Engine:
       │     ├── Text Preprocessor (URL/Email/Phone/Money token masking)
       │     ├── TF-IDF Vectorizer (Unigrams + Bigrams, sublinear TF)
       │     ├── Calibrated Logistic Regression (Scam vs Legitimate)
       │     └── Multi-class Category Classifier (10 PRD Scam Vectors)
       ├── Explainable AI & Rule-Based Indicator Engine:
       │     ├── 13 Threat Indicator Detectors with Exact Evidence Extraction
       │     ├── Calibrated Mathematical Risk Scorer (0 - 100 Scale)
       │     ├── Grounded Natural-Language Synthesizer
       │     └── Category-Specific Actionable Safety Recommendations
       └── Privacy Utilities (SHA-256 hashing, credential redaction)
            │
            ▼
[ SQLite Database: SQLAlchemy ORM ]
       ├── users (user_id, name, email, password_hash, created_at)
       ├── scans (scan_id, input_type, input_hash, prediction, risk_score, category)
       ├── indicators (indicator_id, scan_id, indicator, severity, description)
       └── feedback (feedback_id, scan_id, user_label, comments, created_at)
```

---

## 2. Directory Structure

```
miniproject/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py           # Route aggregator
│   │   │   ├── health.py             # GET /api/health
│   │   │   ├── scan.py               # GET /api/scan/status
│   │   │   └── analyze.py            # POST /api/analyze/message (Core ML & Explainability)
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   │   ├── user.py, scan.py, indicator.py, feedback.py
│   │   ├── schemas/                  # Pydantic validation schemas
│   │   │   ├── health.py, scan.py
│   │   ├── ml/                       # Machine Learning Pipeline
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # BaseScamDetector abstract interface
│   │   │   ├── preprocessor.py       # Regex tokenization & text normalization
│   │   │   ├── rules.py              # 13 Rule-based indicators, risk scorer & explainer
│   │   │   ├── dataset_generator.py  # Realistic 335-sample dataset builder
│   │   │   ├── train.py              # TF-IDF + Logistic Regression training
│   │   │   ├── evaluate.py           # Evaluation script (Accuracy, F1, Confusion Matrix)
│   │   │   ├── pipeline.py           # Production hybrid inference engine
│   │   │   └── saved_models/         # Serialized artifacts (.joblib, metrics.json)
│   │   ├── utils/
│   │   │   └── security.py           # Privacy hashing & secret masking
│   │   ├── config.py, database.py, main.py
│   ├── data/
│   │   ├── scamshield.db             # Local SQLite database
│   │   ├── scam_dataset.csv          # Training dataset (335 samples)
│   │   └── scam_test_set.csv         # Held-out test split
│   ├── venv/                         # Python virtual environment
│   ├── test_api.py                   # Automated API test suite
│   ├── test_ml.py                    # Sample scam/legit validation suite
│   ├── test_explainability.py        # 12-case Explainable AI test suite
│   ├── requirements.txt              # Backend dependencies
│   └── run.py                        # Backend runner script
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx            # Live connection status
│   │   │   ├── HealthStatus.jsx      # Backend & SQLite status card
│   │   │   ├── ScannerPreview.jsx    # Interactive AI scanner with presets & evidence chips
│   │   │   ├── ArchitectureCard.jsx  # System breakdown & roadmap
│   │   │   └── Footer.jsx            # Disclaimer & metadata
│   │   ├── services/api.js           # Frontend API client
│   │   ├── App.jsx, App.css, index.css
│   └── package.json, vite.config.js
├── .gitignore, .env.example
└── README.md
```

---

## 3. Explainable AI & Risk Scoring Engine

### A. Hybrid Detection Model
The system never relies on black-box predictions alone. It computes an auditable hybrid result:
1. **Statistical ML**: A calibrated Logistic Regression classifier operating on unigram/bigram TF-IDF features outputs the probability $P(\text{scam}) \in [0, 1]$.
2. **Rule-Based Engine**: Identifies specific threat mechanisms with exact text evidence matches.

### B. Detected Threat Indicators
The system inspects each message for 13 distinct threat signals:

| Indicator | Severity | Description |
| :--- | :--- | :--- |
| **Urgent language detected** | High | High-pressure time limits (e.g., `'within 24 hours'`, `'immediately'`). |
| **Threats of account suspension** | High | Threats of account/card/utility suspension, deletion, or arrest. |
| **Requests for OTP** | Critical | Direct solicitation of one-time SMS verification codes. |
| **Requests for PIN** | Critical | Deceptive requests for UPI PIN, MPIN, or ATM PIN. |
| **Requests for passwords** | Critical | Attempts to harvest netbanking passwords or login passcodes. |
| **Requests for card/bank details** | Critical | Harvesting CVV, 16-digit card numbers, or expiration dates. |
| **Suspicious payment request** | Critical | Deceptive claims that scanning QR codes or paying a fee credits funds. |
| **Unrealistic rewards** | High | Promises of 200% returns, unprompted cashbacks, or free devices. |
| **Lottery/prize claims** | High | Claims of winning unentered lotteries or KBC lucky draws. |
| **Fake job offers** | High | Inflated daily pay for liking YouTube videos or typing tasks. |
| **Suspicious links** | Medium | Shortened links (`bit.ly`, `tinyurl`) or risky TLDs (`.xyz`, `.top`, `.tk`). |
| **KYC/account verification requests** | High | Demands for urgent PAN, Aadhaar, or re-KYC linking. |
| **Impersonation of authorities** | High | Impersonation of SBI, HDFC, CBI, Police, Income Tax, or Netflix. |

### C. Mathematical Risk Scoring (0–100)
The risk score is calculated mathematically from calibrated signals rather than arbitrary values:

$$\text{Score} = \min(100.0, \, S_{\text{ML}} + S_{\text{Rules}} + S_{\text{Synergy}})$$

- **ML Component ($S_{\text{ML}}$)**: Up to 50 points ($P(\text{scam}) \times 50.0$).
- **Rule Component ($S_{\text{Rules}}$)**: Up to 50 points based on indicator weights (Critical: 18–22 pts, High: 10–14 pts, Medium: 6–8 pts).
- **Synergy Boost ($S_{\text{Synergy}}$)**: Co-occurrence of critical credential harvesting with high ML confidence adds up to +13 points.
- **Benign Urgency Dampening**: Isolated urgency words in non-financial, non-credential contexts (e.g., *"urgent team meeting"*) are prevented from triggering false alarms.

#### Calibrated Risk Bands:
- **0 – 30**: **Low Risk** (Legitimate communication)
- **31 – 60**: **Medium Risk** (Potentially suspicious, exercise caution)
- **61 – 80**: **High Risk** (Suspicious solicitation)
- **81 – 100**: **Critical Risk** (High-confidence fraudulent attack)

### D. Grounded Natural-Language Explanations
For every scan, the engine synthesizes an explanation grounded in the exact detected evidence:
> *"This message appears to be a high-risk scam attempt because it combines urgent language detected (e.g. 'immediately'), threats of account suspension (e.g. 'suspended'), suspicious links (e.g. '.xyz') matching established Banking / KYC Phishing attack patterns."*

### E. Actionable Safety Recommendations
Tailored guidance provided according to the detected risk vector:
- **UPI Scams**: Clear warning that entering a UPI PIN always debits funds, never credits them.
- **Banking / KYC**: Instructions that banks never threaten suspension via SMS or third-party links.
- **Job / Task Scams**: Notice that legitimate employers never recruit exclusively via Telegram or ask for upfront deposits.
- **Official Reporting**: Direct referral to the National Cyber Crime Portal (cybercrime.gov.in / helpline 1930).

---

## 4. How to Run Locally

### Option 1: Single Unified Localhost (Everything on `http://127.0.0.1:8000`)
Run the unified launcher from the project root:
```bash
python run_app.py
```
*(Or double-click `start.bat` on Windows)*

Everything runs seamlessly on **one single URL**:
- **Web UI & Dashboard**: `http://127.0.0.1:8000/`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Health Check API**: `http://127.0.0.1:8000/api/health`

---

### Option 2: Separate Frontend Dev Server (Vite Hot-Reload)
If actively developing frontend React components:
1. **Backend**:
   ```bash
   cd backend
   .\venv\Scripts\python run.py
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   *Dashboard on `http://localhost:5173`, API proxied automatically to `8000`.*

---

## 5. Automated Verification & Testing

Run all test suites from the `backend/` directory:

```powershell
cd backend

# 1. Run 12-sample Explainable AI & Risk Scoring Test
.\venv\Scripts\python test_explainability.py

# 2. Run Sample Prediction Validation Suite
.\venv\Scripts\python test_ml.py

# 3. Run Automated API & Database Persistence Test
.\venv\Scripts\python test_api.py

# 4. Run Model Benchmark (Accuracy, Recall, Precision, Confusion Matrix)
.\venv\Scripts\python app/ml/evaluate.py
```

---

## 6. API Reference: `POST /api/analyze/message`

**Endpoint**: `http://127.0.0.1:8000/api/analyze/message`

**Input Payload:**
```json
{
  "message": "Dear SBI customer, your YONO account has been suspended due to pending KYC. Update PAN at http://sbi-kyc-verify.xyz immediately to unblock within 24 hours."
}
```

**Output Payload:**
```json
{
  "prediction": "Scam",
  "risk_score": 94.7,
  "risk_level": "Critical",
  "category": "Banking / KYC Phishing",
  "confidence": 0.79,
  "indicators": [
    {
      "indicator": "Urgent language detected",
      "severity": "high",
      "description": "Uses high-pressure or panic-inducing time limits to force hurried action.",
      "evidence": "'immediately'"
    },
    {
      "indicator": "Threats of account suspension",
      "severity": "high",
      "description": "Threatens immediate suspension, deletion, blockage of accounts, cards, utilities, or legal action.",
      "evidence": "'suspended'"
    },
    {
      "indicator": "Suspicious links",
      "severity": "medium",
      "description": "Employs URL shorteners, IP addresses, or low-reputation top-level domains to hide true destinations.",
      "evidence": "'.xyz'"
    },
    {
      "indicator": "KYC/account verification requests",
      "severity": "high",
      "description": "Demands immediate submission of government identity or KYC documents through unverified links.",
      "evidence": "'YONO account'"
    },
    {
      "indicator": "Impersonation of banks/government/companies",
      "severity": "high",
      "description": "Impersonates trusted institutions like banks, law enforcement, or global brands to establish false trust.",
      "evidence": "'SBI customer'"
    }
  ],
  "risk_breakdown": {
    "ml_contribution": 39.7,
    "rule_contribution": 50.0,
    "synergy_boost": 5.0,
    "total_indicators_detected": 5
  },
  "explanation": "This message appears to be a high-risk scam attempt because it combines urgent language detected (e.g. 'immediately'), threats of account suspension (e.g. 'suspended'), suspicious links (e.g. '.xyz') matching established Banking / KYC Phishing attack patterns.",
  "recommendations": [
    "Do NOT click any links, open attachments, or visit unverified websites mentioned in the message.",
    "Banks never threaten account suspension via SMS or third-party links. Verify directly through your official mobile banking app or branch.",
    "Verify the sender independently using contact details from the organization's official website.",
    "Report suspected cyber frauds immediately to the National Cyber Crime Portal (cybercrime.gov.in or helpline 1930 in India)."
  ],
  "input_preview": "Dear SBI customer, your YONO account has been suspended due to pending KYC. Update PAN at http://sbi-kyc-verify.xyz imme...",
  "scan_id": 10,
  "analyzed_at": "2026-10-07T10:08:41.381961Z"
}
```

---

## 7. URL Scam & Phishing Scanner (PRD Section 14)

### A. Passive Safe-Mode Architecture
In compliance with strict security principles, the URL scanner executes **passive lexical static analysis**:
- **Zero Network Execution**: The backend never opens, pings, downloads from, or executes user-submitted URLs.
- **Pure String Feature Extraction**: Evaluates scheme, host, ports, subdomains, file extensions, and encoding purely via string heuristics.
- **Optional External Threat-Intel**: Pluggable threat-intelligence APIs (e.g. VirusTotal/Google Safe Browsing). If no API key is provided, the system seamlessly operates in 100% offline local static analysis mode without failing.

### B. Static Threat Indicators Detected
The engine detects 13 distinct URL-level attack vectors:

| Indicator | Severity | Detection Rule |
| :--- | :--- | :--- |
| **Raw IP Address Host** | Critical | Numeric IPv4 host (e.g., `192.168.1.100`) evading domain reputation. |
| **Userinfo Redirection (@)** | Critical | Credential trick forcing browser navigation to suffix domain (`google.com@phish.xyz`). |
| **Malicious Executable Download** | Critical | Paths ending in dangerous executables or trojans (`.apk`, `.exe`, `.scr`, `.bat`). |
| **Brand Impersonation / Spoofing** | Critical | Trusted brand names (`sbi`, `hdfc`, `paytm`, `netflix`) in unauthorized non-whitelisted domains. |
| **High-Risk Top-Level Domain** | High | Low-cost or heavily abused TLDs (`.xyz`, `.top`, `.tk`, `.ml`, `.ga`, `.click`). |
| **Non-Standard Port** | High | Unconventional web ports (`:8080`, `:8888`) bypassing standard port 80/443 filters. |
| **Phishing / Action Keywords** | High | Credential harvesting keywords (`login`, `kyc`, `verify`, `update`, `claim`, `reward`). |
| **Excessive Subdomain Nesting** | High | 2 or more nested subdomains crafting deceptive visual replicas. |
| **Obfuscated Link Shortener** | Medium | Shortening services (`bit.ly`, `tinyurl`, `t.co`) hiding true destinations. |
| **Unencrypted HTTP Scheme** | Medium | Plaintext HTTP lacking SSL/TLS encryption. |
| **Excessive URL Length** | Medium/High | URLs exceeding 75 or 110 characters concealing parameters. |
| **Excessive Domain Hyphens** | Medium | 3 or more hyphens chained together (`secure-login-update-service`). |
| **Hexadecimal Percent Encoding** | Medium | Multiple `%XX` tokens obfuscating destinations. |

---

## 8. API Reference: `POST /api/analyze/url`

**Endpoint**: `http://127.0.0.1:8000/api/analyze/url`

**Input Payload:**
```json
{
  "url": "http://indiapost-parcel-tracking.top/download/update.apk"
}
```

**Output Payload:**
```json
{
  "url": "http://indiapost-parcel-tracking.top/download/update.apk",
  "prediction": "Scam",
  "risk_score": 100.0,
  "risk_level": "Critical",
  "category": "High-Risk Phishing Link / Fraudulent Domain",
  "confidence": 0.88,
  "indicators": [
    {
      "indicator": "Direct Executable / Malware Payload Download (.APK)",
      "severity": "critical",
      "description": "Directly links to executable files or Android APK packages commonly used to install banking trojans.",
      "evidence": "'.apk' in path"
    },
    {
      "indicator": "Brand Name Impersonation in Unofficial Domain ('INDIAPOST')",
      "severity": "critical",
      "description": "Uses the trusted brand name 'INDIAPOST' inside a third-party non-official domain to deceive victims.",
      "evidence": "'indiapost' in 'indiapost-parcel-tracking.top'"
    },
    {
      "indicator": "High-Risk Top-Level Domain (.top)",
      "severity": "high",
      "description": "The '.top' domain extension is frequently associated with disposable, low-cost phishing and spam infrastructure.",
      "evidence": "'.top'"
    },
    {
      "indicator": "Phishing-Related Keywords in URL",
      "severity": "high",
      "description": "Contains sensitive security keywords ('login', 'kyc', 'verify', 'update') commonly deployed on credential harvesting landing pages.",
      "evidence": "['update']"
    },
    {
      "indicator": "Unencrypted HTTP Scheme (Missing HTTPS)",
      "severity": "medium",
      "description": "Transmits data over unencrypted HTTP, leaving communications vulnerable to interception and identity tampering.",
      "evidence": "'http://'"
    }
  ],
  "features": {
    "scheme": "http",
    "host": "indiapost-parcel-tracking.top",
    "is_https": false,
    "is_ip_address": false,
    "has_unusual_port": false,
    "subdomain_count": 0,
    "url_length": 56,
    "tld": "top",
    "is_shortener": false
  },
  "threat_intel_status": "Local Static Analysis (External Threat-Intel Optional / Not Configured)",
  "explanation": "This URL appears to be a high-risk phishing destination because it exhibits direct executable / malware payload download (.apk), brand name impersonation in unofficial domain ('indiapost'), high-risk top-level domain (.top).",
  "recommendations": [
    "Do NOT open, click, or load this link in your browser.",
    "Never download or execute files (.apk, .exe) downloaded from unsolicited or unverified URLs.",
    "This link attempts to impersonate 'INDIAPOST'. Navigate directly to the official website instead.",
    "Report suspected malicious URLs to Google Safe Browsing and the National Cyber Crime Portal (cybercrime.gov.in / dial 1930 in India)."
  ],
  "scan_id": 21,
  "analyzed_at": "2026-10-07T10:31:18.910000Z"
}
```

---

## 9. Running URL Scanner Tests

```powershell
cd backend
.\venv\Scripts\python test_url_scanner.py
```
*Validates 10 attack classes: Raw IP hosts, brand spoofing, trojan APK downloads, `@` userinfo tricks, link shorteners, and official whitelisted domains.*

---

## 10. Persistent Scan History & SQLite Privacy Architecture

### A. Privacy-First Storage Policy (Zero-Knowledge Credentials)
In compliance with strict data protection guidelines, **no sensitive user credentials are ever stored** in the SQLite database (`data/scamshield.db`):
- **Card Numbers**: Replaced with `[REDACTED_CARD]`
- **CVVs / CVCs**: Replaced with `[REDACTED_CVV]`
- **OTPs & PINs**: Replaced with `[REDACTED_OTP_PIN]`
- **Passwords & Passcodes**: Replaced with `[REDACTED_PWD]`
- **Auth Tokens (JWTs, Bearers)**: Replaced with `[REDACTED_TOKEN]`
- **Cryptographic Fingerprint**: Retains a SHA-256 hash (`input_hash`) for deduplication and audit integrity without plaintext retention.

### B. Scan History API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/scans` | Returns chronological scan history with pagination (`limit`, `offset`) and filters (`scan_type`, `risk_level`). |
| `GET` | `/api/scans/{id}` | Returns complete scan details including detected indicators, explanation, and recommendations. |
| `DELETE` | `/api/scans/{id}` | Permanently deletes a single scan record and cascades to related indicators. |
| `DELETE` | `/api/scans` | Purges all scan history records from the local SQLite database. |

### C. Frontend History Dashboard
Accessible directly at **`http://localhost:8000/`** under the **`SCAN HISTORY`** tab:
- **Card List**: Displays date/time, scan type (`MESSAGE` vs `URL`), risk score (0–100), risk level tag, category, and sanitized preview.
- **Filters & Search**: Filter by scan type (All, Messages, URLs) or search by keyword/preview snippet.
- **Detail Modal**: Opens a modal displaying full explainability indicators, explanation, and safety recommendations.
- **Record Deletion & Purge**: Delete individual records or clear all history with safety confirmation.
- **Empty & Error States**: Graceful UI when no records exist or when network errors occur.

### D. Running History & Privacy Tests

```powershell
cd backend
.\venv\Scripts\python test_history.py
```
*Validates credential sanitization, SQLite persistence across process reboots, item retrieval, and deletion endpoints.*

---

## 11. Main Dashboard & System Navigation

### A. Real-Time Security Metrics
The dashboard connects directly to the SQLite audit database via `GET /api/dashboard/stats`:
- **KPI Metrics**: Total scans, Critical threats, High-risk scans, Medium-risk scans, Low-risk benign scans, and Overall Threat Rate.
- **Risk Band Donut Chart**: Segmented SVG Donut visualizing percentage proportions of Critical, High, Medium, and Low risk scans with central average score.
- **Scan Activity Timeline**: Multi-bar trend chart displaying daily volumes of threats vs clean scans over the past 7 days.
- **Scam Category Distribution**: Ranked horizontal progress bars showing threat vectors detected in real scans.
- **Recent Activity Table**: Instant preview table of the latest scans with risk tags and quick links to full audit details.

---

## 9. Scam Awareness & Cyber Education Module

ScamShield AI provides a comprehensive, beginner-friendly cybersecurity educational center specifically tailored to modern fraud vectors operating across India.

### A. Golden Security Rule: The 6 Secrets NEVER to Share

A dedicated, high-visibility cybersecurity advisory highlights the six critical credentials legitimate organizations will **never** request:
1. **OTP (One-Time Password)**: Grants authentication & authorizes funds transfer; never share with anyone, including bank officials or delivery staff.
2. **UPI PIN**: Secret 4/6-digit authorization code; strictly used to **pay/debit** funds, **never** required to receive money or claim refunds.
3. **ATM PIN**: Card security PIN; never disclose over calls or enter on websites.
4. **Passwords**: NetBanking, email, and portal logins; protect with 2FA and never reuse.
5. **CVV**: 3-digit card verification code; used to charge cards online.
6. **Banking Credentials**: NetBanking IDs, account numbers, and debit card PINs.

> **Universal Rule of Thumb:** If any caller, SMS, WhatsApp message, or website requests any of these 6 credentials, it is **100% a scam**. Disconnect immediately.

### B. 10 Comprehensive Scam Playbooks

Each of the 10 categories features an expandable breakdown with 5 structured components:
- **1. What the Scam Looks Like**: Realistic scenario description + simulated realistic message bubble with one-click "Copy Sample" and "Test in Scanner".
- **2. Common Warning Signs**: Telltale behavioral and technical red flags.
- **3. What Scammers Usually Ask For**: Concrete attack requests (APKs, screen sharing, prepaid deposits).
- **4. What the User Should NEVER Share**: High-contrast danger block with explicit non-negotiable items.
- **5. What You Should Do If Received**: Actionable, step-by-step protective instructions.

#### The 10 Threat Vectors Covered:
1. **UPI Scams**: QR code collect requests, fake OLX buyer transactions, cashback reward traps.
2. **Banking / KYC Scams**: 24-hour account suspension warnings, unblock APKs, fake PAN/Aadhaar updates.
3. **Fake Job / Internship Scams**: YouTube like/subscribe tasks, hotel ratings, Telegram prepaid investment schemes.
4. **Courier Scams**: India Post / FedEx unpaid address correction fee of Rs 25, customs clearance phishing.
5. **Lottery / Prize Scams**: KBC lucky draw, Amazon anniversary car/cash prizes, advance GST clearance fees.
6. **Investment Scams**: VIP WhatsApp/Telegram trading groups, guaranteed 200% returns, unverified trading APKs.
7. **Government Impersonation**: Digital arrest over Skype/WhatsApp video calls by fake CBI, ED, or Cyber Police.
8. **Customer-Care Scams**: Fake Google Maps helpline numbers, AnyDesk / TeamViewer remote screen control.
9. **Account Takeover**: Accidental 6-digit WhatsApp code forwarding, 5G SIM swap attacks.
10. **Phishing**: Cloned streaming & cloud billing portals, lookalike domains, urgent credential resets.

### C. Interactive Features & Emergency Response
- **Real-Time Search & Category Filters**: Quickly find fraud types by keyword or category pill (Banking & UPI, Jobs & Wealth, Delivery & Rewards, Impersonation & Phishing, Account Security).
- **Interactive Suspicion Triage**: 4-point checkbox self-test alerting users to high-risk message characteristics.
- **Emergency Incident Response Protocol**: 4-step emergency action plan covering immediate card freezing, Golden Hour reporting via **Dial 1930**, filing evidence on **cybercrime.gov.in**, and security credentials rotation.




