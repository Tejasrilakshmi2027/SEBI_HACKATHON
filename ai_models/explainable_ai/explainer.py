from typing import Dict, List, Any
import json


class ExplainableAI:
    """Explainable AI - highlights suspicious areas and provides explanations."""
    
    def __init__(self):
        self.highlight_colors = {
            'critical': '#FF0000',
            'high': '#FF6600',
            'medium': '#FFCC00',
            'low': '#00CC00'
        }
    
    def explain_analysis(self, analysis_result: Dict[str, Any], scan_type: str) -> Dict[str, Any]:
        """Generate explainable AI output."""
        
        explanations = {
            'suspicious_areas': self._identify_suspicious_areas(analysis_result, scan_type),
            'highlighted_content': self._highlight_suspicious_content(analysis_result, scan_type),
            'feature_importance': self._calculate_feature_importance(analysis_result),
            'decision_path': self._explain_decision_path(analysis_result),
            'visual_explanations': self._generate_visual_explanations(analysis_result, scan_type)
        }
        
        return explanations
    
    def _identify_suspicious_areas(self, analysis_result: Dict[str, Any], scan_type: str) -> List[Dict[str, Any]]:
        """Identify suspicious areas in the content."""
        suspicious_areas = []
        
        checks = analysis_result.get('checks', {})
        
        for check_name, check_data in checks.items():
            if isinstance(check_data, dict):
                risk_score = check_data.get('risk_score', 0.0)
                issues = check_data.get('issues', [])
                
                if risk_score > 0.3 and issues:
                    for issue in issues:
                        suspicious_areas.append({
                            'area': check_name,
                            'issue': issue,
                            'severity': self._get_severity(risk_score),
                            'confidence': risk_score
                        })
        
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        suspicious_areas.sort(key=lambda x: severity_order[x['severity']])
        
        return suspicious_areas
    
    def _get_severity(self, risk_score: float) -> str:
        """Get severity level from risk score."""
        if risk_score >= 0.8:
            return 'critical'
        elif risk_score >= 0.6:
            return 'high'
        elif risk_score >= 0.3:
            return 'medium'
        else:
            return 'low'
    
    def _highlight_suspicious_content(self, analysis_result: Dict[str, Any], scan_type: str) -> Dict[str, Any]:
        """Highlight suspicious content for display."""
        highlights = {}
        
        checks = analysis_result.get('checks', {})
        
        # Email-specific highlights
        if scan_type == 'email':
            highlights = self._highlight_email_content(checks)
        elif scan_type == 'url':
            highlights = self._highlight_url_content(checks)
        elif scan_type == 'pdf':
            highlights = self._highlight_pdf_content(checks)
        elif scan_type == 'image':
            highlights = self._highlight_image_content(checks)
        elif scan_type == 'video':
            highlights = self._highlight_video_content(checks)
        elif scan_type == 'audio':
            highlights = self._highlight_audio_content(checks)
        elif scan_type == 'social_media':
            highlights = self._highlight_social_media_content(checks)
        
        return highlights
    
    def _highlight_email_content(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """Highlight suspicious email content."""
        highlights = {
            'sender': [],
            'subject': [],
            'body': [],
            'links': [],
            'attachments': []
        }
        
        # Highlight sender issues
        sender_check = checks.get('sender_analysis', {})
        if sender_check.get('risk_score', 0) > 0.3:
            highlights['sender'].append({
                'text': sender_check.get('sender', ''),
                'reason': ', '.join(sender_check.get('issues', [])),
                'severity': self._get_severity(sender_check.get('risk_score', 0))
            })
        
        # Highlight subject issues
        subject_check = checks.get('subject_analysis', {})
        if subject_check.get('risk_score', 0) > 0.3:
            highlights['subject'].append({
                'text': subject_check.get('subject', ''),
                'reason': ', '.join(subject_check.get('issues', [])),
                'severity': self._get_severity(subject_check.get('risk_score', 0))
            })
        
        # Highlight suspicious links
        link_check = checks.get('link_analysis', {})
        suspicious_links = link_check.get('links', [])
        link_issues = link_check.get('issues', [])
        
        for i, link in enumerate(suspicious_links):
            if i < len(link_issues):
                highlights['links'].append({
                    'text': link,
                    'reason': link_issues[i],
                    'severity': self._get_severity(link_check.get('risk_score', 0))
                })
        
        return highlights
    
    def _highlight_url_content(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """Highlight suspicious URL content."""
        highlights = {
            'domain': [],
            'ssl': [],
            'whois': []
        }
        
        # Highlight domain issues
        domain_check = checks.get('typosquatting_check', {})
        if domain_check.get('risk_score', 0) > 0.3:
            highlights['domain'].append({
                'reason': ', '.join(domain_check.get('issues', [])),
                'severity': self._get_severity(domain_check.get('risk_score', 0))
            })
        
        # Highlight SSL issues
        ssl_check = checks.get('ssl_check', {})
        if ssl_check.get('risk_score', 0) > 0.3:
            highlights['ssl'].append({
                'has_ssl': ssl_check.get('has_ssl', False),
                'reason': ', '.join(ssl_check.get('issues', [])),
                'severity': self._get_severity(ssl_check.get('risk_score', 0))
            })
        
        return highlights
    
    def _highlight_pdf_content(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """Highlight suspicious PDF content."""
        highlights = {
            'metadata': [],
            'text': [],
            'logos': [],
            'signatures': []
        }
        
        # Highlight metadata issues
        metadata_check = checks.get('metadata_analysis', {})
        if metadata_check.get('risk_score', 0) > 0.3:
            highlights['metadata'].append({
                'reason': ', '.join(metadata_check.get('issues', [])),
                'severity': self._get_severity(metadata_check.get('risk_score', 0))
            })
        
        return highlights
    
    def _highlight_image_content(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """Highlight suspicious image content."""
        highlights = {
            'metadata': [],
            'blur': [],
            'edges': [],
            'faces': []
        }
        
        # Highlight metadata issues
        metadata_check = checks.get('metadata_analysis', {})
        if metadata_check.get('risk_score', 0) > 0.3:
            highlights['metadata'].append({
                'reason': ', '.join(metadata_check.get('issues', [])),
                'severity': self._get_severity(metadata_check.get('risk_score', 0))
            })
        
        # Highlight face issues
        face_check = checks.get('face_analysis', {})
        if face_check.get('risk_score', 0) > 0.3:
            highlights['faces'].append({
                'face_count': face_check.get('face_count', 0),
                'reason': ', '.join(face_check.get('issues', [])),
                'severity': self._get_severity(face_check.get('risk_score', 0))
            })
        
        return highlights
    
    def _highlight_video_content(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """Highlight suspicious video content."""
        highlights = {
            'temporal': [],
            'blinks': [],
            'lip_sync': [],
            'faces': []
        }
        
        # Highlight temporal issues
        temporal_check = checks.get('temporal_consistency', {})
        if temporal_check.get('risk_score', 0) > 0.3:
            highlights['temporal'].append({
                'reason': ', '.join(temporal_check.get('issues', [])),
                'severity': self._get_severity(temporal_check.get('risk_score', 0))
            })
        
        # Highlight blink issues
        blink_check = checks.get('blink_detection', {})
        if blink_check.get('risk_score', 0) > 0.3:
            highlights['blinks'].append({
                'blink_rate': blink_check.get('blink_count', 0) / max(blink_check.get('total_faces', 1), 1),
                'reason': ', '.join(blink_check.get('issues', [])),
                'severity': self._get_severity(blink_check.get('risk_score', 0))
            })
        
        return highlights
    
    def _highlight_audio_content(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """Highlight suspicious audio content."""
        highlights = {
            'pitch': [],
            'noise': [],
            'timbre': []
        }
        
        # Highlight pitch issues
        pitch_check = checks.get('pitch_analysis', {})
        if pitch_check.get('risk_score', 0) > 0.3:
            highlights['pitch'].append({
                'pitch_std': pitch_check.get('pitch_std', 0),
                'reason': ', '.join(pitch_check.get('issues', [])),
                'severity': self._get_severity(pitch_check.get('risk_score', 0))
            })
        
        return highlights
    
    def _highlight_social_media_content(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """Highlight suspicious social media content."""
        highlights = {
            'keywords': [],
            'links': [],
            'urgency': []
        }
        
        # Highlight keyword issues
        keyword_check = checks.get('scam_keyword_analysis', {})
        if keyword_check.get('risk_score', 0) > 0.3:
            highlights['keywords'].append({
                'found_keywords': keyword_check.get('found_keywords', []),
                'reason': ', '.join(keyword_check.get('issues', [])),
                'severity': self._get_severity(keyword_check.get('risk_score', 0))
            })
        
        return highlights
    
    def _calculate_feature_importance(self, analysis_result: Dict[str, Any]) -> Dict[str, float]:
        """Calculate feature importance for the decision."""
        importance = {}
        
        checks = analysis_result.get('checks', {})
        
        for check_name, check_data in checks.items():
            if isinstance(check_data, dict):
                risk_score = check_data.get('risk_score', 0.0)
                importance[check_name] = risk_score
        
        # Normalize to sum to 1
        total = sum(importance.values())
        if total > 0:
            importance = {k: v/total for k, v in importance.items()}
        
        return importance
    
    def _explain_decision_path(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Explain the decision path taken by the AI."""
        decision_path = []
        
        overall_risk = analysis_result.get('risk_score', 0.0)
        
        decision_path.append(f"Overall risk score calculated: {overall_risk:.2f}")
        
        if overall_risk < 0.3:
            decision_path.append("Risk score below low threshold → classified as LOW risk")
        elif overall_risk < 0.6:
            decision_path.append("Risk score in medium range → classified as MEDIUM risk")
        elif overall_risk < 0.8:
            decision_path.append("Risk score in high range → classified as HIGH risk")
        else:
            decision_path.append("Risk score above critical threshold → classified as CRITICAL risk")
        
        # Add check-specific decision points
        checks = analysis_result.get('checks', {})
        for check_name, check_data in checks.items():
            if isinstance(check_data, dict):
                risk_score = check_data.get('risk_score', 0.0)
                if risk_score > 0.5:
                    decision_path.append(f"{check_name} detected significant issues (risk: {risk_score:.2f})")
        
        return decision_path
    
    def _generate_visual_explanations(self, analysis_result: Dict[str, Any], scan_type: str) -> Dict[str, Any]:
        """Generate visual explanations for the analysis."""
        visual_explanations = {
            'charts': [],
            'heatmaps': [],
            'overlays': []
        }
        
        # Generate risk distribution chart data
        checks = analysis_result.get('checks', {})
        risk_distribution = []
        for check_name, check_data in checks.items():
            if isinstance(check_data, dict):
                risk_distribution.append({
                    'check': check_name,
                    'risk_score': check_data.get('risk_score', 0.0)
                })
        
        visual_explanations['charts'].append({
            'type': 'bar',
            'title': 'Risk Distribution by Check',
            'data': risk_distribution
        })
        
        # Generate feature importance chart
        feature_importance = self._calculate_feature_importance(analysis_result)
        importance_data = [
            {'feature': k, 'importance': v} 
            for k, v in feature_importance.items()
        ]
        
        visual_explanations['charts'].append({
            'type': 'pie',
            'title': 'Feature Importance',
            'data': importance_data
        })
        
        return visual_explanations
