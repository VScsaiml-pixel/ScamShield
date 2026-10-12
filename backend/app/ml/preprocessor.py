import re

class TextPreprocessor:
    """
    Standard NLP preprocessing pipeline for message & text scam detection.
    Normalizes text while preserving crucial scam signal tokens (URLs, phones, currency).
    """

    def __init__(self):
        # Regex patterns
        self.url_pattern = re.compile(r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.(?:com|org|net|in|co|xyz|top|info|live|tk|bit\.ly|tinyurl\.com)[^\s]*', re.IGNORECASE)
        self.email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+', re.IGNORECASE)
        self.upi_pattern = re.compile(r'[\w\.\-]+@(okhdfcbank|okaxis|oksbi|paytm|ybl|apl|upi)\b', re.IGNORECASE)
        self.phone_pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}|\b[6-9]\d{9}\b')
        self.money_pattern = re.compile(r'(?:(?:rs|inr|usd|\$|€|£|₹)\.?\s*[\d,]+(?:\.\d+)?)|(?:[\d,]+(?:\.\d+)?\s*(?:rs|inr|rupees|lakh|crore|dollars))', re.IGNORECASE)
        self.num_pattern = re.compile(r'\b\d+\b')
        self.whitespace_pattern = re.compile(r'\s+')

    def preprocess(self, text: str) -> str:
        """
        Cleans and tokenizes text input into normalized string.
        """
        if not text or not isinstance(text, str):
            return ""

        cleaned = text.strip()

        # Mask UPI handles
        cleaned = self.upi_pattern.sub(' [UPI_TOKEN] ', cleaned)

        # Mask URLs
        cleaned = self.url_pattern.sub(' [URL_TOKEN] ', cleaned)

        # Mask Emails
        cleaned = self.email_pattern.sub(' [EMAIL_TOKEN] ', cleaned)

        # Mask Currency & Monetary figures
        cleaned = self.money_pattern.sub(' [MONEY_TOKEN] ', cleaned)

        # Mask Phone numbers
        cleaned = self.phone_pattern.sub(' [PHONE_TOKEN] ', cleaned)

        # Mask general numbers
        cleaned = self.num_pattern.sub(' [NUM_TOKEN] ', cleaned)

        # Lowercase
        cleaned = cleaned.lower()

        # Remove strange non-ascii characters while preserving punctuation that carries sentiment (?, !)
        cleaned = re.sub(r'[^\w\s\?!.,\[\]]', ' ', cleaned)

        # Normalize whitespace
        cleaned = self.whitespace_pattern.sub(' ', cleaned).strip()

        return cleaned

# Singleton instance for simple importing
preprocessor = TextPreprocessor()

def preprocess_text(text: str) -> str:
    return preprocessor.preprocess(text)
