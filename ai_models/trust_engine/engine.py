from typing import Dict, List, Any
from app.models.scan import RiskLevel


class TrustEngine:
    """Trust Intelligence Engine - computes trust scores and risk levels."""
    
    def __init__(self):
        # Risk level thresholds
        self.risk_thresholds = {
            RiskLevel.low: 0.3,
            RiskLevel.medium: 0.6,
            RiskLevel.high: 0.8,
            RiskLevel.critical: 0.9
        }
        
        # Legitimate sources (for verification)
        self.legitimate_sources = {
            'sebi.gov.in': 0.95,
            'nseindia.com': 0.95,
            'bseindia.com': 0.95,
            'rbi.org.in': 0.95,
            'mca.gov.in': 0.90
        }
    
    async def compute_trust_score(self, analysis_result: Dict[str, Any], scan_type: str) -> Dict[str, Any]:
        """Compute trust score based on analysis results."""
        
        # Extract risk score from analysis
        risk_score = analysis_result.get('risk_score', 0.0)
        
        # Convert risk score to trust score (inverse relationship)
        trust_score = (1 - risk_score) * 100
        
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)
        
        # Calculate confidence
        confidence = self._calculate_confidence(analysis_result)
        
        # Generate reasons
        reasons = self._generate_reasons(analysis_result, risk_score)
        
        # Generate evidence
        evidence = self._generate_evidence(analysis_result)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, scan_type)
        
        return {
            'trust_score': round(trust_score, 2),
            'risk_level': risk_level,
            'confidence': round(confidence, 2),
            'reasons': reasons,
            'evidence': evidence,
            'recommendations': recommendations,
            'analysis_result': analysis_result
        }
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on risk score."""
        if risk_score >= self.risk_thresholds[RiskLevel.critical]:
            return RiskLevel.critical
        elif risk_score >= self.risk_thresholds[RiskLevel.high]:
            return RiskLevel.high
        elif risk_score >= self.risk_thresholds[RiskLevel.medium]:
            return RiskLevel.medium
        else:
            return RiskLevel.low
    
    def _calculate_confidence(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate confidence in the analysis."""
        
        # Base confidence
        confidence = 0.8
        
        # Adjust based on number of checks performed
        checks = analysis_result.get('checks', {})
        check_count = len(checks)
        
        if check_count >= 5:
            confidence += 0.1
        elif check_count < 3:
            confidence -= 0.2
        
        # Adjust based on consistency of results
        risk_scores = []
        for check_name, check_data in checks.items():
            if isinstance(check_data, dict) and 'risk_score' in check_data:
                risk_scores.append(check_data['risk_score'])
        
        if risk_scores:
            score_std = (sum((x - sum(risk_scores)/len(risk_scores))**2 for x in risk_scores) / len(risk_scores))**0.5
            if score_std < 0.2:
                confidence += 0.1
            elif score_std > 0.4:
                confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_reasons(self, analysis_result: Dict[str, Any], risk_score: float) -> List[str]:
        """Generate reasons for the trust score."""
        reasons = []
        
        checks = analysis_result.get('checks', {})
        
        # Collect issues from all checks
        for check_name, check_data in checks.items():
            if isinstance(check_data, dict):
                issues = check_data.get('issues', [])
                for issue in issues:
                    reasons.append(f"{check_name}: {issue}")
        
        # Add summary reason
        if risk_score < 0.3:
            reasons.append("Overall analysis indicates low risk")
        elif risk_score < 0.6:
            reasons.append("Overall analysis indicates moderate risk")
        elif risk_score < 0.8:
            reasons.append("Overall analysis indicates high risk")
        else:
            reasons.append("Overall analysis indicates critical risk")
        
        return reasons
    
    def _generate_evidence(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate evidence for the analysis."""
        evidence = []
        
        checks = analysis_result.get('checks', {})
        
        for check_name, check_data in checks.items():
            if isinstance(check_data, dict):
                # Extract key metrics as evidence
                for key, value in check_data.items():
                    if key not in ['issues', 'risk_score'] and isinstance(value, (int, float)):
                        evidence.append({
                            'check': check_name,
                            'metric': key,
                            'value': value,
                            'type': 'metric'
                        })
        
        return evidence
    
    def _generate_recommendations(self, risk_level: RiskLevel, scan_type: str) -> List[str]:
        """Generate recommendations based on risk level."""
        recommendations = []
        
        if risk_level == RiskLevel.low:
            recommendations.append("Content appears legitimate")
            recommendations.append("No immediate action required")
            recommendations.append("Continue monitoring for any changes")
        
        elif risk_level == RiskLevel.medium:
            recommendations.append("Exercise caution with this content")
            recommendations.append("Verify the source independently")
            recommendations.append("Cross-check with official channels")
        
        elif risk_level == RiskLevel.high:
            recommendations.append("This content shows signs of manipulation")
            recommendations.append("Do not act on this content without verification")
            recommendations.append("Report to appropriate authorities if applicable")
            recommendations.append("Contact official sources for confirmation")
        
        elif risk_level == RiskLevel.critical:
            recommendations.append("CRITICAL: This content is likely fraudulent")
            recommendations.append("Do not engage with this content")
            recommendations.append("Report immediately to SEBI/cybercrime authorities")
            recommendations.append("Share this information with relevant stakeholders")
            recommendations.append("Block the source if possible")
        
        # Add type-specific recommendations
        if scan_type == 'email':
            recommendations.append("Verify sender email domain carefully")
            recommendations.append("Check email headers for spoofing")
        elif scan_type == 'url':
            recommendations.append("Do not click on suspicious links")
            recommendations.append("Verify URL with official sources")
        elif scan_type == 'pdf':
            recommendations.append("Verify document authenticity with issuer")
            recommendations.append("Check for digital signatures")
        elif scan_type in ['image', 'video']:
            recommendations.append("Be aware of deepfake technology")
            recommendations.append("Cross-reference with trusted sources")
        
        return recommendations
    
    def verify_legitimate_source(self, domain: str) -> Dict[str, Any]:
        """Verify if a domain is a legitimate source."""
        domain_lower = domain.lower()
        
        if domain_lower in self.legitimate_sources:
            return {
                'is_legitimate': True,
                'trust_score': self.legitimate_sources[domain_lower],
                'source': domain_lower
            }
        
        # Check for subdomains of legitimate sources
        for legit_domain, score in self.legitimate_sources.items():
            if domain_lower.endswith('.' + legit_domain):
                return {
                    'is_legitimate': True,
                    'trust_score': score * 0.9,  # Slightly lower for subdomains
                    'source': legit_domain,
                    'subdomain': domain_lower
                }
        
        return {
            'is_legitimate': False,
            'trust_score': 0.0,
            'source': 'unknown'
        }
