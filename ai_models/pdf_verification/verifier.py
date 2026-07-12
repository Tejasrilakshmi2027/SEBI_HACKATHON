import fitz  # PyMuPDF
from PIL import Image
import io
import re
from typing import Dict, List, Any
import aiofiles
import pytesseract
import cv2
import numpy as np
from datetime import datetime


class PDFVerifier:
    """AI-powered PDF verification system for detecting fake_documents."""
    
    def __init__(self):
        # Known legitimate organizations
        self.legitimate_orgs = {
            'SEBI', 'Securities and Exchange Board of India',
            'NSE', 'National Stock Exchange',
            'BSE', 'Bombay Stock Exchange',
            'RBI', 'Reserve Bank of India'
        }
        
        # Suspicious keywords in fake documents
        self.suspicious_keywords = [
            'urgent action required', 'immediate payment',
            'account suspended', 'verify now', 'lottery winner',
            'unclaimed funds', 'inheritance', 'prize money'
        ]
    
    async def verify(self, file_path: str) -> Dict[str, Any]:
        """Verify PDF document authenticity."""
        
        # Open PDF
        doc = fitz.open(file_path)
        
        # Extract metadata
        metadata = self._extract_metadata(doc)
        
        # Extract text content
        text_content = self._extract_text(doc)
        
        # Extract images
        images = self._extract_images(doc)
        
        # Perform various checks
        checks = {
            'metadata_analysis': self._analyze_metadata(metadata),
            'text_analysis': self._analyze_text(text_content),
            'logo_analysis': await self._analyze_logos(images),
            'layout_analysis': self._analyze_layout(doc),
            'signature_analysis': await self._analyze_signatures(images),
            'qr_analysis': await self._analyze_qr_codes(images),
            'font_analysis': self._analyze_fonts(doc),
            'watermark_analysis': await self._analyze_watermarks(doc)
        }
        
        doc.close()
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(checks)
        
        return {
            'metadata': metadata,
            'checks': checks,
            'risk_score': risk_score,
            'is_forged': risk_score > 0.5
        }
    
    def _extract_metadata(self, doc) -> Dict[str, Any]:
        """Extract PDF metadata."""
        metadata = doc.metadata
        return {
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'subject': metadata.get('subject', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creation_date': metadata.get('creationDate', ''),
            'modification_date': metadata.get('modDate', ''),
            'page_count': len(doc)
        }
    
    def _extract_text(self, doc) -> str:
        """Extract text from PDF."""
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    
    def _extract_images(self, doc) -> List[bytes]:
        """Extract images from PDF."""
        images = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                images.append(image_bytes)
        
        return images
    
    def _analyze_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze PDF metadata for inconsistencies."""
        issues = []
        risk_score = 0.0
        
        # Check for missing metadata
        if not metadata.get('author'):
            issues.append("Missing author metadata")
            risk_score += 0.1
        
        if not metadata.get('creation_date'):
            issues.append("Missing creation date")
            risk_score += 0.1
        
        # Check for suspicious creator tools
        suspicious_creators = ['online converter', 'free pdf maker', 'pdf generator']
        creator = metadata.get('creator', '').lower()
        for suspicious in suspicious_creators:
            if suspicious in creator:
                issues.append(f"Suspicious creator tool: {creator}")
                risk_score += 0.2
        
        # Check for future dates
        if metadata.get('creation_date'):
            try:
                creation_date = datetime.strptime(metadata['creation_date'], "D:%Y%m%d%H%M%S%z")
                if creation_date > datetime.now():
                    issues.append("Creation date is in the future")
                    risk_score += 0.3
            except:
                pass
        
        return {
            'metadata': metadata,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text content for suspicious patterns."""
        issues = []
        risk_score = 0.0
        text_lower = text.lower()
        
        # Check for suspicious keywords
        for keyword in self.suspicious_keywords:
            if keyword in text_lower:
                issues.append(f"Suspicious keyword found: '{keyword}'")
                risk_score += 0.15
        
        # Check for legitimate organization mentions
        org_mentions = []
        for org in self.legitimate_orgs:
            if org.lower() in text_lower:
                org_mentions.append(org)
        
        if not org_mentions:
            issues.append("No legitimate organization mentioned")
            risk_score += 0.1
        
        # Check for poor OCR quality indicators
        if len(text) < 100:
            issues.append("Very low text content (possible poor OCR)")
            risk_score += 0.2
        
        # Check for inconsistent spacing
        if re.search(r'  +', text):
            issues.append("Inconsistent spacing detected")
            risk_score += 0.1
        
        return {
            'text_length': len(text),
            'org_mentions': org_mentions,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    async def _analyze_logos(self, images: List[bytes]) -> Dict[str, Any]:
        """Analyze extracted images for logos."""
        issues = []
        risk_score = 0.0
        
        if not images:
            issues.append("No images found in PDF")
            risk_score += 0.2
            return {'image_count': 0, 'issues': issues, 'risk_score': min(risk_score, 1.0)}
        
        # Analyze each image for logo characteristics
        logo_count = 0
        for img_bytes in images:
            try:
                img = Image.open(io.BytesIO(img_bytes))
                
                # Check image dimensions (logos are typically small)
                width, height = img.size
                if width < 200 and height < 200:
                    logo_count += 1
                
                # Check for transparency (common in logos)
                if img.mode in ('RGBA', 'LA'):
                    logo_count += 0.5
            except:
                pass
        
        if logo_count == 0:
            issues.append("No potential logos detected")
            risk_score += 0.2
        
        return {
            'image_count': len(images),
            'potential_logos': logo_count,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_layout(self, doc) -> Dict[str, Any]:
        """Analyze PDF layout for inconsistencies."""
        issues = []
        risk_score = 0.0
        
        # Check for inconsistent page sizes
        page_sizes = set()
        for page in doc:
            rect = page.rect
            page_sizes.add((rect.width, rect.height))
        
        if len(page_sizes) > 1:
            issues.append("Inconsistent page sizes detected")
            risk_score += 0.2
        
        # Check for very short documents
        if len(doc) < 2:
            issues.append("Document has very few pages")
            risk_score += 0.1
        
        return {
            'page_count': len(doc),
            'page_sizes': list(page_sizes),
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    async def _analyze_signatures(self, images: List[bytes]) -> Dict[str, Any]:
        """Analyze images for signature patterns."""
        issues = []
        risk_score = 0.0
        
        signature_count = 0
        for img_bytes in images:
            try:
                img = Image.open(io.BytesIO(img_bytes))
                img_array = np.array(img)
                
                # Convert to grayscale
                if len(img_array.shape) == 3:
                    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                else:
                    gray = img_array
                
                # Apply edge detection (signatures have distinctive edges)
                edges = cv2.Canny(gray, 50, 150)
                
                # Check for signature-like patterns
                edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
                if 0.01 < edge_density < 0.1:
                    signature_count += 1
            except:
                pass
        
        return {
            'signature_count': signature_count,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    async def _analyze_qr_codes(self, images: List[bytes]) -> Dict[str, Any]:
        """Analyze images for QR codes."""
        issues = []
        risk_score = 0.0
        
        qr_count = 0
        for img_bytes in images:
            try:
                img = Image.open(io.BytesIO(img_bytes))
                img_array = np.array(img)
                
                # Detect QR codes
                detector = cv2.QRCodeDetector()
                retval, points = detector.detect(img_array)
                
                if retval:
                    qr_count += 1
            except:
                pass
        
        if qr_count > 0:
            issues.append(f"QR codes detected: {qr_count}")
            risk_score += 0.1
        
        return {
            'qr_count': qr_count,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_fonts(self, doc) -> Dict[str, Any]:
        """Analyze font usage in PDF."""
        issues = []
        risk_score = 0.0
        
        fonts = set()
        for page in doc:
            text_dict = page.get_text("dict")
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            font = span.get("font", "")
                            fonts.add(font)
        
        # Check for too many different fonts
        if len(fonts) > 10:
            issues.append(f"Excessive font variety: {len(fonts)} fonts")
            risk_score += 0.2
        
        # Check for suspicious font names
        suspicious_fonts = ['downloaded', 'web', 'online']
        for font in fonts:
            font_lower = font.lower()
            for suspicious in suspicious_fonts:
                if suspicious in font_lower:
                    issues.append(f"Suspicious font: {font}")
                    risk_score += 0.1
        
        return {
            'font_count': len(fonts),
            'fonts': list(fonts)[:10],
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    async def _analyze_watermarks(self, doc) -> Dict[str, Any]:
        """Analyze for watermarks."""
        issues = []
        risk_score = 0.0
        
        # Check for watermark text
        watermark_keywords = ['draft', 'confidential', 'sample', 'copy', 'unofficial']
        text = self._extract_text(doc).lower()
        
        for keyword in watermark_keywords:
            if keyword in text:
                issues.append(f"Watermark indicator found: '{keyword}'")
                risk_score += 0.15
        
        return {
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _calculate_risk_score(self, checks: Dict[str, Any]) -> float:
        """Calculate overall PDF forgery risk score."""
        weighted_scores = {
            'metadata_analysis': 0.2,
            'text_analysis': 0.25,
            'logo_analysis': 0.15,
            'layout_analysis': 0.1,
            'signature_analysis': 0.1,
            'qr_analysis': 0.1,
            'font_analysis': 0.05,
            'watermark_analysis': 0.05
        }
        
        total_score = 0.0
        for check_name, weight in weighted_scores.items():
            if check_name in checks:
                total_score += checks[check_name]['risk_score'] * weight
        
        return min(total_score, 1.0)
