/**
 * Email Phishing Detector Component
 * Provides UI for email phishing detection with Explainable AI
 */

import React, { useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, Loader2, FileText, Info } from 'lucide-react';
import { emailPhishingService, EmailPhishingResponse, HighlightedRegion, Explanation } from '../services/emailPhishingService';
import { useAuth } from '../context/AuthContext';

interface EmailPhishingDetectorProps {
  onResult?: (result: EmailPhishingResponse) => void;
}

export const EmailPhishingDetector: React.FC<EmailPhishingDetectorProps> = ({ onResult }) => {
  const { token } = useAuth();
  const [emailContent, setEmailContent] = useState('');
  const [result, setResult] = useState<EmailPhishingResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDetect = async () => {
    if (!emailContent.trim()) {
      setError('Please enter email content');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const detectionResult = await emailPhishingService.detectPhishing(emailContent, token);
      setResult(detectionResult);
      if (onResult) {
        onResult(detectionResult);
      }
    } catch (err) {
      setError('Failed to detect phishing. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const renderHighlightedText = (text: string, regions: HighlightedRegion[]) => {
    if (!regions || regions.length === 0) {
      return <p className="text-gray-700 whitespace-pre-wrap">{text}</p>;
    }

    const sortedRegions = [...regions].sort((a, b) => a.start - b.start);
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;

    sortedRegions.forEach((region) => {
      // Add text before this region
      if (region.start > lastIndex) {
        parts.push(
          <span key={`before-${region.start}`}>
            {text.substring(lastIndex, region.start)}
          </span>
        );
      }

      // Add highlighted region
      const severityColor = emailPhishingService.getSeverityColor(region.severity);
      parts.push(
        <mark
          key={`highlight-${region.start}`}
          className={`px-1 rounded ${severityColor}`}
          title={region.reason}
        >
          {text.substring(region.start, region.end)}
        </mark>
      );

      lastIndex = region.end;
    });

    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(
        <span key="after">{text.substring(lastIndex)}</span>
      );
    }

    return <p className="text-gray-700 whitespace-pre-wrap">{parts}</p>;
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-2 mb-4">
          <FileText className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold">Email Phishing Detection</h3>
        </div>

        <textarea
          value={emailContent}
          onChange={(e) => setEmailContent(e.target.value)}
          placeholder="Paste email content here (include Subject, From, and Body)..."
          className="w-full h-48 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
        />

        {error && (
          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
            <AlertTriangle className="w-4 h-4" />
            <span>{error}</span>
          </div>
        )}

        <button
          onClick={handleDetect}
          disabled={loading}
          className="mt-4 w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Shield className="w-4 h-4" />
              Detect Phishing
            </>
          )}
        </button>
      </div>

      {/* Results Section */}
      {result && (
        <div className="bg-white rounded-lg shadow-md p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              {result.is_phishing ? (
                <AlertTriangle className="w-6 h-6 text-red-600" />
              ) : (
                <CheckCircle className="w-6 h-6 text-green-600" />
              )}
              <h3 className="text-lg font-semibold">
                {result.is_phishing ? 'Phishing Detected' : 'Legitimate Email'}
              </h3>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium border ${emailPhishingService.getRiskLevelBadgeColor(result.risk_level)}`}
            >
              {result.risk_level.toUpperCase()}
            </span>
          </div>

          {/* Trust Score */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Trust Score</span>
              <span className="text-2xl font-bold">{result.trust_score}/100</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all ${
                  result.trust_score > 70
                    ? 'bg-green-500'
                    : result.trust_score > 40
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
                }`}
                style={{ width: `${result.trust_score}%` }}
              />
            </div>
          </div>

          {/* Confidence */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Confidence</div>
              <div className="text-xl font-bold">{(result.confidence * 100).toFixed(1)}%</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600 mb-1">Phishing Probability</div>
              <div className="text-xl font-bold">{(result.probabilities.phishing * 100).toFixed(1)}%</div>
            </div>
          </div>

          {/* Highlighted Text */}
          {result.highlighted_regions && result.highlighted_regions.length > 0 && (
            <div className="mb-6">
              <div className="flex items-center gap-2 mb-3">
                <Info className="w-4 h-4 text-blue-600" />
                <h4 className="font-semibold">Highlighted Suspicious Regions</h4>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg max-h-64 overflow-y-auto">
                {renderHighlightedText(emailContent, result.highlighted_regions)}
              </div>
            </div>
          )}

          {/* Explanations */}
          {result.explanations && result.explanations.length > 0 && (
            <div className="mb-6">
              <h4 className="font-semibold mb-3">Explanations</h4>
              <div className="space-y-2">
                {result.explanations.map((explanation: Explanation, index: number) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg border ${
                      explanation.severity === 'critical'
                        ? 'bg-red-50 border-red-200'
                        : explanation.severity === 'high'
                        ? 'bg-orange-50 border-orange-200'
                        : explanation.severity === 'positive'
                        ? 'bg-green-50 border-green-200'
                        : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      <span className="text-xs font-medium uppercase px-2 py-1 rounded bg-gray-200">
                        {explanation.type}
                      </span>
                      <span className="text-sm">{explanation.message}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Linguistic Features */}
          {result.linguistic_features && (
            <div className="mb-6">
              <h4 className="font-semibold mb-3">Linguistic Features</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {Object.entries(result.linguistic_features).map(([key, value]) => (
                  <div key={key} className="bg-gray-50 p-3 rounded-lg">
                    <div className="text-xs text-gray-600 capitalize">{key.replace(/_/g, ' ')}</div>
                    <div className="text-lg font-bold">{value}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {result.recommendations && result.recommendations.length > 0 && (
            <div>
              <h4 className="font-semibold mb-3">Recommendations</h4>
              <ul className="space-y-2">
                {result.recommendations.map((recommendation: string, index: number) => (
                  <li key={index} className="flex items-start gap-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    <span>{recommendation}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
