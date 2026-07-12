import re
from typing import Dict, List, Any
from PIL import Image
import io
import aiofiles


class SocialMediaScanner:
    """AI-powered social media content scanner for detecting scams and manipulation."""
    
    def __init__(self):
        # Scam patterns
        self.scam_keywords = [
            'guaranteed returns', 'risk-free investment', 'double your money',
            'insider tip', 'secret strategy', 'pump and dump',
            'get rich quick', 'sure shot', '100% profit',
            'multiplier', 'bonus offer', 'limited time',
            'act now', 'don\'t miss', 'exclusive access'
        ]
        
        # Platform-specific patterns
        self.platform_patterns = {
            'twitter': {
                'hashtags': ['#stock', '#investment', '#trading', '#crypto'],
                'mentions': ['@', '$'],
                'suspicious_chars': ['…', '…']
            },
            'whatsapp': {
                'forwarded': ['forwarded many times', 'forwarded message'],
                'links': ['http', 'https', 'www.']
            },
            'telegram': {
                'channels': ['t.me/', 'joinchat'],
                'signals': ['signal', 'call', 'target']
            }
        }
        
        # Pump and dump patterns
        self.pump_dump_patterns = [
            r'\$\w+\s+to\s+the\s+moon',
            r'buy\s+now\s+before\s+pump',
            r'will\s+go\s+\d+x',
            r'rocket\s+emoji',
            r'🚀'
        ]
    
    async def scan(self, file_path: str) -> Dict[str, Any]:
        """Scan social media content for scams."""
        
        # Determine file type and read content
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            return await self._scan_image(file_path)
        else:
            # Assume text content
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            return await self._scan_text(content)
    
    async def _scan_image(self, file_path: str) -> Dict[str, Any]:
        """Scan social media screenshot image."""
        try:
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
            
            img = Image.open(io.BytesIO(image_bytes))
            
            # Perform OCR to extract text
            try:
                import pytesseract
                text = pytesseract.image_to_string(img)
            except:
                text = ""
            
            # Analyze the extracted text
            text_analysis = await self._scan_text(text)
            
            # Add image-specific analysis
            image_analysis = {
                'image_format': img.format,
                'image_size': img.size,
                'has_text': len(text) > 0
            }
            
            return {
                'type': 'image',
                'image_analysis': image_analysis,
                'text_analysis': text_analysis,
                'risk_score': text_analysis['risk_score'],
                'is_scam': text_analysis['risk_score'] > 0.5
            }
        except Exception as e:
            return {
                'error': f'Image scan failed: {str(e)}',
                'risk_score': 0.0,
                'is_scam': False
            }
    
    async def _scan_text(self, content: str) -> Dict[str, Any]:
        """Scan text content for scam patterns."""
        
        checks = {
            'scam_keyword_analysis': self._analyze_scam_keywords(content),
            'pump_dump_analysis': self._analyze_pump_dump(content),
            'urgency_analysis': self._analyze_urgency(content),
            'link_analysis': self._analyze_links(content),
            'platform_analysis': self._detect_platform(content),
            'sentiment_analysis': self._analyze_sentiment(content),
            'grammar_analysis': self._analyze_grammar(content)
        }
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(checks)
        
        return {
            'content_length': len(content),
            'checks': checks,
            'risk_score': risk_score,
            'is_scam': risk_score > 0.5
        }
    
    def _analyze_scam_keywords(self, content: str) -> Dict[str, Any]:
        """Analyze for scam keywords."""
        issues = []
        risk_score = 0.0
        content_lower = content.lower()
        
        found_keywords = []
        for keyword in self.scam_keywords:
            if keyword in content_lower:
                found_keywords.append(keyword)
                risk_score += 0.1
        
        if found_keywords:
            issues.append(f"Scam keywords found: {', '.join(found_keywords)}")
        
        # Check for excessive capitalization
        caps_ratio = sum(1 for c in content if c.isupper()) / len(content) if content else 0
        if caps_ratio > 0.3:
            issues.append(f"Excessive capitalization: {caps_ratio:.2%}")
            risk_score += 0.15
        
        return {
            'found_keywords': found_keywords,
            'caps_ratio': caps_ratio,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_pump_dump(self, content: str) -> Dict[str, Any]:
        """Analyze for pump and dump patterns."""
        issues = []
        risk_score = 0.0
        
        for pattern in self.pump_dump_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Pump and dump pattern detected: {pattern}")
                risk_score += 0.25
        
        # Check for stock ticker mentions
        ticker_pattern = r'\$[A-Z]{1,5}'
        tickers = re.findall(ticker_pattern, content)
        
        if len(tickers) > 3:
            issues.append(f"Excessive stock ticker mentions: {len(tickers)}")
            risk_score += 0.2
        
        # Check for price targets
        price_pattern = r'target\s+\$?\d+'
        if re.search(price_pattern, content, re.IGNORECASE):
            issues.append("Price target mentioned")
            risk_score += 0.15
        
        return {
            'ticker_count': len(tickers),
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_urgency(self, content: str) -> Dict[str, Any]:
        """Analyze urgency indicators."""
        issues = []
        risk_score = 0.0
        content_lower = content.lower()
        
        urgency_keywords = [
            'urgent', 'immediately', 'now', 'today', 'limited time',
            'ending soon', 'last chance', 'don\'t wait', 'act fast'
        ]
        
        urgency_count = sum(1 for keyword in urgency_keywords if keyword in content_lower)
        
        if urgency_count > 0:
            issues.append(f"Urgency indicators found: {urgency_count}")
            risk_score += min(urgency_count * 0.1, 0.4)
        
        # Check for time pressure
        time_patterns = [r'\d+\s+hours?', r'\d+\s+minutes?', r'ends?\s+\d+']
        for pattern in time_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append("Time pressure detected")
                risk_score += 0.15
                break
        
        return {
            'urgency_count': urgency_count,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_links(self, content: str) -> Dict[str, Any]:
        """Analyze links in content."""
        issues = []
        risk_score = 0.0
        
        # Extract URLs
        url_pattern = r'http[s]?://[^\s<>"]+'
        urls = re.findall(url_pattern, content)
        
        if len(urls) > 0:
            # Check for URL shorteners
            shorteners = ['bit.ly', 'tinyurl.com', 't.co', 'ow.ly']
            for url in urls:
                for shortener in shorteners:
                    if shortener in url:
                        issues.append(f"URL shortener detected: {url}")
                        risk_score += 0.2
            
            # Check for suspicious domains
            suspicious_tlds = ['.xyz', '.top', '.zip', '.tk']
            for url in urls:
                for tld in suspicious_tlds:
                    if url.endswith(tld):
                        issues.append(f"Suspicious TLD in URL: {url}")
                        risk_score += 0.25
            
            # Check for excessive links
            if len(urls) > 3:
                issues.append(f"Excessive links: {len(urls)}")
                risk_score += 0.15
        
        return {
            'link_count': len(urls),
            'urls': urls[:5],
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _detect_platform(self, content: str) -> Dict[str, Any]:
        """Detect social media platform."""
        issues = []
        risk_score = 0.0
        
        detected_platforms = []
        
        # Twitter detection
        if '@' in content and '#' in content:
            detected_platforms.append('twitter')
        
        # WhatsApp detection
        if 'whatsapp' in content.lower() or 'forwarded' in content.lower():
            detected_platforms.append('whatsapp')
        
        # Telegram detection
        if 'telegram' in content.lower() or 't.me/' in content:
            detected_platforms.append('telegram')
        
        # Instagram detection
        if 'instagram' in content.lower() or 'insta' in content.lower():
            detected_platforms.append('instagram')
        
        if not detected_platforms:
            issues.append("Could not detect social media platform")
            risk_score += 0.1
        
        return {
            'detected_platforms': detected_platforms,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment of content."""
        issues = []
        risk_score = 0.0
        
        # Simple sentiment analysis
        positive_words = ['amazing', 'incredible', 'fantastic', 'best', 'perfect', 'guaranteed']
        negative_words = ['scam', 'fake', 'fraud', 'lose', 'risk', 'danger']
        
        positive_count = sum(1 for word in positive_words if word in content.lower())
        negative_count = sum(1 for word in negative_words if word in content.lower())
        
        # Overly positive sentiment without warnings is suspicious
        if positive_count > 3 and negative_count == 0:
            issues.append("Overly positive sentiment without risk warnings")
            risk_score += 0.25
        
        # Check for emotional manipulation
        emotional_words = ['excited', 'happy', 'lucky', 'blessed', 'thrilled']
        emotional_count = sum(1 for word in emotional_words if word in content.lower())
        
        if emotional_count > 2:
            issues.append("Emotional manipulation detected")
            risk_score += 0.15
        
        return {
            'positive_count': positive_count,
            'negative_count': negative_count,
            'emotional_count': emotional_count,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_grammar(self, content: str) -> Dict[str, Any]:
        """Analyze grammar and writing style."""
        issues = []
        risk_score = 0.0
        
        # Check for excessive exclamation marks
        exclamation_count = content.count('!')
        if exclamation_count > 3:
            issues.append(f"Excessive exclamation marks: {exclamation_count}")
            risk_score += 0.15
        
        # Check for multiple question marks
        question_count = content.count('?')
        if question_count > 2:
            issues.append(f"Excessive question marks: {question_count}")
            risk_score += 0.1
        
        # Check for all caps words
        words = content.split()
        caps_words = [word for word in words if word.isupper() and len(word) > 1]
        
        if len(caps_words) > 3:
            issues.append(f"Excessive all-caps words: {len(caps_words)}")
            risk_score += 0.15
        
        # Check for poor sentence structure
        sentences = content.split('.')
        short_sentences = [s for s in sentences if 0 < len(s.strip()) < 10]
        
        if len(short_sentences) > len(sentences) * 0.4:
            issues.append("Unusual sentence structure")
            risk_score += 0.1
        
        return {
            'exclamation_count': exclamation_count,
            'question_count': question_count,
            'caps_words': len(caps_words),
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _calculate_risk_score(self, checks: Dict[str, Any]) -> float:
        """Calculate overall scam risk score."""
        weighted_scores = {
            'scam_keyword_analysis': 0.3,
            'pump_dump_analysis': 0.25,
            'urgency_analysis': 0.15,
            'link_analysis': 0.15,
            'sentiment_analysis': 0.1,
            'grammar_analysis': 0.05
        }
        
        total_score = 0.0
        for check_name, weight in weighted_scores.items():
            if check_name in checks:
                total_score += checks[check_name]['risk_score'] * weight
        
        return min(total_score, 1.0)
