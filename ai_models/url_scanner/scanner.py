import re
import ssl
import socket
from typing import Dict, List, Any
from urllib.parse import urlparse
import whois
import datetime


class URLScanner:
    """AI-powered URL security scanner."""
    
    def __init__(self):
        # Known legitimate domains
        self.legitimate_domains = {
            'sebi.gov.in', 'nseindia.com', 'bseindia.com',
            'rbi.org.in', 'mca.gov.in', 'incometax.gov.in',
            'nsdl.co.in', 'cdslindia.com'
        }
        
        # Suspicious TLDs
        self.suspicious_tlds = [
            '.xyz', '.top', '.zip', '.tk', '.ml', '.ga', '.cf',
            '.gq', '.cc', '.pw', '.club', '.online', '.site'
        ]
        
        # URL shorteners
        self.url_shorteners = [
            'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly',
            'is.gd', 'buff.ly', 'rebrand.ly', 'short.io'
        ]
        
        # Known phishing blacklist (sample)
        self.phishing_blacklist = [
            'sebi-verify.com', 'nse-secure.net', 'bse-login.org',
            'sebi-alert.com', 'stock-update.xyz'
        ]
    
    async def scan(self, file_path: str) -> Dict[str, Any]:
        """Scan URL from file."""
        # For file input, assume it contains a URL
        import aiofiles
        async with aiofiles.open(file_path, 'r') as f:
            url = await f.read()
        
        return await self.scan_url(url.strip())
    
    async def scan_url(self, url: str) -> Dict[str, Any]:
        """Perform comprehensive URL security scan."""
        
        # Parse URL
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Perform various checks
        checks = {
            'ssl_check': await self._check_ssl(domain),
            'https_check': self._check_https(url),
            'domain_age': await self._check_domain_age(domain),
            'whois_check': await self._check_whois(domain),
            'typosquatting_check': self._check_typosquatting(domain),
            'blacklist_check': self._check_blacklist(domain),
            'suspicious_tld_check': self._check_suspicious_tld(domain),
            'url_shortener_check': self._check_url_shortener(domain),
            'subdomain_check': self._check_subdomain(domain),
            'special_chars_check': self._check_special_chars(domain)
        }
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(checks)
        
        return {
            'url': url,
            'domain': domain,
            'checks': checks,
            'risk_score': risk_score,
            'is_malicious': risk_score > 0.5
        }
    
    async def _check_ssl(self, domain: str) -> Dict[str, Any]:
        """Check SSL certificate validity."""
        issues = []
        risk_score = 0.0
        
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check certificate validity
                    if cert:
                        issues.append("Valid SSL certificate present")
                    else:
                        issues.append("Invalid or missing SSL certificate")
                        risk_score += 0.4
        except Exception as e:
            issues.append(f"SSL check failed: {str(e)}")
            risk_score += 0.5
        
        return {
            'has_ssl': risk_score == 0.0,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _check_https(self, url: str) -> Dict[str, Any]:
        """Check if URL uses HTTPS."""
        issues = []
        risk_score = 0.0
        
        if not url.startswith('https://'):
            issues.append("URL does not use HTTPS")
            risk_score += 0.3
        else:
            issues.append("URL uses HTTPS")
        
        return {
            'uses_https': url.startswith('https://'),
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    async def _check_domain_age(self, domain: str) -> Dict[str, Any]:
        """Check domain age."""
        issues = []
        risk_score = 0.0
        
        try:
            domain_info = whois.whois(domain)
            
            if domain_info and domain_info.creation_date:
                if isinstance(domain_info.creation_date, list):
                    creation_date = domain_info.creation_date[0]
                else:
                    creation_date = domain_info.creation_date
                
                age_days = (datetime.datetime.now() - creation_date).days
                
                if age_days < 30:
                    issues.append(f"Domain is very young ({age_days} days)")
                    risk_score += 0.4
                elif age_days < 90:
                    issues.append(f"Domain is relatively young ({age_days} days)")
                    risk_score += 0.2
                else:
                    issues.append(f"Domain age is reasonable ({age_days} days)")
            else:
                issues.append("Could not determine domain age")
                risk_score += 0.2
        except Exception as e:
            issues.append(f"Domain age check failed: {str(e)}")
            risk_score += 0.1
        
        return {
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    async def _check_whois(self, domain: str) -> Dict[str, Any]:
        """Check WHOIS information."""
        issues = []
        risk_score = 0.0
        
        try:
            domain_info = whois.whois(domain)
            
            if not domain_info:
                issues.append("No WHOIS information available")
                risk_score += 0.3
            else:
                # Check for privacy protection
                registrar = domain_info.registrar
                if registrar and 'privacy' in registrar.lower():
                    issues.append("Domain uses privacy protection")
                    risk_score += 0.1
                
                # Check registrant information
                if not domain_info.org:
                    issues.append("No organization information in WHOIS")
                    risk_score += 0.1
        except Exception as e:
            issues.append(f"WHOIS check failed: {str(e)}")
            risk_score += 0.1
        
        return {
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _check_typosquatting(self, domain: str) -> Dict[str, Any]:
        """Check for typosquatting."""
        issues = []
        risk_score = 0.0
        
        for legit_domain in self.legitimate_domains:
            if self._is_typosquatting(domain, legit_domain):
                issues.append(f"Potential typosquatting of {legit_domain}")
                risk_score += 0.5
                break
        
        return {
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _is_typosquatting(self, domain: str, legitimate: str) -> bool:
        """Check if domain is a typosquatting attempt."""
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
    
    def _check_blacklist(self, domain: str) -> Dict[str, Any]:
        """Check if domain is in phishing blacklist."""
        issues = []
        risk_score = 0.0
        
        for blacklisted in self.phishing_blacklist:
            if domain == blacklisted or domain.endswith('.' + blacklisted):
                issues.append(f"Domain found in phishing blacklist: {blacklisted}")
                risk_score += 1.0
                break
        
        if risk_score == 0.0:
            issues.append("Domain not in known blacklist")
        
        return {
            'is_blacklisted': risk_score > 0.0,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _check_suspicious_tld(self, domain: str) -> Dict[str, Any]:
        """Check for suspicious top-level domains."""
        issues = []
        risk_score = 0.0
        
        for tld in self.suspicious_tlds:
            if domain.endswith(tld):
                issues.append(f"Suspicious TLD detected: {tld}")
                risk_score += 0.3
                break
        
        return {
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _check_url_shortener(self, domain: str) -> Dict[str, Any]:
        """Check if URL uses a shortener service."""
        issues = []
        risk_score = 0.0
        
        for shortener in self.url_shorteners:
            if domain == shortener or domain.endswith('.' + shortener):
                issues.append(f"URL shortener detected: {shortener}")
                risk_score += 0.3
                break
        
        return {
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _check_subdomain(self, domain: str) -> Dict[str, Any]:
        """Check for suspicious subdomains."""
        issues = []
        risk_score = 0.0
        
        parts = domain.split('.')
        
        # Check for excessive subdomains
        if len(parts) > 4:
            issues.append(f"Excessive subdomains: {len(parts) - 2}")
            risk_score += 0.2
        
        # Check for random-looking subdomains
        if len(parts) > 2:
            subdomain = parts[0]
            if len(subdomain) > 15 and re.match(r'^[a-z0-9]+$', subdomain):
                issues.append("Suspicious subdomain pattern")
                risk_score += 0.2
        
        return {
            'subdomain_count': len(parts) - 2,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _check_special_chars(self, domain: str) -> Dict[str, Any]:
        """Check for special characters in domain."""
        issues = []
        risk_score = 0.0
        
        # Check for non-standard characters
        if re.search(r'[^a-zA-Z0-9.-]', domain):
            issues.append("Domain contains special characters")
            risk_score += 0.3
        
        # Check for hyphen abuse
        if domain.count('-') > 3:
            issues.append("Excessive hyphens in domain")
            risk_score += 0.2
        
        # Check for consecutive hyphens
        if '--' in domain:
            issues.append("Consecutive hyphens in domain")
            risk_score += 0.2
        
        return {
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _calculate_risk_score(self, checks: Dict[str, Any]) -> float:
        """Calculate overall URL risk score."""
        weighted_scores = {
            'ssl_check': 0.2,
            'https_check': 0.15,
            'domain_age': 0.15,
            'whois_check': 0.1,
            'typosquatting_check': 0.2,
            'blacklist_check': 0.1,
            'suspicious_tld_check': 0.05,
            'url_shortener_check': 0.05
        }
        
        total_score = 0.0
        for check_name, weight in weighted_scores.items():
            if check_name in checks:
                total_score += checks[check_name]['risk_score'] * weight
        
        return min(total_score, 1.0)
