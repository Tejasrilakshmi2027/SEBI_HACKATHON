"""
PDF Verification Engine
Uses EasyOCR for text extraction, logo detection, metadata verification, and forgery detection
"""

import os
import io
import re
import json
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np
from PIL import Image
import easyocr
import cv2
import PyPDF2
from pdf2image import convert_from_path
import pikepdf


class PDFVerifier:
    """PDF Verification Engine with forgery detection"""
    
    def __init__(self):
        self.ocr_reader = easyocr.Reader(['en'], gpu=False)
        self.trusted_logos = self._load_trusted_logos()
        self.trusted_signatures = self._load_trusted_signatures()
    
    def _load_trusted_logos(self) -> Dict[str, np.ndarray]:
        """Load trusted logos for verification"""
        logos = {}
        logo_dir = os.path.join(os.path.dirname(__file__), "trusted_logos")
        if os.path.exists(logo_dir):
            for filename in os.listdir(logo_dir):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    logo_name = os.path.splitext(filename)[0]
                    logo_path = os.path.join(logo_dir, filename)
                    logos[logo_name] = cv2.imread(logo_path, cv2.IMREAD_GRAYSCALE)
        return logos
    
    def _load_trusted_signatures(self) -> Dict[str, np.ndarray]:
        """Load trusted signatures for verification"""
        signatures = {}
        sig_dir = os.path.join(os.path.dirname(__file__), "trusted_signatures")
        if os.path.exists(sig_dir):
            for filename in os.listdir(sig_dir):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    sig_name = os.path.splitext(filename)[0]
                    sig_path = os.path.join(sig_dir, filename)
                    signatures[sig_name] = cv2.imread(sig_path, cv2.IMREAD_GRAYSCALE)
        return signatures
    
    def extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract PDF metadata"""
        metadata = {}
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                if reader.metadata:
                    metadata['title'] = reader.metadata.get('/Title', '')
                    metadata['author'] = reader.metadata.get('/Author', '')
                    metadata['subject'] = reader.metadata.get('/Subject', '')
                    metadata['creator'] = reader.metadata.get('/Creator', '')
                    metadata['producer'] = reader.metadata.get('/Producer', '')
                    metadata['creation_date'] = reader.metadata.get('/CreationDate', '')
                    metadata['modification_date'] = reader.metadata.get('/ModDate', '')
                
                metadata['page_count'] = len(reader.pages)
                metadata['is_encrypted'] = reader.is_encrypted
                
                with pikepdf.open(pdf_path) as pdf:
                    metadata['pdf_version'] = pdf.pdf_version
                    metadata['has_xref_stream'] = 'XRefStm' in pdf.Root.keys()
                    
        except Exception as e:
            metadata['error'] = str(e)
        
        return metadata
    
    def verify_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Verify PDF metadata for signs of forgery"""
        verification = {
            'is_valid': True,
            'issues': [],
            'warnings': []
        }
        
        if not metadata.get('title'):
            verification['warnings'].append('Missing title in metadata')
        
        if not metadata.get('author'):
            verification['warnings'].append('Missing author in metadata')
        
        if metadata.get('is_encrypted'):
            verification['warnings'].append('PDF is encrypted - may hide forgery')
        
        if metadata.get('page_count', 0) < 1:
            verification['is_valid'] = False
            verification['issues'].append('Invalid page count')
        
        if metadata.get('pdf_version', '') not in ['1.4', '1.5', '1.6', '1.7', '2.0']:
            verification['warnings'].append(f'Unusual PDF version: {metadata.get("pdf_version")}')
        
        return verification
    
    def extract_text_with_ocr(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text from PDF using OCR"""
        extracted_data = []
        
        try:
            images = convert_from_path(pdf_path, dpi=200)
            
            for page_num, image in enumerate(images):
                image_np = np.array(image)
                
                result = self.ocr_reader.readtext(image_np)
                
                page_text = ' '.join([text[1] for text in result])
                page_confidence = np.mean([text[2] for text in result]) if result else 0
                
                extracted_data.append({
                    'page_number': page_num + 1,
                    'text': page_text,
                    'confidence': float(page_confidence),
                    'text_regions': [
                        {
                            'text': text[1],
                            'bbox': text[0],
                            'confidence': float(text[2])
                        }
                        for text in result
                    ]
                })
                
        except Exception as e:
            extracted_data.append({'error': str(e)})
        
        return extracted_data
    
    def detect_logos(self, pdf_path: str) -> Dict[str, Any]:
        """Detect logos in PDF using template matching"""
        logo_results = {
            'detected_logos': [],
            'confidence_scores': {},
            'positions': []
        }
        
        if not self.trusted_logos:
            return logo_results
        
        try:
            images = convert_from_path(pdf_path, dpi=200)
            
            for page_num, image in enumerate(images):
                image_np = np.array(image)
                gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
                
                for logo_name, logo_template in self.trusted_logos.items():
                    try:
                        h, w = logo_template.shape
                        
                        res = cv2.matchTemplate(gray, logo_template, cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                        
                        if max_val > 0.7:
                            logo_results['detected_logos'].append(logo_name)
                            logo_results['confidence_scores'][logo_name] = float(max_val)
                            logo_results['positions'].append({
                                'logo': logo_name,
                                'page': page_num + 1,
                                'position': max_loc,
                                'confidence': float(max_val)
                            })
                    except Exception as e:
                        continue
                        
        except Exception as e:
            logo_results['error'] = str(e)
        
        return logo_results
    
    def detect_signatures(self, pdf_path: str) -> Dict[str, Any]:
        """Detect signatures in PDF"""
        signature_results = {
            'detected_signatures': [],
            'confidence_scores': {},
            'positions': []
        }
        
        if not self.trusted_signatures:
            return signature_results
        
        try:
            images = convert_from_path(pdf_path, dpi=200)
            
            for page_num, image in enumerate(images):
                image_np = np.array(image)
                gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
                
                for sig_name, sig_template in self.trusted_signatures.items():
                    try:
                        h, w = sig_template.shape
                        
                        res = cv2.matchTemplate(gray, sig_template, cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                        
                        if max_val > 0.65:
                            signature_results['detected_signatures'].append(sig_name)
                            signature_results['confidence_scores'][sig_name] = float(max_val)
                            signature_results['positions'].append({
                                'signature': sig_name,
                                'page': page_num + 1,
                                'position': max_loc,
                                'confidence': float(max_val)
                            })
                    except Exception as e:
                        continue
                        
        except Exception as e:
            signature_results['error'] = str(e)
        
        return signature_results
    
    def detect_forgery_indicators(self, pdf_path: str, extracted_text: List[Dict]) -> Dict[str, Any]:
        """Detect indicators of document forgery"""
        forgery_indicators = {
            'inconsistencies': [],
            'suspicious_patterns': [],
            'confidence': 0.0
        }
        
        full_text = ' '.join([page.get('text', '') for page in extracted_text])
        
        suspicious_keywords = [
            'guaranteed', '100%', 'risk free', 'no loss',
            'secret', 'insider', 'exclusive', 'limited time',
            'urgent', 'act now', 'immediate'
        ]
        
        for keyword in suspicious_keywords:
            if keyword.lower() in full_text.lower():
                forgery_indicators['suspicious_patterns'].append({
                    'type': 'suspicious_keyword',
                    'keyword': keyword,
                    'context': self._get_keyword_context(full_text, keyword)
                })
        
        sebi_keywords = ['sebi', 'nse', 'bse', 'rbi', 'mutual fund', 'amfi']
        sebi_count = sum(1 for keyword in sebi_keywords if keyword.lower() in full_text.lower())
        
        if sebi_count == 0:
            forgery_indicators['inconsistencies'].append({
                'type': 'missing_regulatory_references',
                'message': 'No SEBI/NSE/BSE references found in financial document'
            })
        
        registration_pattern = r'\b(?:ARN|PAN|CIN|GSTIN)[A-Z0-9]{10,}\b'
        registrations = re.findall(registration_pattern, full_text, re.IGNORECASE)
        
        if not registrations:
            forgery_indicators['inconsistencies'].append({
                'type': 'missing_registration_numbers',
                'message': 'No registration numbers (ARN, PAN, CIN, GSTIN) found'
            })
        
        font_inconsistencies = self._detect_font_inconsistencies(extracted_text)
        if font_inconsistencies:
            forgery_indicators['inconsistencies'].extend(font_inconsistencies)
        
        total_indicators = len(forgery_indicators['inconsistencies']) + len(forgery_indicators['suspicious_patterns'])
        forgery_indicators['confidence'] = min(total_indicators / 10.0, 1.0)
        
        return forgery_indicators
    
    def _get_keyword_context(self, text: str, keyword: str, context_length: 50) -> str:
        """Get context around a keyword"""
        index = text.lower().find(keyword.lower())
        if index == -1:
            return ''
        
        start = max(0, index - context_length)
        end = min(len(text), index + len(keyword) + context_length)
        
        return text[start:end]
    
    def _detect_font_inconsistencies(self, extracted_text: List[Dict]) -> List[Dict]:
        """Detect font inconsistencies across pages"""
        inconsistencies = []
        
        if len(extracted_text) < 2:
            return inconsistencies
        
        avg_confidences = [page.get('confidence', 0) for page in extracted_text]
        confidence_std = np.std(avg_confidences)
        
        if confidence_std > 0.2:
            inconsistencies.append({
                'type': 'font_inconsistency',
                'message': f'High variance in OCR confidence across pages (std: {confidence_std:.2f})'
            })
        
        text_lengths = [len(page.get('text', '')) for page in extracted_text]
        length_std = np.std(text_lengths)
        
        if length_std > np.mean(text_lengths) * 0.5:
            inconsistencies.append({
                'type': 'layout_inconsistency',
                'message': f'High variance in text length across pages (std: {length_std:.0f})'
            })
        
        return inconsistencies
    
    def calculate_trust_score(self, metadata: Dict, metadata_verification: Dict, 
                             logo_results: Dict, signature_results: Dict,
                             forgery_indicators: Dict) -> int:
        """Calculate overall trust score (0-100)"""
        score = 100
        
        if not metadata_verification.get('is_valid'):
            score -= 30
        
        score -= len(metadata_verification.get('issues', [])) * 10
        score -= len(metadata_verification.get('warnings', [])) * 5
        
        if not logo_results.get('detected_logos'):
            score -= 15
        
        if not signature_results.get('detected_signatures'):
            score -= 10
        
        score -= len(forgery_indicators.get('suspicious_patterns', [])) * 8
        score -= len(forgery_indicators.get('inconsistencies', [])) * 5
        
        score -= forgery_indicators.get('confidence', 0) * 20
        
        return max(0, min(100, score))
    
    def verify_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Main verification function"""
        result = {
            'is_forged': False,
            'confidence': 0.0,
            'trust_score': 0,
            'risk_level': 'low',
            'metadata': {},
            'metadata_verification': {},
            'extracted_text': [],
            'logo_detection': {},
            'signature_detection': {},
            'forgery_indicators': {},
            'recommendations': []
        }
        
        try:
            result['metadata'] = self.extract_metadata(pdf_path)
            result['metadata_verification'] = self.verify_metadata(result['metadata'])
            result['extracted_text'] = self.extract_text_with_ocr(pdf_path)
            result['logo_detection'] = self.detect_logos(pdf_path)
            result['signature_detection'] = self.detect_signatures(pdf_path)
            result['forgery_indicators'] = self.detect_forgery_indicators(pdf_path, result['extracted_text'])
            
            result['trust_score'] = self.calculate_trust_score(
                result['metadata'],
                result['metadata_verification'],
                result['logo_detection'],
                result['signature_detection'],
                result['forgery_indicators']
            )
            
            result['confidence'] = 1.0 - (result['trust_score'] / 100.0)
            
            if result['trust_score'] < 50:
                result['risk_level'] = 'critical'
                result['is_forged'] = True
            elif result['trust_score'] < 70:
                result['risk_level'] = 'high'
                result['is_forged'] = True
            elif result['trust_score'] < 85:
                result['risk_level'] = 'medium'
            else:
                result['risk_level'] = 'low'
            
            result['recommendations'] = self._generate_recommendations(result)
            
        except Exception as e:
            result['error'] = str(e)
            result['trust_score'] = 50
            result['risk_level'] = 'medium'
        
        return result
    
    def _generate_recommendations(self, result: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if result['is_forged']:
            recommendations.append('Document shows signs of forgery - verify with issuer')
            recommendations.append('Cross-check registration numbers with official databases')
            recommendations.append('Contact the issuing organization directly')
        else:
            recommendations.append('Document appears legitimate')
            recommendations.append('Still verify with official sources if unsure')
        
        if not result['logo_detection'].get('detected_logos'):
            recommendations.append('No trusted logos detected - manual verification recommended')
        
        if result['metadata_verification'].get('warnings'):
            recommendations.append('Review metadata warnings for potential issues')
        
        if result['forgery_indicators'].get('suspicious_patterns'):
            recommendations.append('Document contains suspicious patterns - review carefully')
        
        return recommendations


def main():
    """Test the PDF verifier"""
    print("=" * 60)
    print("PDF Verification Engine")
    print("=" * 60)
    
    verifier = PDFVerifier()
    
    test_pdf = "sample.pdf"
    if os.path.exists(test_pdf):
        print(f"\nVerifying: {test_pdf}")
        result = verifier.verify_pdf(test_pdf)
        
        print(f"\nTrust Score: {result['trust_score']}/100")
        print(f"Risk Level: {result['risk_level'].upper()}")
        print(f"Is Forged: {result['is_forged']}")
        
        print(f"\nDetected Logos: {result['logo_detection'].get('detected_logos', [])}")
        print(f"Detected Signatures: {result['signature_detection'].get('detected_signatures', [])}")
        
        print(f"\nRecommendations:")
        for rec in result['recommendations']:
            print(f"  - {rec}")
    else:
        print(f"\nTest PDF not found: {test_pdf}")
        print("Place a PDF file named 'sample.pdf' in the current directory to test")


if __name__ == "__main__":
    main()
