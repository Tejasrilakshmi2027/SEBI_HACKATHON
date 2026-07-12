"""
Email Phishing Detection Inference Script
Uses trained BERT model for phishing detection with Explainable AI
Supports .eml files, enhanced parsing, sender spoofing detection, credential harvesting detection
"""

import os
import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F
from collections import defaultdict
import re
import email
from email import policy
from email.parser import BytesParser
from email.header import decode_header
from urllib.parse import urlparse
import dns.resolver
import tldextract


class EmailPhishingDetector:
    """Email Phishing Detection with Explainable AI"""
    
    def __init__(self, model_path="./ai_models/email_phishing/saved_model"):
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        self.load_model()
        self.trusted_domains = self._load_trusted_domains()
        self.credential_keywords = self._load_credential_keywords()
        
    def load_model(self):
        """Load trained model and tokenizer"""
        print(f"Loading model from {self.model_path}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Using base BERT model as fallback...")
            self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
            self.model = AutoModelForSequenceClassification.from_pretrained(
                "bert-base-uncased", 
                num_labels=2
            )
            self.model.to(self.device)
            self.model.eval()
    
    def _load_trusted_domains(self):
        """Load trusted domains for spoofing detection"""
        return [
            'sebi.gov.in', 'nseindia.com', 'bseindia.com', 'rbi.org.in',
            'amfiindia.com', 'nsdl.co.in', 'cdslindia.com', 'mcxindia.com',
            'icicibank.com', 'hdfcbank.com', 'sbi.co.in', 'axisbank.com',
            'kotak.com', 'hdfcbank.com', 'bankofbaroda.com', 'pnb.co.in'
        ]
    
    def _load_credential_keywords(self):
        """Load credential harvesting keywords"""
        return [
            'password', 'username', 'login', 'signin', 'sign in', 'log in',
            'credential', 'authenticate', 'verify', 'confirm', 'update',
            'reset', 'change', 'enter', 'provide', 'submit', 'account'
        ]
    
    def parse_eml_file(self, eml_path):
        """Parse .eml file and extract email components"""
        try:
            with open(eml_path, 'rb') as f:
                msg = BytesParser(policy=policy.default).parse(f)
            
            parsed = {
                'subject': self._decode_header(msg.get('Subject', '')),
                'from': self._decode_header(msg.get('From', '')),
                'to': self._decode_header(msg.get('To', '')),
                'cc': self._decode_header(msg.get('Cc', '')),
                'reply_to': self._decode_header(msg.get('Reply-To', '')),
                'sender': self._decode_header(msg.get('Sender', '')),
                'return_path': self._decode_header(msg.get('Return-Path', '')),
                'date': msg.get('Date', ''),
                'message_id': msg.get('Message-ID', ''),
                'body': '',
                'headers': dict(msg.items()),
                'links': []
            }
            
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        try:
                            payload = part.get_payload(decode=True)
                            parsed['body'] = payload.decode('utf-8', errors='ignore')
                        except:
                            parsed['body'] = str(part.get_payload())
            else:
                try:
                    payload = msg.get_payload(decode=True)
                    parsed['body'] = payload.decode('utf-8', errors='ignore')
                except:
                    parsed['body'] = str(msg.get_payload())
            
            parsed['links'] = self._extract_links(parsed['body'])
            
            return parsed
        except Exception as e:
            return {'error': str(e)}
    
    def _decode_header(self, header_value):
        """Decode email header"""
        if not header_value:
            return ''
        try:
            decoded_parts = decode_header(header_value)
            decoded = ''
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    decoded += part
            return decoded
        except:
            return str(header_value)
    
    def _extract_links(self, text):
        """Extract all links from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    def detect_sender_spoofing(self, parsed_email):
        """Detect sender spoofing"""
        spoofing_indicators = {
            'is_spoofed': False,
            'confidence': 0.0,
            'indicators': []
        }
        
        from_addr = parsed_email.get('from', '')
        reply_to = parsed_email.get('reply_to', '')
        sender = parsed_email.get('sender', '')
        return_path = parsed_email.get('return_path', '')
        
        from_domain = self._extract_domain(from_addr)
        reply_to_domain = self._extract_domain(reply_to)
        sender_domain = self._extract_domain(sender)
        return_path_domain = self._extract_domain(return_path)
        
        if from_domain and reply_to_domain and from_domain != reply_to_domain:
            spoofing_indicators['indicators'].append({
                'type': 'reply_to_mismatch',
                'message': f'Reply-To domain ({reply_to_domain}) differs from From domain ({from_domain})',
                'severity': 'high'
            })
            spoofing_indicators['confidence'] += 0.3
        
        if from_domain and sender_domain and from_domain != sender_domain:
            spoofing_indicators['indicators'].append({
                'type': 'sender_mismatch',
                'message': f'Sender domain ({sender_domain}) differs from From domain ({from_domain})',
                'severity': 'high'
            })
            spoofing_indicators['confidence'] += 0.3
        
        if from_domain and return_path_domain and from_domain != return_path_domain:
            spoofing_indicators['indicators'].append({
                'type': 'return_path_mismatch',
                'message': f'Return-Path domain ({return_path_domain}) differs from From domain ({from_domain})',
                'severity': 'medium'
            })
            spoofing_indicators['confidence'] += 0.2
        
        if from_domain:
            extracted = tldextract.extract(from_domain)
            if extracted.subdomain and extracted.domain:
                suspicious_subdomains = ['verify', 'secure', 'account', 'login', 'support', 'service', 'notification']
                if extracted.subdomain.lower() in suspicious_subdomains:
                    spoofing_indicators['indicators'].append({
                        'type': 'suspicious_subdomain',
                        'message': f'Suspicious subdomain: {extracted.subdomain}',
                        'severity': 'medium'
                    })
                    spoofing_indicators['confidence'] += 0.2
        
        spoofing_indicators['confidence'] = min(spoofing_indicators['confidence'], 1.0)
        spoofing_indicators['is_spoofed'] = spoofing_indicators['confidence'] > 0.5
        
        return spoofing_indicators
    
    def _extract_domain(self, email_addr):
        """Extract domain from email address"""
        if not email_addr:
            return ''
        match = re.search(r'@([^>\s]+)', email_addr)
        if match:
            return match.group(1).strip('<>')
        return ''
    
    def detect_credential_harvesting(self, parsed_email):
        """Detect credential harvesting attempts"""
        harvesting_indicators = {
            'is_harvesting': False,
            'confidence': 0.0,
            'indicators': []
        }
        
        subject = parsed_email.get('subject', '').lower()
        body = parsed_email.get('body', '').lower()
        combined = subject + ' ' + body
        
        credential_count = 0
        for keyword in self.credential_keywords:
            count = combined.count(keyword)
            if count > 0:
                credential_count += count
                harvesting_indicators['indicators'].append({
                    'type': 'credential_keyword',
                    'keyword': keyword,
                    'count': count,
                    'severity': 'high' if count > 1 else 'medium'
                })
                harvesting_indicators['confidence'] += min(count * 0.1, 0.3)
        
        url_indicators = 0
        for link in parsed_email.get('links', []):
            parsed = urlparse(link)
            path_lower = parsed.path.lower()
            if any(kw in path_lower for kw in ['login', 'signin', 'account', 'verify', 'reset', 'password']):
                url_indicators += 1
                harvesting_indicators['indicators'].append({
                    'type': 'suspicious_url_path',
                    'url': link,
                    'message': 'URL contains credential-related path',
                    'severity': 'high'
                })
                harvesting_indicators['confidence'] += 0.2
        
        harvesting_indicators['confidence'] = min(harvesting_indicators['confidence'], 1.0)
        harvesting_indicators['is_harvesting'] = harvesting_indicators['confidence'] > 0.4
        
        return harvesting_indicators
    
    def detect_ai_generated_patterns(self, parsed_email):
        """Detect AI-generated phishing patterns"""
        ai_indicators = {
            'is_ai_generated': False,
            'confidence': 0.0,
            'indicators': []
        }
        
        subject = parsed_email.get('subject', '')
        body = parsed_email.get('body', '')
        
        if not body:
            return ai_indicators
        
        sentences = re.split(r'[.!?]+', body)
        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()]) if sentences else 0
        
        if avg_sentence_length > 25:
            ai_indicators['indicators'].append({
                'type': 'unnatural_sentence_length',
                'message': f'Unusually long average sentence length: {avg_sentence_length:.1f}',
                'severity': 'medium'
            })
            ai_indicators['confidence'] += 0.2
        
        vocabulary_diversity = len(set(body.lower().split())) / len(body.split()) if body.split() else 0
        if vocabulary_diversity > 0.8:
            ai_indicators['indicators'].append({
                'type': 'high_vocabulary_diversity',
                'message': f'Unusually high vocabulary diversity: {vocabulary_diversity:.2f}',
                'severity': 'low'
            })
            ai_indicators['confidence'] += 0.1
        
        perfect_grammar = len(re.findall(r'[A-Z][a-z]+ [a-z]+ [a-z]+', body))
        total_words = len(body.split())
        if total_words > 0 and perfect_grammar / total_words > 0.3:
            ai_indicators['indicators'].append({
                'type': 'perfect_grammar',
                'message': 'Unusually perfect grammar patterns detected',
                'severity': 'low'
            })
            ai_indicators['confidence'] += 0.15
        
        repetitive_patterns = len(re.findall(r'(\b\w+\b)\1', body))
        if repetitive_patterns > 5:
            ai_indicators['indicators'].append({
                'type': 'repetitive_patterns',
                'message': f'High number of repetitive patterns: {repetitive_patterns}',
                'severity': 'medium'
            })
            ai_indicators['confidence'] += 0.2
        
        ai_indicators['confidence'] = min(ai_indicators['confidence'], 1.0)
        ai_indicators['is_ai_generated'] = ai_indicators['confidence'] > 0.4
        
        return ai_indicators
    
    def preprocess_email(self, email_content, is_eml=False):
        """Preprocess email content"""
        if is_eml:
            parsed = self.parse_eml_file(email_content)
            if 'error' in parsed:
                return f"ERROR: {parsed['error']}"
            
            subject = parsed.get('subject', '')
            body = parsed.get('body', '')
            sender = parsed.get('from', '')
            
            combined = f"SUBJECT: {subject} SENDER: {sender} BODY: {body}"
            return combined[:512]
        else:
            lines = email_content.split("\n")
            subject = ""
            body = ""
            sender = ""
            
            for line in lines:
                if line.lower().startswith("subject:"):
                    subject = line[8:].strip()
                elif line.lower().startswith("from:") or line.lower().startswith("sender:"):
                    sender = line.split(":")[1].strip()
                elif line.lower().startswith("body:"):
                    body = line[5:].strip()
            
            combined = f"SUBJECT: {subject} SENDER: {sender} BODY: {body}"
            return combined[:512]
    
    def extract_linguistic_features(self, text):
        """Extract linguistic features for explainability"""
        features = {
            "urgency_keywords": len(re.findall(r"\b(urgent|immediate|action required|verify now|expire|deadline|alert|warning)\b", text.lower())),
            "suspicious_urls": len(re.findall(r"http[s]?://[^\s]+\.xyz|http[s]?://[^\s]+\.(tk|ml|ga|cf|top|pw|gq)\b", text.lower())),
            "money_mentions": len(re.findall(r"\$\d+|\d+\s*(dollars|usd|rupees|inr|rs|₹)\b", text.lower())),
            "account_keywords": len(re.findall(r"\b(account|password|login|sign in|verify|authenticate|credential)\b", text.lower())),
            "all_caps": sum(1 for word in text.split() if word.isupper() and len(word) > 2),
            "exclamation_count": text.count("!"),
            "question_count": text.count("?"),
            "suspicious_words": len(re.findall(r"\b(free|winner|congratulations|prize|lottery|guaranteed|limited time|exclusive)\b", text.lower())),
            "sebi_mentions": len(re.findall(r"\b(sebi|nse|bse|rbi|regulatory)\b", text.lower())),
            "length": len(text),
            "typosquatting_attempts": len(re.findall(r"\b(s3bi|s3bi|sebl|ns3|bs3|rbi\.gov\.in\.com|nseindia\.co)\b", text.lower()))
        }
        return features
    
    def predict(self, email_content, return_explanations=True, is_eml=False):
        """Predict if email is phishing"""
        parsed_email = None
        if is_eml:
            parsed_email = self.parse_eml_file(email_content)
        
        # Preprocess
        processed_text = self.preprocess_email(email_content, is_eml=is_eml)
        
        # Tokenize
        inputs = self.tokenizer(
            processed_text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = F.softmax(logits, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item()
        
        # Extract features
        linguistic_features = self.extract_linguistic_features(processed_text)
        
        # Additional detections
        spoofing_detection = None
        credential_detection = None
        ai_detection = None
        
        if parsed_email and 'error' not in parsed_email:
            spoofing_detection = self.detect_sender_spoofing(parsed_email)
            credential_detection = self.detect_credential_harvesting(parsed_email)
            ai_detection = self.detect_ai_generated_patterns(parsed_email)
        
        # Determine risk level
        if predicted_class == 1:  # Phishing
            if confidence > 0.8:
                risk_level = "critical"
            elif confidence > 0.6:
                risk_level = "high"
            else:
                risk_level = "medium"
        else:  # Legitimate
            if confidence > 0.8:
                risk_level = "low"
            else:
                risk_level = "low"
        
        # Calculate trust score (0-100)
        if predicted_class == 1:
            trust_score = int((1 - confidence) * 100)
        else:
            trust_score = int(confidence * 100)
        
        result = {
            "is_phishing": bool(predicted_class),
            "confidence": round(confidence, 4),
            "risk_level": risk_level,
            "trust_score": trust_score,
            "probabilities": {
                "legitimate": round(probabilities[0][0].item(), 4),
                "phishing": round(probabilities[0][1].item(), 4)
            }
        }
        
        if return_explanations:
            result["explanations"] = self.generate_explanations(
                processed_text, 
                linguistic_features, 
                predicted_class, 
                confidence,
                spoofing_detection,
                credential_detection,
                ai_detection
            )
            result["linguistic_features"] = linguistic_features
            result["highlighted_regions"] = self.get_highlighted_regions(
                processed_text, 
                linguistic_features
            )
            result["parsed_email"] = parsed_email
            result["spoofing_detection"] = spoofing_detection
            result["credential_detection"] = credential_detection
            result["ai_detection"] = ai_detection
        
        return result
    
    def generate_explanations(self, text, features, predicted_class, confidence, spoofing_detection=None, credential_detection=None, ai_detection=None):
        """Generate human-readable explanations"""
        explanations = []
        
        if spoofing_detection and spoofing_detection['is_spoofed']:
            for indicator in spoofing_detection['indicators']:
                explanations.append({
                    "type": indicator['type'],
                    "message": indicator['message'],
                    "severity": indicator['severity']
                })
        
        if credential_detection and credential_detection['is_harvesting']:
            for indicator in credential_detection['indicators']:
                explanations.append({
                    "type": indicator['type'],
                    "message": indicator.get('message', f"Credential keyword detected: {indicator['keyword']}"),
                    "severity": indicator['severity']
                })
        
        if ai_detection and ai_detection['is_ai_generated']:
            for indicator in ai_detection['indicators']:
                explanations.append({
                    "type": indicator['type'],
                    "message": indicator['message'],
                    "severity": indicator['severity']
                })
        
        if predicted_class == 1:  # Phishing
            if features["urgency_keywords"] > 0:
                explanations.append({
                    "type": "urgency",
                    "message": f"Detected {features['urgency_keywords']} urgency keyword(s) which are common in phishing emails",
                    "severity": "high"
                })
            
            if features["suspicious_urls"] > 0:
                explanations.append({
                    "type": "suspicious_url",
                    "message": f"Found {features['suspicious_urls']} suspicious URL(s) with known malicious TLDs",
                    "severity": "critical"
                })
            
            if features["money_mentions"] > 0:
                explanations.append({
                    "type": "money",
                    "message": f"Money-related content detected ({features['money_mentions']} mentions), common in financial scams",
                    "severity": "high"
                })
            
            if features["account_keywords"] > 2:
                explanations.append({
                    "type": "account",
                    "message": f"Multiple account-related keywords ({features['account_keywords']}) requesting action",
                    "severity": "medium"
                })
            
            if features["all_caps"] > 2:
                explanations.append({
                    "type": "formatting",
                    "message": f"Excessive use of ALL CAPS ({features['all_caps']} words), common in phishing",
                    "severity": "medium"
                })
            
            if features["exclamation_count"] > 3:
                explanations.append({
                    "type": "punctuation",
                    "message": f"Excessive exclamation marks ({features['exclamation_count']}) indicating urgency",
                    "severity": "medium"
                })
            
            if features["suspicious_words"] > 0:
                explanations.append({
                    "type": "suspicious_words",
                    "message": f"Suspicious words detected: {features['suspicious_words']} (e.g., free, winner, prize)",
                    "severity": "high"
                })
            
            if confidence > 0.8:
                explanations.append({
                    "type": "model_confidence",
                    "message": f"High model confidence ({confidence:.1%}) indicating strong phishing indicators",
                    "severity": "high"
                })
        else:  # Legitimate
            if features["sebi_mentions"] > 0:
                explanations.append({
                    "type": "official",
                    "message": "Contains legitimate regulatory references (SEBI, NSE, BSE)",
                    "severity": "positive"
                })
            
            if features["urgency_keywords"] == 0 and features["suspicious_urls"] == 0:
                explanations.append({
                    "type": "clean",
                    "message": "No urgency keywords or suspicious URLs detected",
                    "severity": "positive"
                })
            
            if confidence > 0.8:
                explanations.append({
                    "type": "model_confidence",
                    "message": f"High model confidence ({confidence:.1%}) indicating legitimate content",
                    "severity": "positive"
                })
        
        return explanations
    
    def get_highlighted_regions(self, text, features):
        """Get regions of text to highlight for explainability"""
        highlighted = []
        
        # Highlight urgency keywords
        urgency_pattern = r"\b(urgent|immediate|action required|verify now|expire|deadline|alert|warning)\b"
        for match in re.finditer(urgency_pattern, text, re.IGNORECASE):
            highlighted.append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "reason": "Urgency keyword",
                "severity": "high"
            })
        
        # Highlight suspicious URLs
        url_pattern = r"http[s]?://[^\s]+\.xyz|http[s]?://[^\s]+\.(tk|ml|ga|cf|top|pw)"
        for match in re.finditer(url_pattern, text, re.IGNORECASE):
            highlighted.append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "reason": "Suspicious URL",
                "severity": "critical"
            })
        
        # Highlight money mentions
        money_pattern = r"\$\d+|\d+\s*(dollars|usd|rupees|inr|rs|₹)"
        for match in re.finditer(money_pattern, text, re.IGNORECASE):
            highlighted.append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "reason": "Money mention",
                "severity": "high"
            })
        
        # Highlight suspicious words
        suspicious_pattern = r"\b(free|winner|congratulations|prize|lottery|guaranteed|limited time|exclusive)\b"
        for match in re.finditer(suspicious_pattern, text, re.IGNORECASE):
            highlighted.append({
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "reason": "Suspicious word",
                "severity": "high"
            })
        
        return highlighted
    
    def get_feature_importance(self, text, features):
        """Calculate feature importance for explainability"""
        importance = {}
        
        # Normalize features
        max_urgency = max(features["urgency_keywords"], 1)
        max_urls = max(features["suspicious_urls"], 1)
        max_money = max(features["money_mentions"], 1)
        max_account = max(features["account_keywords"], 1)
        
        importance["urgency_score"] = features["urgency_keywords"] / max_urgency
        importance["url_risk"] = features["suspicious_urls"] / max_urls
        importance["financial_risk"] = features["money_mentions"] / max_money
        importance["account_risk"] = features["account_keywords"] / max_account
        importance["formatting_risk"] = min(features["all_caps"] / 5, 1.0)
        importance["punctuation_risk"] = min(features["exclamation_count"] / 5, 1.0)
        
        # Calculate overall risk score
        weights = {
            "urgency_score": 0.25,
            "url_risk": 0.30,
            "financial_risk": 0.20,
            "account_risk": 0.15,
            "formatting_risk": 0.05,
            "punctuation_risk": 0.05
        }
        
        overall_risk = sum(importance[k] * weights[k] for k in importance)
        importance["overall_risk"] = overall_risk
        
        return importance
    
    def batch_predict(self, emails):
        """Predict multiple emails at once"""
        results = []
        for email in emails:
            result = self.predict(email)
            results.append(result)
        return results
    
    def get_recommendations(self, prediction_result):
        """Get actionable recommendations based on prediction"""
        recommendations = []
        
        if prediction_result["is_phishing"]:
            if prediction_result["risk_level"] == "critical":
                recommendations.append("Delete this email immediately")
                recommendations.append("Do not click on any links or attachments")
                recommendations.append("Report to your IT security team")
                recommendations.append("Block the sender")
            elif prediction_result["risk_level"] == "high":
                recommendations.append("Do not click on any links")
                recommendations.append("Verify sender through official channels")
                recommendations.append("Report as phishing")
            else:
                recommendations.append("Exercise caution with this email")
                recommendations.append("Verify the sender's identity")
                recommendations.append("Do not provide sensitive information")
        else:
            recommendations.append("Email appears legitimate")
            recommendations.append("Still verify sender if unsure")
            recommendations.append("Check for any unusual requests")
        
        return recommendations


def main():
    """Test the inference script"""
    print("=" * 60)
    print("Email Phishing Detection Inference")
    print("=" * 60)
    
    # Initialize detector
    detector = EmailPhishingDetector()
    
    # Test emails
    test_emails = [
        "Subject: URGENT Your account will be suspended Body: Dear customer your account will be suspended within 24 hours unless you verify your identity immediately Click here http://verify-account-xyz.com",
        "Subject: Quarterly portfolio statement Body: Your quarterly portfolio statement for Q4 2023 is now available Please log in to your account to view",
        "Subject: You won 50000 dollars Body: Congratulations you have won 50000 dollars Click to claim http://lottery-winner.xyz",
        "Subject: Investment update Body: Here is your monthly investment update from our team Market performance has been steady",
    ]
    
    print("\nRunning predictions...")
    for i, email in enumerate(test_emails, 1):
        print(f"\n{'='*60}")
        print(f"Email {i}")
        print(f"{'='*60}")
        print(f"Content: {email[:100]}...")
        
        result = detector.predict(email)
        
        print(f"\nPrediction: {'PHISHING' if result['is_phishing'] else 'LEGITIMATE'}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Risk Level: {result['risk_level'].upper()}")
        print(f"Trust Score: {result['trust_score']}/100")
        
        print(f"\nExplanations:")
        for exp in result["explanations"]:
            print(f"  - [{exp['severity'].upper()}] {exp['message']}")
        
        print(f"\nRecommendations:")
        for rec in detector.get_recommendations(result):
            print(f"  - {rec}")


if __name__ == "__main__":
    main()
