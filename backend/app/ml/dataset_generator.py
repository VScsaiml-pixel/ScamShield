import os
import csv
import random
from pathlib import Path

# Base hand-crafted templates with realistic variations
BANKS = ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "Punjab National Bank", "Kotak Mahindra Bank", "Bank of Baroda", "Canara Bank"]
SHORTENERS = ["bit.ly/kyc-fix", "tinyurl.com/bank-alert", "is.gd/sbi-verify", "cutt.ly/pan-link", "rb.gy/card-unblock", "sbi-kyc-portal.xyz", "hdfc-secure-auth.top"]
AMOUNTS = ["1,500", "2,499", "5,000", "10,000", "25,000", "50,000", "1,00,000", "25,00,000"]

BASE_SCAMS = [
    # Banking / KYC Phishing
    ("Dear {bank} customer, your account will be blocked today due to incomplete KYC. Update PAN at http://{url} immediately.", "Banking / KYC Phishing"),
    ("Alert: Your {bank} netbanking access is restricted. Verify your credentials and Aadhaar at http://{url} within 12 hours.", "Banking / KYC Phishing"),
    ("Your {bank} debit card is blocked. Call our verification manager at +919876543210 urgently to reactivate.", "Banking / KYC Phishing"),
    ("Urgent: {bank} reward points worth Rs {amount} expiring today. Redeem cash directly to your bank account at http://{url}", "Banking / KYC Phishing"),
    ("Attention: {bank} re-KYC deadline today. Failure to update PAN card at http://{url} will result in account freeze.", "Banking / KYC Phishing"),

    # UPI / Payment Scam
    ("Congratulations! You received a cashback of Rs {amount} on PhonePe. Scan QR code and enter your secret UPI PIN to credit your bank account.", "UPI / Payment Scam"),
    ("GooglePay alert: You won Rs {amount} cash voucher! Click http://{url} and enter UPI PIN to transfer funds.", "UPI / Payment Scam"),
    ("Paytm KYC refund of Rs {amount} approved. Accept collect request or enter PIN to claim credit instantly.", "UPI / Payment Scam"),
    ("OLX Buyer: I transferred Rs {amount} for your item. Scan this QR code in GPay to receive money directly.", "UPI / Payment Scam"),
    ("Special promo: Pay Rs 1 to receive Rs {amount} cashback into your linked bank account. Visit http://{url}", "UPI / Payment Scam"),

    # Fake Job / Internship
    ("Part-time Work From Home opportunity! Earn Rs 3,000 to 5,000 daily by rating hotels and liking YouTube videos. Join Telegram: t.me/jobs_india", "Fake Job / Internship"),
    ("Amazon HR: Selected for remote data entry associate. Daily payout Rs 2,500. No experience needed. Contact WhatsApp +919876541234.", "Fake Job / Internship"),
    ("Google India Internship 2026: Direct selection without technical interview! Stipend Rs {amount}/month. Pay Rs 999 registration fee at http://{url}", "Fake Job / Internship"),
    ("Earn daily income from home: Simple typing tasks. Payout sent every evening via UPI. Deposit Rs 500 security fee to receive project files.", "Fake Job / Internship"),
    ("Netflix subtitle reviewer: Earn $40/hr watching movies. Submit refundable documentation fee to confirm hiring.", "Fake Job / Internship"),

    # Lottery / Prize Scam
    ("Dear customer, your mobile number won Rs {amount} in KBC Lucky Draw 2026. Contact Rana Pratap at +919999888877 to claim prize.", "Lottery / Prize Scam"),
    ("Congratulations! You won an iPhone 16 Pro Max in Diwali Mega Raffle. Claim free gift before midnight at http://{url}", "Lottery / Prize Scam"),
    ("Coca-Cola Promo: Your SIM card won $500,000 USD. Send bank details and passport copy to claims@promo-claim.xyz to release funds.", "Lottery / Prize Scam"),
    ("TATA Motors Lucky Draw: Your phone number won a brand new car! Deposit vehicle registration tax of Rs 4,999 to dispatch.", "Lottery / Prize Scam"),
    ("Selected among 10 lucky winners to receive cash reward of Rs {amount}. Click http://{url} to claim.", "Lottery / Prize Scam"),

    # Investment Scam
    ("Double your money in 7 days! Guaranteed 200% profit with zero risk in crypto arbitrage trading. Join VIP Telegram group: http://{url}", "Investment Scam"),
    ("SEBI certified stock tips: Earn 10% daily return guaranteed. Deposit minimum Rs 10,000 today to start receiving buy calls.", "Investment Scam"),
    ("AI Automated Forex Bot: Earn passive income of Rs 50,000 weekly without trading experience. Register at http://{url}", "Investment Scam"),
    ("Government backed solar energy investment: Invest Rs 5,000 and get Rs 800 daily payout directly in bank account.", "Investment Scam"),
    ("Crypto cloud mining: Mine Bitcoin on phone with zero hardware. Free 50 USDT bonus. Deposit 100 USDT to unlock withdrawal.", "Investment Scam"),

    # Courier / Delivery Scam
    ("India Post: Your package #IND88291 cannot be delivered due to invalid street address. Update address and pay Rs 25 redelivery at http://{url}", "Courier / Delivery Scam"),
    ("FedEx Express: Parcel containing prohibited items in your name is detained at Mumbai Customs. Contact customs clearance immediately to avoid arrest.", "Courier / Delivery Scam"),
    ("DHL Alert: Shipment on hold due to unpaid customs duty of Rs 140. Pay online at http://{url} within 12 hours to avoid return.", "Courier / Delivery Scam"),
    ("BlueDart delivery failed: Courier could not locate your premises. Reschedule delivery and verify contact details at http://{url}", "Courier / Delivery Scam"),
    ("Speed Post: Parcel address unreadable. Confirm pin code and pay delivery fee of Rs 49 at http://{url} to release shipment.", "Courier / Delivery Scam"),

    # Government Impersonation
    ("Income Tax Department: Tax evasion proceedings initiated against PAN. Pay outstanding penalty of Rs 15,000 at http://{url} or arrest warrant will be issued.", "Government Impersonation"),
    ("CBI Cyber Cell: Illegal offensive media was accessed from your IP. Contact investigating officer on Skype immediately to avoid digital arrest.", "Government Impersonation"),
    ("Electricity Department: Your power connection will be disconnected at 9:30 PM tonight due to unpaid bill. Call officer at +919765432100 immediately.", "Government Impersonation"),
    ("Traffic Police E-Challan: 3 unpaid speeding violations pending arrest warrant. Pay Rs 2,000 challan immediately at http://{url}", "Government Impersonation"),
    ("TRAI Notice: Your mobile number will be disconnected across all telecom operators within 2 hours due to illegal activity. Press 9 to verify.", "Government Impersonation"),

    # Tech-Support Scam
    ("CRITICAL ALERT: Windows Security detected Trojan spyware virus on your PC! System files damaged. Call Microsoft Technician toll-free at 1800-987-654.", "Tech-Support Scam"),
    ("Apple Support: Your Apple ID is locked due to suspicious logins. Download AnyDesk and share code with our technician to recover device.", "Tech-Support Scam"),
    ("Google Security: Critical vulnerability detected in Chrome browser. Install TeamViewer QuickSupport and call engineer to clean system.", "Tech-Support Scam"),
    ("McAfee Antivirus: Your protection expired today. 5 viruses found on computer. Call 1800-444-222 to renew and remove threats.", "Tech-Support Scam"),
    ("Android system warning: Severe virus infection detected! Download cleaning tool at http://{url} immediately.", "Tech-Support Scam"),

    # Account Takeover
    ("Instagram Security: Profile violated copyright rules and will be permanently deleted in 24 hours. Submit appeal at http://{url}", "Account Takeover"),
    ("WhatsApp security: Someone is trying to register WhatsApp with your phone. Send the 6-digit code you received to verify ownership.", "Account Takeover"),
    ("Facebook Alert: We received a password reset request from unknown device in Russia. If not you, cancel request at http://{url}", "Account Takeover"),
    ("Telegram warning: Account reported for spam. Confirm phone number and OTP at http://{url} to prevent account deletion.", "Account Takeover"),
    ("Twitter / X Support: Your verified badge will be removed unless you confirm credentials at http://{url} within 12 hours.", "Account Takeover"),

    # Credential Theft
    ("Dear Netflix user, monthly subscription payment failed. Update card number, CVV, and expiry at http://{url} to avoid cancellation.", "Credential Theft"),
    ("University Portal: Semester exam results published. Login with roll number and netbanking password at http://{url} to download marksheet.", "Credential Theft"),
    ("Spotify Premium: Billing error occurred. Re-enter debit card number and 3-digit CVV at http://{url} to keep listening.", "Credential Theft"),
    ("Paytm wallet alert: Provide your 4-digit passcode and SMS OTP to unlock suspended wallet balance.", "Credential Theft"),
    ("Email quota exceeded: 15 incoming emails are on hold. Re-authenticate with your email password at http://{url}", "Credential Theft")
]

BASE_LEGITIMATE = [
    # Legitimate Banking
    ("Rs {amount} debited from A/C XX4921 on 07-Oct-26 at Swiggy UPI. Available balance: Rs 24,310.50. - HDFC Bank", "Legitimate Banking"),
    ("Your OTP for transaction of Rs {amount} at Amazon Pay is 482910. Valid for 5 mins. Do not share OTP with anyone including bank staff.", "Legitimate Banking"),
    ("Dear customer, Rs {amount} credited to account XX1038 via NEFT by ABC INFOTECH PVT LTD. Available Bal: Rs 45,820.50.", "Legitimate Banking"),
    ("Your credit card statement for month ending September is ready. Total due: Rs {amount}. Due date: 20-Oct-2026. View in official mobile app.", "Legitimate Banking"),
    ("Axis Bank: Rs 500 debited from account ending 4091 for ATM cash withdrawal at Green Park Branch. Call 1800-419-5959 if not done by you.", "Legitimate Banking"),
    ("Rs 250.00 paid to Delhi Metro Card Recharge via PhonePe UPI. UTR: 428910284912. Bank Ref: 489210.", "Legitimate Banking"),
    ("Auto-debit for SIP mutual fund Rs 2,000 in Nippon India Small Cap has been successfully processed. - Zerodha", "Legitimate Banking"),
    ("ICICI Bank: Received quarterly interest credit of Rs 342 in Savings Account ending 8912.", "Legitimate Banking"),
    ("Kotak 811 account balance is Rs 8,920.00 as of today. Never share your MPIN or passwords with anyone.", "Legitimate Banking"),
    ("Electricity bill paid: Received Rs 1,420 towards Consumer No. 982341. Transaction ID: TXN89234891. Thank you, BSES Rajdhani.", "Legitimate Banking"),

    # Legitimate Job / Recruitment
    ("Hi Vanshika, thank you for applying to the Software Engineering Intern role at Microsoft. We invite you for a technical interview on Thursday.", "Legitimate Job"),
    ("Your application for the Data Analyst position at TCS has been shortlisted. Please check the campus placement portal for schedule details.", "Legitimate Job"),
    ("Thank you for completing the online coding assessment on HackerRank. Our recruitment team will review your submission and reach out within 5 days.", "Legitimate Job"),
    ("Dear candidate, please find attached the Google Meet link for your final round interview with our Engineering Director tomorrow at 3 PM.", "Legitimate Job"),
    ("Infosys campus recruitment: The aptitude test results are published on university placement dashboard. Login to view your status.", "Legitimate Job"),
    ("Your job alert for Python Developer roles in Bangalore: 12 new matching openings on LinkedIn. Click to view jobs on LinkedIn app.", "Legitimate Job"),
    ("Welcome to the new intern batch joining this Monday. Please check your official company email for onboarding credentials.", "Legitimate Job"),
    ("We received your application for Product Management Intern. We are reviewing candidates and will update you by end of week.", "Legitimate Job"),
    ("Invitation: Technical talk on AI Agents by senior research scientist from Google DeepMind in Auditorium 2 at 11 AM.", "Legitimate Job"),
    ("Campus Placement Cell: Pre-placement talk by Deloitte on Friday at 4 PM in seminar hall. Formal attire is required.", "Legitimate Job"),

    # Legitimate Delivery
    ("Your Amazon order containing 'Machine Learning with Python' has been dispatched and will arrive by 7 PM today. Track in Amazon app.", "Legitimate Delivery"),
    ("OTP for delivery of your Flipkart package is 7291. Share this OTP with the delivery agent only after inspecting your package.", "Legitimate Delivery"),
    ("Your Zomato food order from Biryani Blues is on the way! Delivery partner Rahul is arriving in approximately 12 minutes.", "Legitimate Delivery"),
    ("Swiggy Instamart: Order #SWG882910 has been delivered. Thank you for shopping with us. Rate your delivery experience in app.", "Legitimate Delivery"),
    ("Blinkit order placed successfully. Your grocery items will be delivered in 10 minutes at your doorstep.", "Legitimate Delivery"),
    ("Blue Dart AWB #8492019481 has been delivered to receptionist at office address. Signed by: Security.", "Legitimate Delivery"),
    ("Myntra: Your package is out for delivery with courier associate Ramesh. You can pay cash or scan UPI upon receipt.", "Legitimate Delivery"),
    ("Dominos Pizza: Your order is baking in the oven! Expected delivery time is 25 minutes.", "Legitimate Delivery"),
    ("Uber trip completed: Rs 185 paid via Uber Cash. Thank you for riding with driver Manoj. View invoice in app.", "Legitimate Delivery"),
    ("Delhivery parcel #DLH9920184 has arrived at your local hub and is scheduled for delivery tomorrow morning.", "Legitimate Delivery"),

    # Legitimate Personal / Work / College
    ("Reminder: Team standup meeting is scheduled today at 10:30 AM on Google Meet. Please update your Jira board tickets beforehand.", "Legitimate Personal/Work"),
    ("Dear students, tomorrow's Computer Networks lecture is rescheduled to 2:00 PM in Room 304. Please bring your lab manuals.", "Legitimate Personal/Work"),
    ("Hey, are you free this evening around 6 PM? Let's catch up at the library to work on the mini project presentation.", "Legitimate Personal/Work"),
    ("Your appointment with Dr. Sharma at Apollo Clinic is confirmed for tomorrow at 4:30 PM. Please arrive 10 minutes prior.", "Legitimate Personal/Work"),
    ("Hi, I have pushed the bug fixes to the GitHub repository branch. Can you please review the pull request when free?", "Legitimate Personal/Work"),
    ("BookmyShow: Booking confirmed for Interstellar at PVR Select Citywalk, Screen 4, Audi 2 on Saturday 7:15 PM.", "Legitimate Personal/Work"),
    ("Dear user, your broadband subscription has been renewed for 30 days. High speed limit: 300 Mbps unlimited data. - Airtel Xstream", "Legitimate Personal/Work"),
    ("IRCTC: PNR 2849102849, Train 12952 Mumbai Rajdhani. Sleeper B3-45 confirmed. Charting done. Safe journey.", "Legitimate Personal/Work"),
    ("Mum called: Can you pick up milk and bread on your way back from college? Call me when you leave.", "Legitimate Personal/Work"),
    ("Library reminder: The book 'Introduction to Algorithms' is due for return on 12-Oct-2026. Renew online on student portal.", "Legitimate Personal/Work"),
    ("Hey Vanshika, I shared the lecture notes on Google Drive. Let me know if you can access the folder.", "Legitimate Personal/Work"),
    ("Project deadline update: Faculty confirmed that final mini project submission is due next Wednesday at 5 PM.", "Legitimate Personal/Work"),
    ("Dinner reservation confirmed for 4 guests at Olive Bistro tonight at 8:00 PM. We look forward to serving you.", "Legitimate Personal/Work"),
    ("Password reset successful for your GitHub account. If you initiated this change, no further action is required.", "Legitimate Personal/Work"),
    ("Flight SG-812 Delhi to Mumbai is on time. Web check-in opens 48 hours prior to departure. - SpiceJet", "Legitimate Personal/Work")
]

def generate_full_dataset():
    random.seed(42)
    rows = []

    # 1. Generate scam samples with realistic variations
    for template, category in BASE_SCAMS:
        # Create 3-4 diverse variations per template
        for _ in range(4):
            bank = random.choice(BANKS)
            url = random.choice(SHORTENERS)
            amount = random.choice(AMOUNTS)
            text = template.format(bank=bank, url=url, amount=amount)
            rows.append({"text": text, "is_scam": 1, "category": category})

    # 2. Generate legitimate samples with realistic variations
    for template, category in BASE_LEGITIMATE:
        for _ in range(3):
            amount = random.choice(AMOUNTS)
            text = template.format(amount=amount)
            rows.append({"text": text, "is_scam": 0, "category": category})

    # Shuffle dataset
    random.shuffle(rows)
    return rows

def save_dataset(output_path: str = None) -> str:
    if output_path is None:
        base_dir = Path(__file__).resolve().parent.parent.parent
        output_path = base_dir / "data" / "scam_dataset.csv"
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset = generate_full_dataset()

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "is_scam", "category"])
        writer.writeheader()
        for r in dataset:
            writer.writerow(r)

    scam_count = sum(1 for r in dataset if r["is_scam"] == 1)
    legit_count = sum(1 for r in dataset if r["is_scam"] == 0)
    print(f"Dataset successfully created with {len(dataset)} samples ({scam_count} Scams, {legit_count} Legitimate) at {output_path}")
    return str(output_path)

if __name__ == "__main__":
    save_dataset()
