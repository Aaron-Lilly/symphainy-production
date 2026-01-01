/**
 * Insights Service Core
 * Core insights service functionality for analysis and session management
 */

// import { config } from '../../../config';
import { 
  InsightsSessionResponse,
  InsightsAnalysisResponse,
  InsightsSummaryResponse,
  VARKInsightsRequest,
  BusinessSummaryRequest,
  CrossPillarIntegrationRequest,
  SmartCityInsightsRequest,
  AGUIEvent,
  FileUrlRequest,
  LearningStyleType,
  DataMappingResponse,
  DataMappingResultsResponse,
  DataMappingOptions
} from './types';

import { getApiEndpointUrl } from '@/shared/config/api-config';

// Use centralized API config (NO hardcoded values)
const API_BASE = getApiEndpointUrl('/api/v1/insights-solution'); // Solution orchestrator endpoints

// Helper to create standardized authenticated headers
const getAuthHeaders = (token?: string, sessionToken?: string) => {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  
  if (sessionToken) {
    headers["X-Session-Token"] = sessionToken;
  }
  
  return headers;
};

export class InsightsService {
  private token?: string;

  constructor(token?: string) {
    this.token = token;
  }

  async startInsightsSession(
    fileUuid: string,
    userId?: string,
    sessionToken?: string
  ): Promise<InsightsSessionResponse> {
    const res = await fetch(`${API_BASE}/session/start`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        file_uuid: fileUuid,
        user_id: userId,
        session_token: sessionToken,
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to start insights session: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  async getInsightsSessionState(
    sessionId: string,
    sessionToken?: string
  ): Promise<InsightsSessionResponse> {
    const params = new URLSearchParams();
    if (sessionToken) params.append('session_token', sessionToken);
    
    const res = await fetch(`${API_BASE}/session/${sessionId}/state?${params.toString()}`, {
      headers: getAuthHeaders(this.token, sessionToken),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to get session state: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  /**
   * Get EDA Analysis using new solution orchestrator endpoint.
   * 
   * @param fileId - File identifier (from Content Pillar)
   * @param analysisOptions - Optional analysis configuration
   * @param sessionToken - Optional session token
   */
  async getEDAAnalysis(
    fileId: string,
    analysisOptions?: Record<string, any>,
    sessionToken?: string
  ): Promise<InsightsAnalysisResponse> {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        file_id: fileId,
        analysis_type: "eda",
        analysis_options: analysisOptions || {},
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to get EDA analysis: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }
  
  // REMOVED: Legacy methods - All insights operations must use insights-solution endpoints

  async getVisualizationAnalysis(
    fileUrl: string,
    sessionId: string,
    additionalInfo?: string,
    sessionToken?: string
  ): Promise<InsightsAnalysisResponse> {
    const res = await fetch(`${API_BASE}/analysis/visualization`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        file_url: fileUrl,
        session_id: sessionId,
        additional_info: additionalInfo,
        session_token: sessionToken,
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to get visualization analysis: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  async getAnomalyDetectionAnalysis(
    fileUrl: string,
    sessionId: string,
    additionalInfo?: string,
    sessionToken?: string
  ): Promise<InsightsAnalysisResponse> {
    const res = await fetch(`${API_BASE}/analysis/anomaly-detection`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        file_url: fileUrl,
        session_id: sessionId,
        additional_info: additionalInfo,
        session_token: sessionToken,
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to get anomaly detection: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  /**
   * Get Business Summary Analysis using new solution orchestrator endpoint.
   */
  async getBusinessAnalysis(
    fileId: string,
    analysisOptions?: Record<string, any>,
    sessionToken?: string
  ): Promise<InsightsAnalysisResponse> {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        file_id: fileId,
        analysis_type: "business_summary",
        analysis_options: analysisOptions || {},
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to get business analysis: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }
  
  /**
   * Get Unstructured Analysis using new solution orchestrator endpoint.
   */
  async getUnstructuredAnalysis(
    fileId: string,
    analysisOptions?: Record<string, any>,
    sessionToken?: string
  ): Promise<InsightsAnalysisResponse> {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        file_id: fileId,
        analysis_type: "unstructured",
        analysis_options: analysisOptions || {},
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to get unstructured analysis: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }
  
  /**
   * Get VARK Analysis using new solution orchestrator endpoint.
   */
  async getVARKAnalysis(
    fileId: string,
    analysisOptions?: Record<string, any>,
    sessionToken?: string
  ): Promise<InsightsAnalysisResponse> {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        file_id: fileId,
        analysis_type: "vark",
        analysis_options: analysisOptions || {},
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to get VARK analysis: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  async generateInsightsSummary(
    sessionId: string,
    additionalInfo?: string,
    sessionToken?: string
  ): Promise<InsightsAnalysisResponse> {
    const res = await fetch(`${API_BASE}/summary/generate`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        session_id: sessionId,
        additional_info: additionalInfo,
        session_token: sessionToken,
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to generate summary: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  async processNaturalLanguageQuery({
    sessionId,
    query,
    fileUrl,
    context,
    sessionToken,
  }: {
    sessionId: string;
    query: string;
    fileUrl?: string;
    context?: any;
    sessionToken?: string;
  }): Promise<InsightsAnalysisResponse> {
    const res = await fetch(`${API_BASE}/query/natural-language`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        session_id: sessionId,
        query,
        file_url: fileUrl,
        context,
        session_token: sessionToken,
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to process query: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  async processChatMessage({
    sessionId,
    message,
    context,
    sessionToken,
  }: {
    sessionId: string;
    message: string;
    context?: any;
    sessionToken?: string;
  }): Promise<InsightsAnalysisResponse> {
    const res = await fetch(`${API_BASE}/chat/message`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        session_id: sessionId,
        message,
        context,
        session_token: sessionToken,
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to process chat message: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  async handleAGUIEvent(event: AGUIEvent): Promise<InsightsAnalysisResponse> {
    const res = await fetch(`${API_BASE}/agui/event`, {
      method: "POST",
      headers: getAuthHeaders(this.token, event.session_token),
      body: JSON.stringify(event),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to handle AGUI event: ${res.status} ${res.statusText}`);
    }
    
    return await res.json();
  }

  /**
   * Execute data mapping operation
   * Maps data from source file to target file using AI-powered field extraction and transformation
   * 
   * Backend returns the complete mapping result directly (no separate polling needed for MVP)
   * 
   * @param sourceFileId - Source file identifier (from Content Pillar)
   * @param targetFileId - Target file identifier (from Content Pillar)
   * @param mappingOptions - Optional mapping configuration
   * @param sessionToken - Optional session token
   */
  async executeDataMapping(
    sourceFileId: string,
    targetFileId: string,
    mappingOptions?: DataMappingOptions,
    sessionToken?: string
  ): Promise<DataMappingResponse> {
    const res = await fetch(`${API_BASE}/mapping`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        source_file_id: sourceFileId,
        target_file_id: targetFileId,
        mapping_options: mappingOptions || {},
      }),
    });
    
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`Failed to execute data mapping: ${res.status} ${res.statusText} - ${errorText}`);
    }
    
    return await res.json();
  }

  /**
   * Get mapping results
   * NOTE: Backend returns results directly in executeDataMapping response
   * This method is kept for future use if backend implements result storage/retrieval
   * 
   * @param mappingId - Mapping operation identifier
   * @param sessionToken - Optional session token
   */
  async getMappingResults(
    mappingId: string,
    sessionToken?: string
  ): Promise<DataMappingResultsResponse> {
    // TODO: Backend may implement this endpoint in the future
    // For now, results are returned directly from executeDataMapping
    throw new Error("getMappingResults not yet supported. Results are returned directly from executeDataMapping.");
  }

  /**
   * Export mapping results
   * Exports the mapped data in the specified format
   * 
   * @param mappingId - Mapping operation identifier
   * @param outputFormat - Output format (excel, json, csv)
   * @param sessionToken - Optional session token
   */
  async exportMappingResults(
    mappingId: string,
    outputFormat: "excel" | "json" | "csv" = "excel",
    sessionToken?: string
  ): Promise<Blob> {
    const res = await fetch(`${API_BASE}/mapping/${mappingId}/export`, {
      method: "POST",
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify({
        output_format: outputFormat,
      }),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to export mapping results: ${res.status} ${res.statusText}`);
    }
    
    return await res.blob();
  }
} 