import React, { useState } from 'react';
import { 
  ShieldAlert, 
  PhoneCall, 
  ExternalLink, 
  ChevronDown, 
  ChevronUp, 
  ArrowRight,
  Search
} from 'lucide-react';

const SCAM_TOPICS = [
  {
    id: "upi",
    title: "UPI & QR Code Scams",
    looksLike: "A buyer on OLX or Facebook Marketplace says they want to pay you, or you receive a message about a cashback reward. They send a QR code or Google Pay/PhonePe 'Collect Request', telling you to enter your UPI PIN to receive the money.",
    warningSigns: [
      "Asking you to enter your UPI PIN or scan a QR code to 'receive' funds",
      "Sending a PhonePe / Google Pay 'Collect Request' disguised as a payment receipt",
      "Rushing you to make an immediate decision without checking your bank balance",
      "Sharing fake or edited transaction screenshots"
    ],
    neverShare: "Your UPI PIN, MPIN, or bank OTP.",
    whatToDo: [
      "Remember: You NEVER need to enter your UPI PIN to receive money.",
      "Decline and cancel any unfamiliar collect request in your UPI application.",
      "Block the sender and report the profile on the marketplace or chat app."
    ]
  },
  {
    id: "kyc",
    title: "Banking & KYC Update Scams",
    looksLike: "An SMS claiming that your SBI, HDFC, ICICI, or PNB bank account or debit card has been suspended and will be permanently closed within 24 hours unless you click an unverified link to update your PAN or Aadhaar card.",
    warningSigns: [
      "Artificial 24-hour urgency threatening immediate account deactivation",
      "SMS sent from a random 10-digit phone number instead of official bank headers (e.g. AD-HDFCBK)",
      "Links ending in unusual domain extensions (.xyz, .top, .live) or bit.ly shorteners",
      "Prompts to download an unofficial '.apk' file to complete verification"
    ],
    neverShare: "NetBanking passwords, card CVV, ATM PIN, or banking OTPs.",
    whatToDo: [
      "Never click links in unsolicited messages regarding KYC updates.",
      "Check your account status strictly through the official mobile banking app or branch.",
      "Forward fraudulent SMS to 1909 (TRAI spam reporting)."
    ]
  },
  {
    id: "jobs",
    title: "Fake Job & Part-Time Task Scams",
    looksLike: "Unsolicited WhatsApp or Telegram messages offering work from home: 'Earn Rs 3,000–5,000 daily by liking YouTube videos, reviewing Google Maps hotels, and submitting screenshots. Instant payouts via UPI'.",
    warningSigns: [
      "Unusually high daily pay for simple, unskilled tasks",
      "Initial small payments (Rs 150–500) given upfront to build false trust (baiting)",
      "Recruiter insists on moving the conversation exclusively to Telegram groups",
      "Demands upfront 'security deposits' or 'prepaid task deposits' to unlock higher earnings"
    ],
    neverShare: "Upfront registration fees, prepaid task deposits, or unwatermarked identity proofs.",
    whatToDo: [
      "Legitimate companies never hire via random WhatsApp messages or demand upfront fees.",
      "Refuse to transfer money for 'prepaid investment tasks'.",
      "Leave the Telegram group immediately and report the account."
    ]
  },
  {
    id: "courier",
    title: "Courier & Delivery Fee Scams",
    looksLike: "An SMS claiming an India Post, FedEx, or Blue Dart package cannot be delivered due to an incomplete address. You are asked to click a link and pay a nominal fee of Rs 25 within 12 hours to reschedule delivery.",
    warningSigns: [
      "Demands for a small fee (Rs 10–50) designed to lower your guard",
      "Lookalike website address that does not end in the official government domain (.gov.in)",
      "High urgency claiming the parcel will be discarded or returned immediately",
      "You receive tracking notices for items you never ordered"
    ],
    neverShare: "Debit or credit card details, CVV, or bank OTPs.",
    whatToDo: [
      "Verify tracking numbers directly on official logistics websites (e.g. indiapost.gov.in).",
      "Remember that Indian government portals always use domains ending in .gov.in or .nic.in.",
      "If card details were entered, immediately freeze the card using your banking app."
    ]
  },
  {
    id: "investment",
    title: "Investment & Stock Trading Scams",
    looksLike: "You are added to a VIP WhatsApp or Telegram stock trading group promising guaranteed 200% monthly returns through institutional AI stock picks, crypto signals, or privileged IPO allocations.",
    warningSigns: [
      "Guaranteed, risk-free high profits (SEBI-registered advisors never guarantee profits)",
      "Group members posting screenshots of massive daily profits (often fake accounts or bots)",
      "Directs you to download private '.apk' trading apps not found on Google Play Store",
      "Funds must be transferred to personal savings accounts instead of a registered broker"
    ],
    neverShare: "Money transfers to individual bank accounts, Demat credentials, or trading passwords.",
    whatToDo: [
      "Verify the advisor or broker's registration on the official SEBI portal (sebi.gov.in).",
      "Never invest money through WhatsApp groups or download private trading apps from web links.",
      "If money was transferred, collect transaction UTR numbers and dial 1930 immediately."
    ]
  },
  {
    id: "lottery",
    title: "Lottery & Prize Scams",
    looksLike: "A WhatsApp message or audio recording claiming you won Rs 25 Lakhs in the Kaun Banega Crorepati (KBC) or Amazon Lucky Draw, asking you to call a manager and pay 'GST' or 'processing fees' to claim the cheque.",
    warningSigns: [
      "Winning a contest, lottery, or lucky draw that you never entered",
      "Uses audio recordings, celebrity pictures, or forged government emblems",
      "Demands payment of 'GST', 'tax clearance', or 'file processing fee' before releasing funds",
      "Urgent payment requests via UPI to personal accounts"
    ],
    neverShare: "Any upfront processing fee, bank passbook copies, or identity documents.",
    whatToDo: [
      "Remember: It is impossible to win a lottery you never participated in.",
      "Never pay any 'processing fee' or 'GST' to claim a prize.",
      "Block the sender and report the message."
    ]
  },
  {
    id: "phishing",
    title: "Phishing & Credential Harvesting",
    looksLike: "An email or SMS claiming your Netflix, Microsoft, Google, or utility account will be suspended today due to payment failure, asking you to click a link to re-verify your password or billing card.",
    warningSigns: [
      "Sender email address does not match the official company domain",
      "Generic greetings like 'Dear Customer' instead of your name",
      "High urgency or threats of immediate service termination",
      "Lookalike domain names with subtle typos or strange subdomains"
    ],
    neverShare: "Account passwords, credit card numbers, CVVs, or security questions.",
    whatToDo: [
      "Check the sender's actual email address and browser address bar.",
      "Never click links in unexpected emails—navigate directly to the official service website.",
      "Test suspicious links using ScamShield AI's URL Scanner."
    ]
  }
];

export default function Education({ onNavigate }) {
  const [expandedId, setExpandedId] = useState("upi");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredTopics = SCAM_TOPICS.filter(t => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      t.title.toLowerCase().includes(q) ||
      t.looksLike.toLowerCase().includes(q) ||
      t.warningSigns.some(ws => ws.toLowerCase().includes(q))
    );
  });

  return (
    <div className="awareness-page">
      {/* 1. HEADER */}
      <div className="page-header">
        <h1 className="page-title">Scam Awareness</h1>
        <p className="page-subtitle">
          Learn how to spot common cyber scams in India and protect your personal information.
        </p>
      </div>

      {/* 2. PROMINENT "REMEMBER: NEVER SHARE" SECTION */}
      <section className="remember-box">
        <div className="remember-header">
          <ShieldAlert size={20} className="text-danger" />
          <h2 className="remember-title">Remember: Never Share These Details</h2>
        </div>
        
        <p className="remember-text">
          No bank, police officer, delivery agent, court official, or government authority will <strong>ever</strong> ask you to share:
        </p>

        <div className="secret-pills-grid">
          <div className="secret-pill">
            <strong>OTP</strong>
            <span>One-Time Password</span>
          </div>
          <div className="secret-pill">
            <strong>UPI PIN</strong>
            <span>Only for sending money</span>
          </div>
          <div className="secret-pill">
            <strong>ATM PIN</strong>
            <span>Card security code</span>
          </div>
          <div className="secret-pill">
            <strong>Password</strong>
            <span>NetBanking & Email</span>
          </div>
          <div className="secret-pill">
            <strong>CVV</strong>
            <span>3 digits on card back</span>
          </div>
          <div className="secret-pill">
            <strong>Banking Credentials</strong>
            <span>User IDs & Passwords</span>
          </div>
        </div>

        <div className="remember-note">
          If anyone asks for these details over a phone call, SMS, or WhatsApp message, <strong>hang up immediately</strong>. It is a scam.
        </div>
      </section>

      {/* 3. NATIONAL HELPLINE BANNER */}
      <div className="helpline-bar">
        <div className="helpline-left">
          <PhoneCall size={18} className="text-primary" />
          <div>
            <strong>National Cyber Crime Helpline: Dial 1930</strong>
            <span className="helpline-desc">Report financial frauds within the first 2 hours to freeze stolen funds.</span>
          </div>
        </div>
        <a 
          href="https://cybercrime.gov.in" 
          target="_blank" 
          rel="noopener noreferrer" 
          className="btn btn-secondary btn-sm"
        >
          <span>cybercrime.gov.in</span>
          <ExternalLink size={12} />
        </a>
      </div>

      {/* 4. SCAM CATEGORIES GUIDE */}
      <section className="section-block">
        <div className="section-header">
          <h2 className="section-title">Common Scam Types</h2>
          <div className="search-bar search-bar-compact">
            <Search size={14} className="search-icon" />
            <input
              type="text"
              className="search-input"
              placeholder="Filter topics..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        <div className="accordion-list">
          {filteredTopics.map((topic) => {
            const isExpanded = expandedId === topic.id;

            return (
              <div key={topic.id} className="accordion-item">
                <button
                  type="button"
                  className="accordion-header"
                  onClick={() => setExpandedId(isExpanded ? null : topic.id)}
                >
                  <span className="accordion-title">{topic.title}</span>
                  {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </button>

                {isExpanded && (
                  <div className="accordion-content">
                    {/* WHAT IT LOOKS LIKE */}
                    <div className="topic-block">
                      <h3 className="topic-label">What the scam looks like:</h3>
                      <p className="topic-desc">{topic.looksLike}</p>
                    </div>

                    {/* WARNING SIGNS */}
                    <div className="topic-block">
                      <h3 className="topic-label">Common warning signs:</h3>
                      <ul className="clean-bullet-list">
                        {topic.warningSigns.map((ws, i) => (
                          <li key={i}>{ws}</li>
                        ))}
                      </ul>
                    </div>

                    {/* WHAT NEVER TO SHARE */}
                    <div className="topic-block topic-danger-box">
                      <h3 className="topic-label text-danger">Never share:</h3>
                      <p className="topic-desc">{topic.neverShare}</p>
                    </div>

                    {/* WHAT TO DO */}
                    <div className="topic-block topic-safe-box">
                      <h3 className="topic-label text-safe">What you should do:</h3>
                      <ul className="clean-bullet-list">
                        {topic.whatToDo.map((step, i) => (
                          <li key={i}>{step}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
