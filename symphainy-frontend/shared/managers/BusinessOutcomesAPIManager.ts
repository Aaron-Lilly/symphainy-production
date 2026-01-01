/**
 * Business Outcomes API Manager
 * 
 * Centralizes all Business Outcomes pillar API calls using semantic endpoints.
 * Provides a clean interface for business outcomes operations.
 */

// ============================================
// Business Outcomes API Manager Types
// ============================================

export interface GenerateRoadmapRequest {
  pillar_outputs: Record<string, any>;
  roadmap_options?: any;
  user_id?: string;
}

export interface GenerateRoadmapResponse {
  success: boolean;
  roadmap_id?: string;
  roadmap?: any;
  message?: string;
  error?: string;
}

export interface GeneratePOCProposalRequest {
  pillar_outputs: Record<string, any>;
  proposal_options?: any;
  user_id?: string;
}

export interface GeneratePOCProposalResponse {
  success: boolean;
  proposal_id?: string;
  proposal?: any;
  message?: string;
  error?: string;
}

export interface PillarSummariesResponse {
  success: boolean;
  summaries?: Record<string, any>;
  message?: string;
  error?: string;
}

export interface JourneyVisualizationResponse {
  success: boolean;
  visualization?: any;
  message?: string;
  error?: string;
}

// ============================================
// Business Outcomes API Manager Class
// ============================================

export class BusinessOutcomesAPIManager {
  private baseURL: string;
  private sessionToken: string;

  constructor(sessionToken: string, baseURL?: string) {
    this.sessionToken = sessionToken;
    // Use centralized API config (NO hardcoded values)
    if (baseURL) {
      this.baseURL = baseURL.replace(':8000', '').replace(/\/$/, '');
    } else {
      // Import here to avoid circular dependency issues
      const { getApiUrl } = require('@/shared/config/api-config');
      this.baseURL = getApiUrl();
    }
  }

  // ============================================
  // Strategic Roadmap
  // ============================================

  async generateStrategicRoadmap(request: GenerateRoadmapRequest): Promise<GenerateRoadmapResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/business-outcomes-pillar/generate-strategic-roadmap`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.sessionToken}`,
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        },
        body: JSON.stringify({
          pillar_outputs: request.pillar_outputs,
          roadmap_options: request.roadmap_options,
          user_id: request.user_id
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.message || errorData.error || 'Roadmap generation failed'
        };
      }

      const data = await response.json();
      return {
        success: data.success,
        roadmap_id: data.roadmap_id,
        roadmap: data.roadmap,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('Error generating strategic roadmap:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Roadmap generation failed'
      };
    }
  }

  // ============================================
  // POC Proposal
  // ============================================

  async generatePOCProposal(request: GeneratePOCProposalRequest): Promise<GeneratePOCProposalResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/business-outcomes-pillar/generate-proof-of-concept-proposal`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.sessionToken}`,
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        },
        body: JSON.stringify({
          pillar_outputs: request.pillar_outputs,
          proposal_options: request.proposal_options,
          user_id: request.user_id
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.message || errorData.error || 'POC proposal generation failed'
        };
      }

      const data = await response.json();
      return {
        success: data.success,
        proposal_id: data.proposal_id,
        proposal: data.proposal,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('Error generating POC proposal:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'POC proposal generation failed'
      };
    }
  }

  // ============================================
  // Pillar Summaries
  // ============================================

  async getPillarSummaries(): Promise<PillarSummariesResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/business-outcomes-pillar/get-pillar-summaries`, {
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
          error: errorData.message || errorData.error || 'Failed to get pillar summaries'
        };
      }

      const data = await response.json();
      return {
        success: data.success,
        summaries: data.summaries,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('Error getting pillar summaries:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get pillar summaries'
      };
    }
  }

  // ============================================
  // Journey Visualization
  // ============================================

  async getJourneyVisualization(): Promise<JourneyVisualizationResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/business-outcomes-pillar/get-journey-visualization`, {
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
          error: errorData.message || errorData.error || 'Failed to get journey visualization'
        };
      }

      const data = await response.json();
      return {
        success: data.success,
        visualization: data.visualization,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('Error getting journey visualization:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get journey visualization'
      };
    }
  }
}






