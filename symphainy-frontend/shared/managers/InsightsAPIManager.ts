/**
 * Insights API Manager
 * 
 * Centralizes all Insights pillar API calls using semantic endpoints.
 * Provides a clean interface for insights analysis operations.
 */

// ============================================
// Insights API Manager Types
// ============================================

export type AnalysisType = 'quick' | 'comprehensive' | 'detailed';

export interface AnalyzeContentRequest {
  file_ids: string[];
  analysis_type?: AnalysisType;
  focus_areas?: string[];  // ["trends", "anomalies", "recommendations"]
  user_id?: string;
}

export interface AnalyzeContentResponse {
  success: boolean;
  analysis_id?: string;
  key_findings?: any[];
  recommendations?: any[];
  visualizations?: any;
  confidence_score?: number;
  message?: string;
  error?: string;
}

export interface AnalysisResultsResponse {
  success: boolean;
  analysis?: any;
  findings?: any[];
  recommendations?: any[];
  message?: string;
  error?: string;
}

export interface VisualizationsResponse {
  success: boolean;
  visualizations?: any;
  message?: string;
  error?: string;
}

// ============================================
// Insights API Manager Class
// ============================================

export class InsightsAPIManager {
  private baseURL: string;
  private sessionToken: string;

  constructor(sessionToken: string, baseURL?: string) {
    // Use centralized API config (NO hardcoded values)
    if (!baseURL) {
      const { getApiUrl } = require('@/shared/config/api-config');
      baseURL = getApiUrl();
    } else {
      baseURL = baseURL.replace(':8000', '').replace(/\/$/, '');
    }
    this.sessionToken = sessionToken;
    this.baseURL = baseURL;
  }

  // ============================================
  // Content Analysis
  // ============================================

  async analyzeContentForInsights(request: AnalyzeContentRequest): Promise<AnalyzeContentResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/insights-pillar/analyze-content`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.sessionToken}`,
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        },
        body: JSON.stringify({
          file_ids: request.file_ids,
          analysis_type: request.analysis_type || 'comprehensive',
          focus_areas: request.focus_areas,
          user_id: request.user_id
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.message || errorData.error || 'Content analysis failed'
        };
      }

      const data = await response.json();
      return {
        success: data.success,
        analysis_id: data.analysis_id,
        key_findings: data.key_findings,
        recommendations: data.recommendations,
        visualizations: data.visualizations,
        confidence_score: data.confidence_score,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('Error analyzing content for insights:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Content analysis failed'
      };
    }
  }

  // ============================================
  // Analysis Results
  // ============================================

  async getAnalysisResults(analysisId: string): Promise<AnalysisResultsResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/insights-pillar/analysis-results/${analysisId}`, {
        headers: {
          'Authorization': `Bearer ${this.sessionToken}`,
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.message || errorData.error || 'Failed to get analysis results'
        };
      }

      const data = await response.json();
      return {
        success: data.success,
        analysis: data.analysis,
        findings: data.findings,
        recommendations: data.recommendations,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('Error getting analysis results:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get analysis results'
      };
    }
  }

  // ============================================
  // Visualizations
  // ============================================

  async getVisualizations(analysisId: string): Promise<VisualizationsResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/insights-pillar/analysis-visualizations/${analysisId}`, {
        headers: {
          'Authorization': `Bearer ${this.sessionToken}`,
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.message || errorData.error || 'Failed to get visualizations'
        };
      }

      const data = await response.json();
      return {
        success: data.success,
        visualizations: data.visualizations,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('Error getting visualizations:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get visualizations'
      };
    }
  }
}






