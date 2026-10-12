import hashlib
import re


def hash_input(content: str) -> str:
    """Generate SHA-256 hash of text/URL for privacy-safe storage and indexing."""
    return hashlib.sha256(content.strip().encode("utf-8")).hexdigest()


def sanitize_and_mask_content(content: str, max_length: int = 150) -> str:
    """
    Strict Privacy Filter (PRD Section 11 & Privacy Requirement).
    Redacts sensitive personal credentials before database storage:
    - Credit/Debit Card Numbers (13-19 digits)
    - CVV/CVC codes
    - OTPs, PINs, UPI PINs, MPINs
    - Passwords & passcodes
    - Authentication Tokens (JWTs, API keys, Bearer tokens)
    - Phone numbers & Emails
    - URL userinfo credentials
    
    Returns a safe, masked preview text ensuring NO secrets are stored in SQLite.
    """
    text = content

    # 1. Redact URL Userinfo credentials (http://user:password@domain -> http://[REDACTED_AUTH]@domain)
    text = re.sub(r'([a-zA-Z]+://)[^/\s:@]+:[^/\s:@]+@', r'\1[REDACTED_AUTH]@', text)

    # 2. Redact Bearer / JWT / Auth Tokens
    text = re.sub(r'(bearer\s+)[a-zA-Z0-9_\-\.]{15,}', r'\1[REDACTED_TOKEN]', text, flags=re.IGNORECASE)
    text = re.sub(r'\beyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]+\b', '[REDACTED_JWT]', text)
    text = re.sub(r'(token|key|secret|auth|api_key)\s*[:=]\s*[a-zA-Z0-9_\-]{8,}', r'\1=[REDACTED_TOKEN]', text, flags=re.IGNORECASE)

    # 3. Redact Credit / Debit Card Numbers (13-19 digits, spaced or hyphenated)
    text = re.sub(r'\b(?:\d[ -]*?){13,19}\b', '[REDACTED_CARD]', text)

    # 4. Redact CVV / CVC (3-4 digits preceded or followed by cvv/cvc)
    text = re.sub(r'\b(cvv|cvc|security code)\s*[:=]?\s*\d{3,4}\b', r'\1 [REDACTED_CVV]', text, flags=re.IGNORECASE)

    # 5. Redact Passwords / Passcodes
    text = re.sub(r'\b(password|passwd|passcode|secret pin)\s*[:=]?\s*\S+', r'\1 [REDACTED_PWD]', text, flags=re.IGNORECASE)

    # 6. Redact OTPs and PINs (explicit OTP keywords followed by numbers)
    text = re.sub(r'\b(otp|one time password|pin|upi pin|mpin|verification code)\s*(?:is|:)?\s*\d{4,8}\b', r'\1 [REDACTED_OTP_PIN]', text, flags=re.IGNORECASE)

    # 7. Redact generic standalone 4-8 digit numbers (catch-all for unlabelled OTPs / PINs)
    text = re.sub(r'\b\d{4,8}\b', '[REDACTED_NUM]', text)

    # 8. Redact Phone numbers (+91 or 10 digits starting with 6-9)
    text = re.sub(r'(?:\+?91[\-\s]?)?[6-9]\d{9}\b', '[REDACTED_PHONE]', text)

    # 9. Redact Email addresses
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', text)

    # Clean whitespace and truncate
    clean_preview = " ".join(text.split())
    if len(clean_preview) > max_length:
        return clean_preview[:max_length] + "..."
    return clean_preview


# Alias for backward compatibility
mask_sensitive_preview = sanitize_and_mask_content
