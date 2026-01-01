/**
 * Session API Manager
 * 
 * Centralizes all Session API calls using semantic endpoints.
 * Provides a clean interface for session management.
 */

// ============================================
// Session API Manager Types
// ============================================

export interface CreateSessionRequest {
  user_id?: string;
  session_type?: string;
  context?: any;
}

export interface CreateSessionResponse {
  success: boolean;
  session_id?: string;
  session_token?: string;
  user_id?: string;
  created_at?: string;
  message?: string;
  error?: string;
}

export interface SessionDetailsResponse {
  success: boolean;
  session?: any;
  message?: string;
  error?: string;
}

export interface SessionStateResponse {
  success: boolean;
  session_state?: any;
  orchestrator_states?: any;
  message?: string;
  error?: string;
}

// ============================================
// Session API Manager Class
// ============================================

export class SessionAPIManager {
  private baseURL: string;
  private sessionToken: string;

  constructor(sessionToken: string = '', baseURL?: string) {
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
  // Session Creation
  // ============================================

  async createUserSession(request: CreateSessionRequest = {}): Promise<CreateSessionResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/session/create-user-session`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.sessionToken}`,
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken || ''
        },
        body: JSON.stringify({
          user_id: request.user_id,
          session_type: request.session_type || 'mvp',
          context: request.context
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.message || errorData.error || 'Session creation failed'
        };
      }

      const data = await response.json();
      
      // Store session token if provided
      if (data.session_token) {
        this.sessionToken = data.session_token;
        if (typeof window !== 'undefined') {
          sessionStorage.setItem('session_token', data.session_token);
        }
      }

      return {
        success: data.success,
        session_id: data.session_id,
        session_token: data.session_token,
        user_id: data.user_id,
        created_at: data.created_at,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('Error creating session:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Session creation failed'
      };
    }
  }

  // ============================================
  // Session Details
  // ============================================

  async getSessionDetails(sessionId: string): Promise<SessionDetailsResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/session/get-session-details/${sessionId}`, {
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
          error: errorData.message || errorData.error || 'Failed to get session details'
        };
      }

      const data = await response.json();
      return {
        success: data.success,
        session: data.session,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('Error getting session details:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get session details'
      };
    }
  }

  // ============================================
  // Session State
  // ============================================

  async getSessionState(sessionId: string): Promise<SessionStateResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/session/get-session-state/${sessionId}`, {
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
          error: errorData.message || errorData.error || 'Failed to get session state'
        };
      }

      const data = await response.json();
      return {
        success: data.success,
        session_state: data.session_state,
        orchestrator_states: data.orchestrator_states,
        message: data.message,
        error: data.error
      };
    } catch (error) {
      console.error('Error getting session state:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get session state'
      };
    }
  }

  // ============================================
  // Session Token Management
  // ============================================

  setSessionToken(token: string): void {
    this.sessionToken = token;
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('session_token', token);
    }
  }

  getSessionToken(): string {
    if (!this.sessionToken && typeof window !== 'undefined') {
      this.sessionToken = sessionStorage.getItem('session_token') || '';
    }
    return this.sessionToken;
  }
}






