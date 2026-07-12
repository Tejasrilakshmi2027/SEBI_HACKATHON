import re
import email
from email import policy
from email.parser import BytesParser
from typing import Dict, List, Any
import aiofiles
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class EmailPhishingDetector:
    """AI-powered email phishing detection system."""
    
    def __init__(self):
        # Known legitimate domains for SEBI, NSE, BSE, etc.
        self.legitimate_domains = {
            'sebi.gov.in', 'nseindia.com', 'bseindia.com',
            'rbi.org.in', 'mca.gov.in', 'incometax.gov.in'
        }
        
        # Suspicious keywords
        self.urgency_keywords = [
            'urgent', 'immediately', 'act now', 'expire', 'deadline',
            'suspended', 'verify now', 'confirm', 'update now'
        ]
        
        self.suspicious_keywords = [
            'lottery', 'winner', 'prize', 'inheritance', 'unclaimed',
            'password', 'account suspended', 'verify identity', 'security alert'
        ]
        
        # Phishing patterns
        self.phishing_patterns = [
            r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}',  # Credit card pattern
            r'\$\d+[,\d]*\.\d{2}',  # Money pattern
            r'bank\s+transfer',  # Bank transfer
            r'wire\s+transfer',  # Wire transfer
        ]
    
    async def analyze(self, file_path: str) -> Dict[str, Any]:
        """Analyze email file for phishing indicators."""
        
        # Read email file
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
        
        # Parse email
        msg = BytesParser(policy=policy.default).parsebytes(content)
        
        # Extract email components
        analysis = {
            'sender': self._extract_sender(msg),
            'subject': msg.get('subject', ''),
            'to': msg.get('to', ''),
            'cc': msg.get('cc', ''),
            'date': msg.get('date', ''),
            'body': self._extract_body(msg),
            'attachments': self._extract_attachments(msg),
            'headers': dict(msg.items())
        }
        
        # Perform various checks
        checks = {
            'sender_analysis': self._analyze_sender(analysis['sender']),
            'domain_analysis': self._analyze_domain(analysis['sender']),
            'subject_analysis': self._analyze_subject(analysis['subject']),
            'body_analysis': self._analyze_body(analysis['body']),
            'link_analysis': self._analyze_links(analysis['body']),
            'attachment_analysis': self._analyze_attachments(analysis['attachments']),
            'header_analysis': self._analyze_headers(analysis['headers']),
            'urgency_analysis': self._analyze_urgency(analysis['subject'] + ' ' + analysis['body'])
        }
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(checks)
        
        return {
            'analysis': analysis,
            'checks': checks,
            'risk_score': risk_score,
            'is_phishing': risk_score > 0.5
        }
    
    def _extract_sender(self, msg) -> str:
        """Extract sender email address."""
        sender = msg.get('from', '')
        if sender:
            # Extract email from sender string
            match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', sender)
            if match:
                return match.group(0)
        return sender
    
    def _extract_body(self, msg) -> str:
        """Extract email body content."""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        pass
                elif content_type == "text/html":
                    try:
                        html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        soup = BeautifulSoup(html_content, 'html.parser')
                        body += soup.get_text()
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(msg.get_payload())
        return body
    
    def _extract_attachments(self, msg) -> List[str]:
        """Extract attachment filenames."""
        attachments = []
        for part in msg.walk():
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if filename:
                    attachments.append(filename)
        return attachments
    
    def _analyze_sender(self, sender: str) -> Dict[str, Any]:
        """Analyze sender email address."""
        issues = []
        risk_score = 0.0
        
        if not sender:
            issues.append("Missing sender")
            risk_score += 0.3
        
        # Check for suspicious patterns
        if sender:
            # Check for numeric-heavy usernames
            username = sender.split('@')[0] if '@' in sender else sender
            if len(re.findall(r'\d', username)) > len(username) / 2:
                issues.append("Sender username contains excessive numbers")
                risk_score += 0.2
            
            # Check for random character strings
            if len(username) > 10 and re.match(r'^[a-z]+\d+[a-z]+$', username.lower()):
                issues.append("Suspicious sender pattern detected")
                risk_score += 0.2
        
        return {
            'sender': sender,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_domain(self, sender: str) -> Dict[str, Any]:
        """Analyze sender domain."""
        issues = []
        risk_score = 0.0
        
        if '@' not in sender:
            issues.append("Invalid email format")
            risk_score += 0.5
        else:
            domain = sender.split('@')[1].lower()
            
            # Check if domain is in legitimate list
            if domain not in self.legitimate_domains:
                # Check for typosquatting
                for legit_domain in self.legitimate_domains:
                    if self._is_typosquatting(domain, legit_domain):
                        issues.append(f"Potential typosquatting of {legit_domain}")
                        risk_score += 0.4
                        break
                
                # Check for free email providers (suspicious for official communications)
                free_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
                if domain in free_providers:
                    issues.append("Using free email provider for official communication")
                    risk_score += 0.2
                
                # Check for suspicious TLDs
                suspicious_tlds = ['.xyz', '.top', '.zip', '.tk', '.ml']
                if any(domain.endswith(tld) for tld in suspicious_tlds):
                    issues.append("Suspicious top-level domain")
                    risk_score += 0.3
        
        return {
            'domain': sender.split('@')[1] if '@' in sender else 'unknown',
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _is_typosquatting(self, domain: str, legitimate: str) -> bool:
        """Check if domain is a typosquatting attempt."""
        # Simple Levenshtein distance check
        if abs(len(domain) - len(legitimate)) > 2:
            return False
        
        distance = self._levenshtein_distance(domain, legitimate)
        return distance <= 2
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _analyze_subject(self, subject: str) -> Dict[str, Any]:
        """Analyze email subject line."""
        issues = []
        risk_score = 0.0
        subject_lower = subject.lower()
        
        # Check for urgency keywords
        for keyword in self.urgency_keywords:
            if keyword in subject_lower:
                issues.append(f"Urgency keyword found: '{keyword}'")
                risk_score += 0.1
        
        # Check for suspicious keywords
        for keyword in self.suspicious_keywords:
            if keyword in subject_lower:
                issues.append(f"Suspicious keyword found: '{keyword}'")
                risk_score += 0.15
        
        # Check for all caps (often used for urgency)
        if subject.isupper() and len(subject) > 5:
            issues.append("Subject line in all caps")
            risk_score += 0.1
        
        # Check for excessive exclamation marks
        if subject.count('!') > 2:
            issues.append("Excessive exclamation marks in subject")
            risk_score += 0.1
        
        return {
            'subject': subject,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_body(self, body: str) -> Dict[str, Any]:
        """Analyze email body content."""
        issues = []
        risk_score = 0.0
        body_lower = body.lower()
        
        # Check for suspicious keywords
        for keyword in self.suspicious_keywords:
            if keyword in body_lower:
                issues.append(f"Suspicious keyword found: '{keyword}'")
                risk_score += 0.1
        
        # Check for phishing patterns
        for pattern in self.phishing_patterns:
            if re.search(pattern, body_lower):
                issues.append(f"Suspicious pattern detected: {pattern}")
                risk_score += 0.15
        
        # Check for poor grammar (simple heuristic)
        sentences = body.split('.')
        short_sentences = [s for s in sentences if len(s.strip()) < 10 and len(s.strip()) > 0]
        if len(short_sentences) > len(sentences) * 0.3:
            issues.append("Unusual sentence structure detected")
            risk_score += 0.1
        
        return {
            'body_length': len(body),
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_links(self, body: str) -> Dict[str, Any]:
        """Analyze links in email body."""
        issues = []
        risk_score = 0.0
        links = re.findall(r'http[s]?://[^\s<>"]+', body)
        
        if not links:
            return {'links': [], 'issues': [], 'risk_score': 0.0}
        
        for link in links:
            parsed = urlparse(link)
            domain = parsed.netloc.lower()
            
            # Check for IP address instead of domain
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain):
                issues.append(f"Link uses IP address: {domain}")
                risk_score += 0.3
            
            # Check for URL shorteners
            shorteners = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co']
            if any(domain.endswith(shortener) for shortener in shorteners):
                issues.append(f"URL shortener detected: {domain}")
                risk_score += 0.2
            
            # Check for non-HTTPS
            if not link.startswith('https://'):
                issues.append(f"Non-HTTPS link: {link[:50]}...")
                risk_score += 0.1
            
            # Check for suspicious TLDs
            suspicious_tlds = ['.xyz', '.top', '.zip', '.tk', '.ml']
            if any(domain.endswith(tld) for tld in suspicious_tlds):
                issues.append(f"Suspicious TLD in link: {domain}")
                risk_score += 0.2
        
        return {
            'link_count': len(links),
            'links': links[:5],  # Return first 5 links
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_attachments(self, attachments: List[str]) -> Dict[str, Any]:
        """Analyze email attachments."""
        issues = []
        risk_score = 0.0
        
        dangerous_extensions = ['.exe', '.scr', '.bat', '.cmd', '.com', '.pif', '.vbs', '.js']
        suspicious_extensions = ['.zip', '.rar', '.7z', '.doc', '.docm', '.xls', '.xlsm']
        
        for attachment in attachments:
            ext = attachment.lower()
            for dangerous in dangerous_extensions:
                if ext.endswith(dangerous):
                    issues.append(f"Dangerous attachment: {attachment}")
                    risk_score += 0.4
            
            for suspicious in suspicious_extensions:
                if ext.endswith(suspicious):
                    issues.append(f"Suspicious attachment: {attachment}")
                    risk_score += 0.2
        
        # Check for double extensions
        for attachment in attachments:
            if attachment.count('.') > 1:
                issues.append(f"Double extension in: {attachment}")
                risk_score += 0.2
        
        return {
            'attachment_count': len(attachments),
            'attachments': attachments,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Analyze email headers for spoofing."""
        issues = []
        risk_score = 0.0
        
        # Check for missing important headers
        important_headers = ['Received', 'Message-ID', 'Date']
        for header in important_headers:
            if header not in headers:
                issues.append(f"Missing header: {header}")
                risk_score += 0.1
        
        # Check for multiple Received headers (could indicate routing through suspicious servers)
        received_count = headers.get('Received', '').count('Received')
        if received_count > 5:
            issues.append(f"Excessive Received headers: {received_count}")
            risk_score += 0.2
        
        # Check for X-Priority header (often used in spam)
        if 'X-Priority' in headers:
            issues.append("X-Priority header present (common in spam)")
            risk_score += 0.1
        
        return {
            'headers_analyzed': len(headers),
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_urgency(self, text: str) -> Dict[str, Any]:
        """Analyze text for urgency indicators."""
        issues = []
        risk_score = 0.0
        text_lower = text.lower()
        
        urgency_count = sum(1 for keyword in self.urgency_keywords if keyword in text_lower)
        
        if urgency_count > 0:
            issues.append(f"Found {urgency_count} urgency indicators")
            risk_score += min(urgency_count * 0.1, 0.5)
        
        return {
            'urgency_count': urgency_count,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _calculate_risk_score(self, checks: Dict[str, Any]) -> float:
        """Calculate overall phishing risk score."""
        weighted_scores = {
            'sender_analysis': 0.2,
            'domain_analysis': 0.25,
            'subject_analysis': 0.15,
            'body_analysis': 0.1,
            'link_analysis': 0.15,
            'attachment_analysis': 0.1,
            'header_analysis': 0.05
        }
        
        total_score = 0.0
        for check_name, weight in weighted_scores.items():
            if check_name in checks:
                total_score += checks[check_name]['risk_score'] * weight
        
        return min(total_score, 1.0)
