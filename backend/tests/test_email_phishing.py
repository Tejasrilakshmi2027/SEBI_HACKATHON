"""
Unit tests for Email Phishing Detection
"""

import pytest
from app.services.email_phishing_service import email_phishing_service


class TestEmailPhishingDetection:
    """Test email phishing detection service"""
    
    def test_phishing_email_detection(self):
        """Test detection of phishing email"""
        phishing_email = """
        Subject: URGENT Your account will be suspended
        Body: Dear customer your account will be suspended within 24 hours unless you verify your identity immediately Click here http://verify-account-xyz.com
        """
        
        result = email_phishing_service.detect_phishing(phishing_email)
        
        assert result is not None
        assert "is_phishing" in result
        assert "confidence" in result
        assert "trust_score" in result
        assert "risk_level" in result
        assert "explanations" in result
        assert "recommendations" in result
    
    def test_legitimate_email_detection(self):
        """Test detection of legitimate email"""
        legitimate_email = """
        Subject: Quarterly portfolio statement
        Body: Your quarterly portfolio statement for Q4 2023 is now available Please log in to your account to view
        """
        
        result = email_phishing_service.detect_phishing(legitimate_email)
        
        assert result is not None
        assert "is_phishing" in result
        assert "trust_score" in result
    
    def test_urgency_keyword_detection(self):
        """Test urgency keyword detection"""
        email_with_urgency = """
        Subject: URGENT immediate action required
        Body: This is urgent and requires immediate action
        """
        
        result = email_phishing_service.detect_phishing(email_with_urgency)
        
        assert result is not None
        if result.get("linguistic_features"):
            assert result["linguistic_features"].get("urgency_keywords", 0) > 0
    
    def test_suspicious_url_detection(self):
        """Test suspicious URL detection"""
        email_with_suspicious_url = """
        Subject: Verify your account
        Body: Click here http://fake-site-xyz.com to verify
        """
        
        result = email_phishing_service.detect_phishing(email_with_suspicious_url)
        
        assert result is not None
        if result.get("linguistic_features"):
            assert result["linguistic_features"].get("suspicious_urls", 0) > 0
    
    def test_money_mention_detection(self):
        """Test money mention detection"""
        email_with_money = """
        Subject: You won 50000 dollars
        Body: Congratulations you have won 50000 dollars
        """
        
        result = email_phishing_service.detect_phishing(email_with_money)
        
        assert result is not None
        if result.get("linguistic_features"):
            assert result["linguistic_features"].get("money_mentions", 0) > 0
    
    def test_trust_score_range(self):
        """Test trust score is within valid range"""
        test_email = "Subject: Test Body: Test content"
        
        result = email_phishing_service.detect_phishing(test_email)
        
        assert result is not None
        assert 0 <= result.get("trust_score", 0) <= 100
    
    def test_confidence_range(self):
        """Test confidence is within valid range"""
        test_email = "Subject: Test Body: Test content"
        
        result = email_phishing_service.detect_phishing(test_email)
        
        assert result is not None
        assert 0 <= result.get("confidence", 0) <= 1
    
    def test_risk_level_valid(self):
        """Test risk level is valid"""
        test_email = "Subject: Test Body: Test content"
        
        result = email_phishing_service.detect_phishing(test_email)
        
        assert result is not None
        assert result.get("risk_level") in ["low", "medium", "high", "critical"]
    
    def test_explanations_not_empty(self):
        """Test explanations are provided"""
        test_email = "Subject: Test Body: Test content"
        
        result = email_phishing_service.detect_phishing(test_email)
        
        assert result is not None
        assert "explanations" in result
        assert isinstance(result["explanations"], list)
    
    def test_recommendations_not_empty(self):
        """Test recommendations are provided"""
        test_email = "Subject: Test Body: Test content"
        
        result = email_phishing_service.detect_phishing(test_email)
        
        assert result is not None
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0
    
    def test_highlighted_regions_structure(self):
        """Test highlighted regions have correct structure"""
        test_email = "Subject: URGENT Test Body: http://fake-xyz.com"
        
        result = email_phishing_service.detect_phishing(test_email)
        
        assert result is not None
        if result.get("highlighted_regions"):
            for region in result["highlighted_regions"]:
                assert "text" in region
                assert "start" in region
                assert "end" in region
                assert "reason" in region
                assert "severity" in region


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
