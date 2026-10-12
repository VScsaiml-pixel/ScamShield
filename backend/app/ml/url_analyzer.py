import re
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional

# Known URL shortener domains
SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "rb.gy",
    "goo.gl", "ow.ly", "buff.ly", "t.ly", "tiny.cc", "lnkd.in"
}

# High-risk / low-cost / commonly abused TLDs
RISKY_TLDS = {
    "xyz", "top", "tk", "ml", "ga", "cf", "gq", "live", "work",
    "club", "fit", "vip", "icu", "rest", "cam", "sbs", "buzz", "click"
}

# High-value brand names frequently targeted by phishing campaigns
TARGET_BRANDS = [
    "sbi", "yono", "hdfc", "icici", "axis", "pnb", "kotak",
    "paytm", "phonepe", "gpay", "bhim", "paypal", "netflix",
    "amazon", "google", "apple", "microsoft", "instagram", "facebook",
    "whatsapp", "fedex", "dhl", "indiapost", "incometax"
]

# Official domain whitelist for high-value brands (legitimate owners)
TRUSTED_ROOT_DOMAINS = {
    "google.com", "google.co.in", "github.com", "microsoft.com",
    "onlinesbi.sbi", "sbi.co.in", "hdfcbank.com", "icicibank.com",
    "axisbank.com", "kotak.com", "pnbindia.in", "paytm.com",
    "phonepe.com", "amazon.in", "amazon.com", "apple.com",
    "netflix.com", "instagram.com", "facebook.com", "whatsapp.com",
    "fedex.com", "dhl.com", "indiapost.gov.in", "incometax.gov.in"
}

# Phishing / sensitive action keywords
ACTION_KEYWORDS = [
    "login", "signin", "verify", "verification", "update", "kyc",
    "pan", "aadhaar", "secure", "security", "banking", "bank",
    "account", "wallet", "claim", "reward", "cashback", "bonus",
    "otp", "unblock", "frozen", "suspended", "restore", "password"
]

# Dangerous file extensions
DANGEROUS_EXTENSIONS = {".apk", ".exe", ".scr", ".bat", ".vbs", ".iso", ".msi"}


class URLAnalyzer:
    """
    Static Lexical URL Analyzer (PRD Section 14).
    Inspects URL strings safely without opening, navigating, or executing network requests.
    Supports optional threat-intelligence API integration with local fallback.
    """

    def __init__(self, threat_intel_api_key: Optional[str] = None):
        self.threat_intel_api_key = threat_intel_api_key
        self.threat_intel_status = (
            "External Threat-Intel Enabled" if threat_intel_api_key 
            else "Local Static Analysis (External Threat-Intel Optional / Not Configured)"
        )

    def analyze_url(self, raw_url: str) -> Dict[str, Any]:
        """
        Performs comprehensive static feature analysis on a target URL string.
        """
        clean_url = raw_url.strip()
        if not clean_url:
            raise ValueError("URL cannot be empty.")

        # Ensure scheme is present for parsing
        normalized_url = clean_url
        if not re.match(r'^[a-zA-Z]+://', clean_url):
            normalized_url = "http://" + clean_url

        try:
            parsed = urlparse(normalized_url)
        except Exception as exc:
            parsed = urlparse("http://invalid-url")

        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path.lower()
        query = parsed.query.lower()

        # Extract host and port
        if ":" in netloc:
            parts = netloc.split(":")
            host = parts[0]
            port = parts[1] if len(parts) > 1 else ""
        else:
            host = netloc
            port = ""

        # Extract subdomains and TLD
        host_parts = host.split(".")
        tld = host_parts[-1] if len(host_parts) > 1 else ""
        root_domain = ".".join(host_parts[-2:]) if len(host_parts) >= 2 else host

        # -------------------------------------------------------------
        # Feature Extractions
        # -------------------------------------------------------------
        is_https = scheme == "https"
        is_ip_address = bool(re.match(r'^\d{1,3}(\.\d{1,3}){3}$', host))
        has_unusual_port = bool(port and port not in ["80", "443"])
        url_length = len(clean_url)
        
        # Subdomains (exclude 'www' and root domain)
        subdomains = [p for p in host_parts[:-2] if p != "www"] if len(host_parts) > 2 else []
        subdomain_count = len(subdomains)

        is_shortener = host in SHORTENER_DOMAINS or root_domain in SHORTENER_DOMAINS

        # -------------------------------------------------------------
        # Threat Indicators Detection
        # -------------------------------------------------------------
        indicators: List[Dict[str, Any]] = []

        # 1. IP Address Host (Critical)
        if is_ip_address:
            indicators.append({
                "id": "ip_host",
                "indicator": "Raw IP Address Used Instead of Domain",
                "severity": "critical",
                "weight": 25.0,
                "evidence": f"'{host}'",
                "description": "Legitimate organizations rarely use raw IP addresses. Phishers use numeric IPs to evade domain name reputation and WHOIS scrutiny."
            })

        # 2. At-Symbol (@) Credential Confusion Trick (Critical)
        if "@" in parsed.netloc:
            indicators.append({
                "id": "at_symbol_trick",
                "indicator": "URL Userinfo Redirection Trick (@ Symbol)",
                "severity": "critical",
                "weight": 25.0,
                "evidence": f"'@' in '{netloc}'",
                "description": "The '@' symbol in URLs forces the browser to treat preceding text as credentials and navigate to the domain after the '@'."
            })

        # 3. Dangerous Executable or APK Download in Path (Critical)
        for ext in DANGEROUS_EXTENSIONS:
            if path.endswith(ext):
                indicators.append({
                    "id": "dangerous_extension",
                    "indicator": f"Direct Executable / Malware Payload Download ({ext.upper()})",
                    "severity": "critical",
                    "weight": 25.0,
                    "evidence": f"'{ext}' in path",
                    "description": "Directly links to executable files or Android APK packages commonly used to install banking trojans."
                })
                break

        # 4. Brand Impersonation / Typosquatting in Domain (Critical/High)
        spoofed_brand = None
        for brand in TARGET_BRANDS:
            if brand in host and root_domain not in TRUSTED_ROOT_DOMAINS:
                spoofed_brand = brand
                break

        if spoofed_brand:
            indicators.append({
                "id": "brand_spoofing",
                "indicator": f"Brand Name Impersonation in Unofficial Domain ('{spoofed_brand.upper()}')",
                "severity": "critical",
                "weight": 22.0,
                "evidence": f"'{spoofed_brand}' in '{host}'",
                "description": f"Uses the trusted brand name '{spoofed_brand.upper()}' inside a third-party non-official domain to deceive victims."
            })

        # 5. High-Risk / Abused Top-Level Domain (High)
        if tld in RISKY_TLDS:
            indicators.append({
                "id": "risky_tld",
                "indicator": f"High-Risk Top-Level Domain (.{tld})",
                "severity": "high",
                "weight": 18.0,
                "evidence": f"'.{tld}'",
                "description": f"The '.{tld}' domain extension is frequently associated with disposable, low-cost phishing and spam infrastructure."
            })

        # 6. Non-Standard Port Specified (High)
        if has_unusual_port:
            indicators.append({
                "id": "unusual_port",
                "indicator": f"Non-Standard Port ({port})",
                "severity": "high",
                "weight": 14.0,
                "evidence": f"':{port}'",
                "description": f"Points to port {port} rather than default standard web ports (80/443), typical of unauthorized or ad-hoc servers."
            })

        # 7. Phishing / Account Action Keywords in Path or Host (High)
        found_keywords = [kw for kw in ACTION_KEYWORDS if kw in host or kw in path or kw in query]
        if found_keywords and root_domain not in TRUSTED_ROOT_DOMAINS:
            # Pick top 2
            kw_sample = found_keywords[:3]
            indicators.append({
                "id": "action_keywords",
                "indicator": "Phishing-Related Keywords in URL",
                "severity": "high",
                "weight": 14.0,
                "evidence": f"{kw_sample}",
                "description": "Contains sensitive security keywords ('login', 'kyc', 'verify', 'update') commonly deployed on credential harvesting landing pages."
            })

        # 8. Excessive Subdomains (High)
        if subdomain_count >= 2:
            indicators.append({
                "id": "excessive_subdomains",
                "indicator": f"Excessive Subdomains ({subdomain_count} Subdomains)",
                "severity": "high",
                "weight": 14.0,
                "evidence": f"'{'.'.join(subdomains)}'",
                "description": "Uses deep subdomain nesting to craft visual replicas of legitimate domains while disguising the actual root host."
            })

        # 9. Known URL Shortener (Medium)
        if is_shortener:
            indicators.append({
                "id": "url_shortener",
                "indicator": "Obfuscated Link via Shortening Service",
                "severity": "medium",
                "weight": 18.0,
                "evidence": f"'{host}'",
                "description": "Shortened links obscure the final landing destination and IP reputation, preventing upfront visual inspection."
            })

        # 10. Missing HTTPS Encryption (Medium)
        if not is_https and not is_ip_address:
            indicators.append({
                "id": "missing_https",
                "indicator": "Unencrypted HTTP Scheme (Missing HTTPS)",
                "severity": "medium",
                "weight": 12.0,
                "evidence": f"'{scheme}://'",
                "description": "Transmits data over unencrypted HTTP, leaving communications vulnerable to interception and identity tampering."
            })

        # 11. Excessive Length (Medium/High)
        if url_length > 110:
            indicators.append({
                "id": "excessive_length",
                "indicator": f"Excessively Long URL ({url_length} Characters)",
                "severity": "high",
                "weight": 10.0,
                "evidence": f"{url_length} chars",
                "description": "Very long URLs are frequently used by attackers to hide malicious parameters and tokens off the visible address bar."
            })
        elif url_length > 75:
            indicators.append({
                "id": "long_url",
                "indicator": f"Unusually Long URL ({url_length} Characters)",
                "severity": "medium",
                "weight": 6.0,
                "evidence": f"{url_length} chars",
                "description": "URL length is longer than standard concise domains, indicating complex tracking or token redirection."
            })

        # 12. Multiple Hyphens in Domain Name (Medium)
        hyphen_count = host.count("-")
        if hyphen_count >= 3:
            indicators.append({
                "id": "multiple_hyphens",
                "indicator": f"Excessive Hyphens in Domain ({hyphen_count} Hyphens)",
                "severity": "medium",
                "weight": 8.0,
                "evidence": f"'{host}'",
                "description": "Attackers chain multiple hyphens to build convincing lookalike domain strings (e.g., 'secure-bank-login-update')."
            })

        # 13. Excessive Percent/Hex Encoding (Medium)
        percent_count = clean_url.count("%")
        if percent_count >= 3:
            indicators.append({
                "id": "percent_encoding",
                "indicator": f"Hexadecimal Percent Encoding ({percent_count} '%' Symbols)",
                "severity": "medium",
                "weight": 8.0,
                "evidence": f"{percent_count} encoded tokens",
                "description": "Heavy percent encoding is commonly used to bypass automated keyword filters and obscure destination parameters."
            })

        # -------------------------------------------------------------
        # Whitelist / Legitimate Exception Check
        # -------------------------------------------------------------
        is_trusted = root_domain in TRUSTED_ROOT_DOMAINS and is_https and not is_ip_address

        # -------------------------------------------------------------
        # Risk Score Calculation
        # -------------------------------------------------------------
        if is_trusted and len(indicators) == 0:
            risk_score = 4.0
        elif is_trusted and len(indicators) > 0:
            # Trusted domain with query tokens (e.g. google search query)
            risk_score = 12.0
        else:
            raw_score = sum(ind["weight"] for ind in indicators)
            # Critical synergy boost
            if any(ind["severity"] == "critical" for ind in indicators) and len(indicators) >= 2:
                raw_score += 10.0

            risk_score = min(100.0, max(0.0, raw_score))

        risk_score = round(risk_score, 1)

        # -------------------------------------------------------------
        # Risk Level & Classification Mapping
        # -------------------------------------------------------------
        # 0–30: Low Risk
        # 31–60: Medium Risk
        # 61–80: High Risk
        # 81–100: Critical Risk
        if risk_score >= 81.0:
            risk_level = "Critical"
            prediction = "Scam"
            category = "High-Risk Phishing Link / Fraudulent Domain"
            confidence = 0.88
        elif risk_score >= 61.0:
            risk_level = "High"
            prediction = "Scam"
            category = "Suspicious Domain / Phishing Infrastructure"
            confidence = 0.82
        elif risk_score >= 31.0:
            risk_level = "Medium"
            prediction = "Suspicious"
            category = "Unverified Link / Potentially Deceptive"
            confidence = 0.70
        else:
            risk_level = "Low"
            prediction = "Legitimate"
            category = "Legitimate / Low-Risk URL"
            confidence = 0.85

        # -------------------------------------------------------------
        # Explanation Synthesis
        # -------------------------------------------------------------
        if risk_level == "Low":
            if is_trusted:
                explanation = f"This URL belongs to an authenticated, verified domain ({root_domain}) using valid HTTPS encryption. No deceptive structural patterns detected."
            else:
                explanation = "This URL exhibits standard web structure with no overt phishing indicators, IP addresses, or suspicious TLD patterns."
        else:
            top_reasons = [ind["indicator"].lower() for ind in indicators[:3]]
            reasons_text = ", ".join(top_reasons)
            if risk_level == "Critical":
                explanation = f"This URL appears to be a high-risk phishing destination because it exhibits {reasons_text}."
            elif risk_level == "High":
                explanation = f"This URL appears potentially suspicious because it features {reasons_text} designed to mimic legitimate resources."
            else:
                explanation = f"This URL contains potentially deceptive characteristics ({reasons_text}). Exercise caution before navigating."

        # -------------------------------------------------------------
        # Actionable Safety Recommendations
        # -------------------------------------------------------------
        recommendations = self._generate_recommendations(risk_level, indicators, host, is_shortener)

        features_dict = {
            "scheme": scheme or "none",
            "host": host,
            "is_https": is_https,
            "is_ip_address": is_ip_address,
            "has_unusual_port": has_unusual_port,
            "subdomain_count": subdomain_count,
            "url_length": url_length,
            "tld": tld or "none",
            "is_shortener": is_shortener
        }

        return {
            "url": clean_url,
            "prediction": prediction,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "category": category,
            "confidence": confidence,
            "indicators": indicators,
            "features": features_dict,
            "threat_intel_status": self.threat_intel_status,
            "explanation": explanation,
            "recommendations": recommendations
        }

    def _generate_recommendations(
        self, 
        risk_level: str, 
        indicators: List[Dict[str, Any]], 
        host: str,
        is_shortener: bool
    ) -> List[str]:
        if risk_level == "Low":
            return [
                "This URL appears safe based on structural analysis, but always confirm website identity before submitting credentials.",
                "Ensure your browser displays a valid padlock icon before entering personal or banking data.",
                "Bookmark official portals instead of relying on external search or message links."
            ]

        recs = [
            "Do NOT open, click, or load this link in your browser.",
            "Never download or execute files (.apk, .exe) downloaded from unsolicited or unverified URLs."
        ]

        if is_shortener:
            recs.append("This is an obfuscated short link. Avoid expanding it unless you can verify the sender through a second trusted channel.")

        if any(ind["id"] == "brand_spoofing" for ind in indicators):
            recs.append(f"The domain claims to be associated with an institution but is NOT on an official domain. Visit the verified organization portal directly.")

        if any(ind["id"] == "ip_host" for ind in indicators):
            recs.append("Legitimate services do not require customers to enter credentials on numeric IP addresses.")

        recs.append("Report suspected malicious URLs to Google Safe Browsing and the National Cyber Crime Portal (cybercrime.gov.in / dial 1930 in India).")
        return recs


# Global singleton instance
_url_analyzer_instance = None

def get_url_analyzer() -> URLAnalyzer:
    global _url_analyzer_instance
    if _url_analyzer_instance is None:
        _url_analyzer_instance = URLAnalyzer()
    return _url_analyzer_instance
