# Sample Data and Demonstration Reports

This document provides sample data and reports for demonstrating the SEBI Sentinel AI platform.

## Sample Email Scans

### Phishing Email Example

**Email Subject:** URGENT: Your SEBI Account Will Be Suspended

**Sender:** support@sebi-verify.com (spoofed)

**Body:**
```
Dear Investor,

We have detected suspicious activity on your SEBI account. Your account will be suspended within 24 hours unless you verify your identity immediately.

Click here to verify: http://sebi-verify-account.com/login

This is an automated message. Do not reply.

SEBI Security Team
```

**Scan Result:**
- **Trust Score:** 15/100
- **Risk Level:** Critical
- **Confidence:** 0.92
- **Reasons:**
  - Suspicious sender domain (typosquatting detected)
  - Urgency keywords in subject line
  - Non-HTTPS link
  - Domain age < 24 hours
  - No valid SPF/DKIM records
- **Recommendations:**
  - Delete this email immediately
  - Do not click on any links
  - Report to actual SEBI authorities
  - Check your official SEBI account directly

### Legitimate Email Example

**Email Subject:** Quarterly Portfolio Statement - Q4 2023

**Sender:** notifications@nseindia.com

**Body:**
```
Dear Investor,

Your quarterly portfolio statement for Q4 2023 is now available for download.

Please log in to your NSE account to view your statement.

Best regards,
NSE Investor Services
```

**Scan Result:**
- **Trust Score:** 95/100
- **Risk Level:** Low
- **Confidence:** 0.88
- **Reasons:**
  - Verified sender domain
  - Valid SPF/DKIM records
  - No urgency indicators
  - Professional tone
  - Links to official domain
- **Recommendations:**
  - Email appears legitimate
  - Verify by logging into official NSE account
  - No immediate action required

## Sample URL Scans

### Malicious URL Example

**URL:** http://sebi-official-login.xyz

**Scan Result:**
- **Trust Score:** 10/100
- **Risk Level:** Critical
- **Confidence:** 0.95
- **Reasons:**
  - Typosquatting detected (sebi-official-login.xyz vs sebi.gov.in)
  - No SSL certificate
  - Domain registered recently
  - Suspicious TLD (.xyz)
  - Blacklisted by multiple security vendors
- **Recommendations:**
  - Do not visit this URL
  - Report to cybersecurity authorities
  - Block in browser/firewall

### Legitimate URL Example

**URL:** https://www.sebi.gov.in

**Scan Result:**
- **Trust Score:** 100/100
- **Risk Level:** Low
- **Confidence:** 0.99
- **Reasons:**
  - Official government domain
  - Valid SSL certificate
  - Domain age > 10 years
  - WHOIS matches official records
  - Not blacklisted
- **Recommendations:**
  - Safe to visit
  - Official SEBI website

## Sample PDF Scans

### Fake Document Example

**File:** investment_opportunity.pdf

**Content:** Promises 50% monthly returns on SEBI-approved investments

**Scan Result:**
- **Trust Score:** 20/100
- **Risk Level:** High
- **Confidence:** 0.85
- **Reasons:**
  - Fake SEBI logo detected
  - Unrealistic return promises
  - No official registration number
  - Inconsistent formatting
  - Suspicious contact information
- **Recommendations:**
  - Do not trust this document
  - Verify with official SEBI database
  - Report to SEBI fraud department

### Legitimate Document Example

**File:** mutual_fund_fact_sheet.pdf

**Content:** Standard mutual fund fact sheet from registered AMC

**Scan Result:**
- **Trust Score:** 92/100
- **Risk Level:** Low
- **Confidence:** 0.90
- **Reasons:**
  - Valid AMC logo
  - Contains valid SEBI registration number
  - Standard regulatory disclosures
  - Consistent with official templates
  - Verified issuer
- **Recommendations:**
  - Document appears legitimate
  - Cross-check with AMFI database
  - Safe to review

## Sample Image Scans

### Deepfake Image Example

**File:** broker_photo.jpg

**Content:** Image of a registered broker with manipulated face

**Scan Result:**
- **Trust Score:** 25/100
- **Risk Level:** High
- **Confidence:** 0.78
- **Reasons:**
  - Inconsistent lighting patterns
  - Blur artifacts around face
  - Unnatural skin texture
  - Metadata anomalies
  - Face analysis shows manipulation
- **Recommendations:**
  - Image likely manipulated
  - Verify broker identity through official channels
  - Do not trust this image for verification

### Legitimate Image Example

**File:** company_logo.png

**Content:** Official company logo from listed company

**Scan Result:**
- **Trust Score:** 98/100
- **Risk Level:** Low
- **Confidence:** 0.95
- **Reasons:**
  - Consistent with official logo
  - No manipulation artifacts
  - Valid metadata
  - Matches official sources
- **Recommendations:**
  - Image appears authentic
  - Safe to use

## Sample Video Scans

### Deepfake Video Example

**File:** ceo_announcement.mp4

**Content:** Video of CEO making fraudulent investment claims

**Scan Result:**
- **Trust Score:** 18/100
- **Risk Level:** Critical
- **Confidence:** 0.82
- **Reasons:**
  - Lip sync inconsistencies
  - Blink pattern anomalies
  - Temporal artifacts between frames
  - Audio-visual mismatch
  - Compression inconsistencies
- **Recommendations:**
  - Video likely deepfake
  - Verify with official company channels
  - Do not act on claims in video

## Sample Audio Scans

### Voice Clone Example

**File:** broker_message.mp3

**Content:** Audio message from broker with cloned voice

**Scan Result:**
- **Trust Score:** 22/100
- **Risk Level:** High
- **Confidence:** 0.80
- **Reasons:**
  - Spectral anomalies detected
  - Unnatural pitch patterns
  - Inconsistent timbre
  - Background noise patterns
  - Synthetic voice indicators
- **Recommendations:**
  - Audio likely synthesized
  - Verify with broker directly
  - Do not act on instructions

## Sample Social Media Scans

### Scam Post Example

**Platform:** Twitter/X

**Content:** "Guaranteed 100x returns on this SEBI-approved stock! Buy now before it's too late! #StockTips #SEBI"

**Scan Result:**
- **Trust Score:** 12/100
- **Risk Level:** Critical
- **Confidence:** 0.90
- **Reasons:**
  - Pump-and-dump language
  - Unrealistic return promises
  - Urgency indicators
  - Fake SEBI endorsement
  - Suspicious hashtags
  - New account with no history
- **Recommendations:**
  - Ignore this post
  - Report to platform
  - Do not engage or share

### Legitimate Post Example

**Platform:** Twitter/X

**Content:** Official SEBI announcement about new regulations

**Scan Result:**
- **Trust Score:** 98/100
- **Risk Level:** Low
- **Confidence:** 0.97
- **Reasons:**
  - Verified official account
  - Professional language
  - Links to official sources
  - Consistent with SEBI communications
- **Recommendations:**
  - Legitimate official announcement
  - Safe to read and share

## Sample Trust Engine Output

### Comprehensive Scan Result

```json
{
  "scan_id": "scan_20240115_12345",
  "scan_type": "email",
  "timestamp": "2024-01-15T10:30:00Z",
  "trust_score": 35.0,
  "risk_level": "high",
  "confidence": 0.85,
  "checks_performed": {
    "sender_analysis": {
      "domain_reputation": 0.2,
      "spf_valid": false,
      "dkim_valid": false,
      "dmarc_valid": false
    },
    "content_analysis": {
      "urgency_score": 0.8,
      "grammar_score": 0.6,
      "suspicious_links": 2,
      "attachment_risk": 0.7
    },
    "header_analysis": {
      "reply_to_mismatch": true,
      "suspicious_headers": 3
    }
  },
  "reasons": [
    "Suspicious sender domain detected",
    "Urgency keywords found in subject line",
    "Non-HTTPS link detected",
    "SPF/DKIM/DMARC records missing or invalid"
  ],
  "evidence": [
    {
      "type": "domain",
      "description": "Sender domain sebi-verify.com is a typosquatting attempt",
      "confidence": 0.95
    },
    {
      "type": "link",
      "description": "Link points to non-HTTPS domain",
      "confidence": 0.90
    }
  ],
  "recommendations": [
    "Do not click on any links in this email",
    "Verify the sender through official SEBI channels",
    "Report this email to your IT security team",
    "Delete the email immediately"
  ],
  "explainable_ai": {
    "highlighted_regions": [
      {
        "type": "sender",
        "text": "support@sebi-verify.com",
        "reason": "Typosquatting detected"
      },
      {
        "type": "subject",
        "text": "URGENT",
        "reason": "Urgency indicator"
      },
      {
        "type": "link",
        "text": "http://sebi-verify-account.com",
        "reason": "Suspicious URL"
      }
    ],
    "feature_importance": {
      "domain_reputation": 0.35,
      "urgency_score": 0.25,
      "link_analysis": 0.20,
      "header_analysis": 0.15,
      "content_analysis": 0.05
    }
  }
}
```

## Sample Dashboard Statistics

### Monthly Threat Overview

```
Total Scans: 1,247
Threats Detected: 234 (18.8%)
Threats Blocked: 189 (80.8% of detected)

Risk Distribution:
- Critical: 45 (19.2%)
- High: 89 (38.0%)
- Medium: 67 (28.6%)
- Low: 33 (14.1%)

Category Breakdown:
- Email Phishing: 89 (38.0%)
- URL Scams: 56 (23.9%)
- Fake Documents: 34 (14.5%)
- Deepfake Images: 23 (9.8%)
- Voice Clones: 18 (7.7%)
- Social Media Scams: 14 (6.0%)
```

### Threat Trend (Last 6 Months)

```
Month    | Scans | Threats | Detection Rate
---------|-------|---------|---------------
Aug 2023 | 980   | 178     | 18.2%
Sep 2023 | 1050  | 195     | 18.6%
Oct 2023 | 1120  | 210     | 18.8%
Nov 2023 | 1180  | 225     | 19.1%
Dec 2023 | 1210  | 230     | 19.0%
Jan 2024 | 1247  | 234     | 18.8%
```

## Sample Report Generation

### Monthly Summary Report

**Report ID:** RPT-2024-01
**Period:** January 2024
**Generated:** 2024-02-01

**Executive Summary:**
- 1,247 total scans performed
- 234 threats detected (18.8% detection rate)
- 189 threats blocked (80.8% block rate)
- Average trust score: 72.5
- Most common threat type: Email phishing (38.0%)

**Key Findings:**
1. Increase in typosquatting attacks targeting SEBI-related domains
2. Rise in voice clone scams using broker identities
3. Improved detection of deepfake images (95% accuracy)
4. Social media scams remain persistent

**Recommendations:**
1. Increase user awareness about typosquatting
2. Implement voice verification for broker communications
3. Continue improving deepfake detection models
4. Monitor social media platforms for scam patterns

## Installation of Sample Data

To load sample data for demonstration:

```bash
# Backend
cd backend
python scripts/load_sample_data.py

# Frontend (if needed)
cd frontend
npm run load-sample-data
```

## Using Sample Data for Demo

1. **Login with demo account:**
   - Email: demo@sebisentinel.com
   - Password: demo123

2. **View pre-loaded scans:**
   - Navigate to Scan History
   - Filter by risk level
   - View detailed results

3. **Test new scans:**
   - Upload sample files from `/sample_data` directory
   - Scan sample URLs
   - Review results

## Notes

- All sample data is fictional and for demonstration purposes only
- No real user data or sensitive information is included
- Sample results are based on simulated AI model outputs
- Use sample data responsibly and only for authorized demonstrations
