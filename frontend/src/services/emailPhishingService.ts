/**
 * Email Phishing Detection Service
 * Integrates with the backend email phishing detection API
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface HighlightedRegion {
  text: string;
  start: number;
  end: number;
  reason: string;
  severity: string;
}

export interface Explanation {
  type: string;
  message: string;
  severity: string;
}

export interface EmailPhishingResponse {
  is_phishing: boolean;
  confidence: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  trust_score: number;
  probabilities: {
    legitimate: number;
    phishing: number;
  };
  explanations: Explanation[];
  highlighted_regions: HighlightedRegion[];
  linguistic_features?: Record<string, any>;
  recommendations: string[];
  user_id?: number;
  scan_type?: string;
}

export interface BatchEmailPhishingResponse {
  results: EmailPhishingResponse[];
  total: number;
  phishing_count: number;
}

export interface FeatureImportanceResponse {
  features: Record<string, any>;
  importance: Record<string, number>;
}

class EmailPhishingService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = `${API_URL}/api/v1/email-phishing`;
  }

  /**
   * Detect if an email is phishing
   */
  async detectPhishing(emailContent: string, token: string): Promise<EmailPhishingResponse> {
    try {
      const response = await axios.post<EmailPhishingResponse>(
        `${this.baseUrl}/detect`,
        { email_content: emailContent },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error detecting phishing:', error);
      throw error;
    }
  }

  /**
   * Detect phishing for multiple emails
   */
  async batchDetectPhishing(emails: string[], token: string): Promise<BatchEmailPhishingResponse> {
    try {
      const response = await axios.post<BatchEmailPhishingResponse>(
        `${this.baseUrl}/batch-detect`,
        { emails },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error in batch phishing detection:', error);
      throw error;
    }
  }

  /**
   * Get feature importance for email analysis
   */
  async getFeatureImportance(emailContent: string, token: string): Promise<FeatureImportanceResponse> {
    try {
      const response = await axios.post<FeatureImportanceResponse>(
        `${this.baseUrl}/feature-importance`,
        { email_content: emailContent },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error getting feature importance:', error);
      throw error;
    }
  }

  /**
   * Check health of the phishing detection service
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    try {
      const response = await axios.get(`${this.baseUrl}/health`);
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }

  /**
   * Get risk level color for UI
   */
  getRiskLevelColor(riskLevel: string): string {
    switch (riskLevel) {
      case 'critical':
        return '#ef4444'; // red-500
      case 'high':
        return '#f97316'; // orange-500
      case 'medium':
        return '#eab308'; // yellow-500
      case 'low':
        return '#22c55e'; // green-500
      default:
        return '#6b7280'; // gray-500
    }
  }

  /**
   * Get risk level badge color for UI
   */
  getRiskLevelBadgeColor(riskLevel: string): string {
    switch (riskLevel) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  }

  /**
   * Highlight text with explanations
   */
  highlightText(text: string, regions: HighlightedRegion[]): string {
    let highlightedText = text;
    let offset = 0;

    // Sort regions by start position
    const sortedRegions = [...regions].sort((a, b) => a.start - b.start);

    sortedRegions.forEach((region) => {
      const before = highlightedText.substring(0, region.start + offset);
      const match = highlightedText.substring(region.start + offset, region.end + offset);
      const after = highlightedText.substring(region.end + offset);

      const colorClass = this.getSeverityColor(region.severity);
      const highlighted = `<mark class="${colorClass}">${match}</mark>`;
      
      highlightedText = before + highlighted + after;
      offset += highlighted.length - match.length;
    });

    return highlightedText;
  }

  /**
   * Get color class for severity
   */
  getSeverityColor(severity: string): string {
    switch (severity) {
      case 'critical':
        return 'bg-red-200';
      case 'high':
        return 'bg-orange-200';
      case 'medium':
        return 'bg-yellow-200';
      case 'positive':
        return 'bg-green-200';
      default:
        return 'bg-gray-200';
    }
  }
}

export const emailPhishingService = new EmailPhishingService();
