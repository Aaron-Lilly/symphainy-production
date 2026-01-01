/**
 * Operations API Manager
 * 
 * Centralizes all Operations pillar API calls and operations.
 * Provides a clean interface for all operations-related functionality.
 */

// ============================================
// Operations API Manager Types
// ============================================

export interface SessionElement {
  id: string;
  type: string;
  name: string;
  content: any;
  metadata?: any;
}

export interface SessionResponse {
  valid: boolean;
  elements?: Record<string, SessionElement>;
  error?: string;
}

export interface CoexistenceRequest {
  sessionToken: string;
  sopInputFileUuid: string;
  workflowInputFileUuid: string;
}

export interface CoexistenceResponse {
  status: string;
  message?: string;
  result?: any;
}

export interface WorkflowRequest {
  sopFileUuid: string;
  sessionToken: string;
}

export interface WorkflowResponse {
  status: string;
  message?: string;
  workflow?: any;
}

export interface SOPRequest {
  workflowFileUuid: string;
  sessionToken: string;
}

export interface SOPResponse {
  status: string;
  message?: string;
  sop?: any;
}

// ============================================
// Operations API Manager Class
// ============================================

export class OperationsAPIManager {
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

  /**
   * Authenticated fetch helper that automatically handles token refresh on 401 errors.
   * Updates sessionToken if refresh succeeds.
   */
  private async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    // Import authenticatedFetch dynamically to avoid circular dependencies
    const { authenticatedFetch } = await import('../../lib/utils/tokenRefresh');
    
    const response = await authenticatedFetch(url, {
      ...options,
      token: this.sessionToken,
    });
    
    return response;
  }

  // ============================================
  // Session Management
  // ============================================

  async getSessionElements(): Promise<SessionResponse> {
    try {
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/v1/operations-pillar/session/elements`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ sessionToken: this.sessionToken })
      });

      if (!response.ok) {
        throw new Error(`Failed to get session elements: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting session elements:', error);
      return {
        valid: false,
        error: error instanceof Error ? error.message : 'Failed to get session elements'
      };
    }
  }

  // ============================================
  // Coexistence Analysis
  // ============================================

  async analyzeCoexistence(request: CoexistenceRequest): Promise<CoexistenceResponse> {
    try {
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/v1/operations-pillar/coexistence/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          status: 'error',
          message: errorData.message || 'Coexistence analysis failed'
        };
      }

      const data = await response.json();
      return {
        status: data.status || 'success',
        message: data.message,
        result: data.result
      };
    } catch (error) {
      console.error('Error analyzing coexistence:', error);
      return {
        status: 'error',
        message: error instanceof Error ? error.message : 'Coexistence analysis failed'
      };
    }
  }

  // ============================================
  // Workflow Generation
  // ============================================

  // ============================================
  // SOP Management (Semantic APIs)
  // ============================================

  async createSOP(sopContent: any, options?: any): Promise<SOPResponse> {
    try {
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/v1/operations-pillar/create-standard-operating-procedure`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        },
        body: JSON.stringify({
          sop_content: sopContent,
          ...options
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          status: 'error',
          message: errorData.message || errorData.error || 'SOP creation failed'
        };
      }

      const data = await response.json();
      return {
        status: data.success ? 'success' : 'error',
        message: data.message,
        sop: data.sop || data.standard_operating_procedure
      };
    } catch (error) {
      console.error('Error creating SOP:', error);
      return {
        status: 'error',
        message: error instanceof Error ? error.message : 'SOP creation failed'
      };
    }
  }

  async listSOPs(): Promise<any[]> {
    try {
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/v1/operations-pillar/list-standard-operating-procedures`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to list SOPs: ${response.statusText}`);
      }

      const data = await response.json();
      return data.standard_operating_procedures || data.sops || [];
    } catch (error) {
      console.error('Error listing SOPs:', error);
      throw error;
    }
  }

  // ============================================
  // Workflow Management (Semantic APIs)
  // ============================================

  async createWorkflow(workflowData: any, options?: any): Promise<WorkflowResponse> {
    try {
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/v1/operations-pillar/create-workflow`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        },
        body: JSON.stringify({
          workflow: workflowData,
          ...options
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          status: 'error',
          message: errorData.message || errorData.error || 'Workflow creation failed'
        };
      }

      const data = await response.json();
      return {
        status: data.success ? 'success' : 'error',
        message: data.message,
        workflow: data.workflow
      };
    } catch (error) {
      console.error('Error creating workflow:', error);
      return {
        status: 'error',
        message: error instanceof Error ? error.message : 'Workflow creation failed'
      };
    }
  }

  async listWorkflows(): Promise<any[]> {
    try {
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/v1/operations-pillar/list-workflows`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to list workflows: ${response.statusText}`);
      }

      const data = await response.json();
      return data.workflows || [];
    } catch (error) {
      console.error('Error listing workflows:', error);
      throw error;
    }
  }

  // ============================================
  // Conversion (Semantic APIs)
  // ============================================

  async convertSOPToWorkflow(sopId: string, options?: any): Promise<WorkflowResponse> {
    try {
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/v1/operations-pillar/convert-sop-to-workflow`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        },
        body: JSON.stringify({
          sop_id: sopId,
          sop_file_uuid: sopId,
          sop_content: options?.sop_content,
          conversion_type: 'sop_to_workflow',
          ...options
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          status: 'error',
          message: errorData.message || errorData.error || 'SOP to workflow conversion failed'
        };
      }

      const data = await response.json();
      return {
        status: data.success ? 'success' : 'error',
        message: data.message,
        workflow: data.workflow
      };
    } catch (error) {
      console.error('Error converting SOP to workflow:', error);
      return {
        status: 'error',
        message: error instanceof Error ? error.message : 'SOP to workflow conversion failed'
      };
    }
  }

  async convertWorkflowToSOP(workflowId: string, options?: any): Promise<SOPResponse> {
    try {
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/v1/operations-pillar/convert-workflow-to-sop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        },
        body: JSON.stringify({
          workflow_id: workflowId,
          workflow_file_uuid: workflowId,
          workflow: options?.workflow,
          workflow_content: options?.workflow,
          conversion_type: 'workflow_to_sop',
          ...options
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          status: 'error',
          message: errorData.message || errorData.error || 'Workflow to SOP conversion failed'
        };
      }

      const data = await response.json();
      return {
        status: data.success ? 'success' : 'error',
        message: data.message,
        sop: data.standard_operating_procedure || data.sop
      };
    } catch (error) {
      console.error('Error converting workflow to SOP:', error);
      return {
        status: 'error',
        message: error instanceof Error ? error.message : 'Workflow to SOP conversion failed'
      };
    }
  }

  // ============================================
  // Legacy Methods (for backward compatibility)
  // ============================================

  async generateWorkflowFromSOP(request: WorkflowRequest): Promise<WorkflowResponse> {
    // Use semantic API
    return this.convertSOPToWorkflow(request.sopFileUuid);
  }

  async generateSOPFromWorkflow(request: SOPRequest): Promise<SOPResponse> {
    // Use semantic API
    return this.convertWorkflowToSOP(request.workflowFileUuid);
  }

  // ============================================
  // Process Optimization
  // ============================================

  async optimizeProcess(processId: string, optimizationType: string): Promise<any> {
    try {
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/v1/operations-pillar/process/${processId}/optimize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ optimizationType })
      });

      if (!response.ok) {
        throw new Error(`Process optimization failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error optimizing process:', error);
      throw error;
    }
  }

  // ============================================
  // Compliance Checking
  // ============================================

  async checkCompliance(processId: string, complianceType: string): Promise<any> {
    try {
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/v1/operations-pillar/compliance/check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ processId, complianceType })
      });

      if (!response.ok) {
        throw new Error(`Compliance check failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error checking compliance:', error);
      throw error;
    }
  }

  // ============================================
  // Operations Health
  // ============================================

  async getHealthStatus(): Promise<any> {
    try {
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/v1/operations-pillar/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error checking operations health:', error);
      throw error;
    }
  }
}





























