import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

from app.ml.pipeline import get_detector

SAMPLE_MESSAGES = [
    # 1. Banking KYC Scam
    {
        "type": "Scam (Banking/KYC)",
        "text": "Dear SBI customer, your YONO account has been suspended due to pending KYC. Update PAN at http://sbi-kyc-fix.xyz immediately to unblock."
    },
    # 2. UPI Payment Scam
    {
        "type": "Scam (UPI)",
        "text": "Congratulations! You have received a cashback refund of Rs 2,500 on PhonePe. Scan this QR code and enter your secret UPI PIN to receive money."
    },
    # 3. Fake Job Scam
    {
        "type": "Scam (Fake Job)",
        "text": "Urgent Part-time Work From Home! Earn Rs 3,000 to 5,000 daily by liking YouTube videos. No experience required. Join Telegram: t.me/fast_earn_india"
    },
    # 4. Government / Authority Impersonation
    {
        "type": "Scam (Impersonation)",
        "text": "CBI Cyber Cell: Illegal media was accessed from your IP address. Contact investigating officer on Skype immediately to avoid digital arrest."
    },
    # 5. Courier / Delivery Scam
    {
        "type": "Scam (Courier)",
        "text": "India Post: Your package #IND9821 cannot be delivered due to invalid street address. Update address and pay Rs 25 redelivery fee at http://bit.ly/ind-post"
    },
    # 6. Legitimate Bank SMS
    {
        "type": "Legitimate (Bank Transaction)",
        "text": "Rs 1,500.00 debited from A/C XX4921 on 07-Oct-26 at Swiggy UPI. Available balance: Rs 24,310.50. - HDFC Bank"
    },
    # 7. Legitimate Job Email
    {
        "type": "Legitimate (Job Interview)",
        "text": "Hi Vanshika, thank you for applying to the Software Engineering Intern role at Microsoft. We invite you for a 45-minute technical interview on Thursday."
    },
    # 8. Legitimate Delivery OTP
    {
        "type": "Legitimate (Courier OTP)",
        "text": "OTP for delivery of your Flipkart package is 7291. Share this OTP with the delivery agent only after inspecting your package."
    },
    # 9. Legitimate College Chat
    {
        "type": "Legitimate (College Teamwork)",
        "text": "Hey, are you free this evening around 6 PM? Let's catch up at the library to work on the mini project presentation."
    }
]

def test_samples():
    print("======================================================================")
    print("           SCAMSHIELD AI - SAMPLE PREDICTION TEST                     ")
    print("======================================================================")
    detector = get_detector()

    for i, item in enumerate(SAMPLE_MESSAGES, 1):
        print(f"\n[{i}] Expected Type: {item['type']}")
        print(f"Message: \"{item['text']}\"")
        result = detector.predict(item["text"])
        
        print(f"-> Prediction:   {result['prediction']} ({result['risk_level']} Risk)")
        print(f"-> Risk Score:   {result['risk_score']} / 100 (Confidence: {result['confidence'] * 100:.0f}%)")
        print(f"-> Category:     {result['category']}")
        print(f"-> Indicators:   {len(result['indicators'])} triggered ({[x['indicator'] for x in result['indicators']]})")
        print(f"-> Explanation:  {result['explanation']}")

if __name__ == "__main__":
    test_samples()
