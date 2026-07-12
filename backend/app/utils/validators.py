import re
from typing import Optional
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """Validate if a string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_valid_email(email: str) -> bool:
    """Validate if a string is a valid email address."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove dangerous characters."""
    # Remove path traversal attempts
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    # Remove null bytes
    filename = filename.replace('\x00', '')
    return filename


def detect_typosquatting(domain: str, legitimate_domains: list) -> Optional[str]:
    """Detect if a domain is a typosquatting attempt."""
    domain = domain.lower()
    
    for legit_domain in legitimate_domains:
        legit_domain = legit_domain.lower()
        
        # Check for character substitution
        if levenshtein_distance(domain, legit_domain) <= 2:
            return legit_domain
        
        # Check for common typosquatting patterns
        if domain.replace('-', '') == legit_domain.replace('-', ''):
            return legit_domain
        
        if domain.replace('0', 'o') == legit_domain:
            return legit_domain
        if domain.replace('1', 'l') == legit_domain:
            return legit_domain
        if domain.replace('1', 'i') == legit_domain:
            return legit_domain
    
    return None


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
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
