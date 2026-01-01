/**
 * Simple Service Layer
 * 
 * A completely client-side only service layer that avoids all SSR issues
 * by not importing React or any client-side dependencies at the module level.
 */

// ============================================
// Simple API Service
// ============================================

export class SimpleAPIService {
  private baseURL: string;
  private sessionToken?: string;

  constructor(baseURL?: string, sessionToken?: string) {
    // Use configured API URL (Traefik route on port 80, not :8000)
    // Override via NEXT_PUBLIC_API_URL environment variable
    // Use centralized API config (NO hardcoded values)
    const { getApiUrl } = require('@/shared/config/api-config');
    const apiBaseURL = baseURL || getApiUrl();
    this.baseURL = apiBaseURL.replace(':8000', '').replace(/\/$/, ''); // Remove port 8000 and trailing slash
    this.sessionToken = sessionToken;
  }

  setSessionToken(token: string) {
    this.sessionToken = token;
  }

  private async makeRequest<T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<{ success: boolean; data?: T; error?: string }> {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string>),
      };

      if (this.sessionToken) {
        headers['Authorization'] = `Bearer ${this.sessionToken}`;
      }

      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorText = await response.text();
        return { success: false, error: errorText };
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  async get<T = any>(endpoint: string): Promise<{ success: boolean; data?: T; error?: string }> {
    return this.makeRequest<T>(endpoint, { method: 'GET' });
  }

  async post<T = any>(endpoint: string, body?: any): Promise<{ success: boolean; data?: T; error?: string }> {
    return this.makeRequest<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async put<T = any>(endpoint: string, body?: any): Promise<{ success: boolean; data?: T; error?: string }> {
    return this.makeRequest<T>(endpoint, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T = any>(endpoint: string): Promise<{ success: boolean; data?: T; error?: string }> {
    return this.makeRequest<T>(endpoint, { method: 'DELETE' });
  }
}

// ============================================
// Simple WebSocket Service
// ============================================

export class SimpleWebSocketService {
  private connections: Map<string, WebSocket> = new Map();
  private sessionToken?: string;

  setSessionToken(token: string) {
    this.sessionToken = token;
  }

  async connect(url: string, options: { requireAuth?: boolean; autoReconnect?: boolean } = {}): Promise<string> {
    const connectionId = `conn_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    
    // Only run on client side
    if (typeof window === 'undefined') {
      throw new Error('WebSocket connections can only be established on the client side');
    }

    // Construct WebSocket URL using configured API URL (Traefik route, not :8000)
    // Use environment variables or default to production Traefik route
    // Use centralized API config (NO hardcoded values)
    const { getApiUrl } = require('@/shared/config/api-config');
    const apiBaseURL = getApiUrl();
    const API_URL = apiBaseURL.replace(':8000', '').replace(/\/$/, ''); // Remove port 8000 and trailing slash
    const wsBaseURL = API_URL.replace(/^http/, 'ws');
    const cleanEndpoint = url.startsWith('/') ? url : `/${url}`;
    const tokenParam = this.sessionToken ? `?session_token=${encodeURIComponent(this.sessionToken)}` : '';
    const wsUrl = `${wsBaseURL}${cleanEndpoint}${tokenParam}`;
    const ws = new WebSocket(wsUrl);

    return new Promise((resolve, reject) => {
      ws.onopen = () => {
        this.connections.set(connectionId, ws);
        resolve(connectionId);
      };

      ws.onerror = (error) => {
        reject(new Error(`WebSocket connection failed: ${error}`));
      };

      ws.onclose = () => {
        this.connections.delete(connectionId);
      };
    });
  }

  subscribe(connectionId: string, eventType: string, callback: (message: any) => void) {
    const ws = this.connections.get(connectionId);
    if (!ws) {
      throw new Error(`WebSocket connection ${connectionId} not found`);
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === eventType) {
          callback(data);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
  }

  send(connectionId: string, message: any) {
    const ws = this.connections.get(connectionId);
    if (!ws) {
      throw new Error(`WebSocket connection ${connectionId} not found`);
    }

    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    } else {
      throw new Error(`WebSocket connection ${connectionId} is not open`);
    }
  }

  disconnect(connectionId: string) {
    const ws = this.connections.get(connectionId);
    if (ws) {
      ws.close();
      this.connections.delete(connectionId);
    }
  }

  disconnectAll() {
    this.connections.forEach((ws, connectionId) => {
      ws.close();
    });
    this.connections.clear();
  }

  getConnections() {
    return Array.from(this.connections.keys()).map(id => ({ id, url: 'unknown' }));
  }
}

// ============================================
// Simple Service Layer Manager
// ============================================

export class SimpleServiceLayerManager {
  private apiService: SimpleAPIService;
  private webSocketService: SimpleWebSocketService;
  private sessionToken?: string;

  constructor() {
    this.apiService = new SimpleAPIService();
    this.webSocketService = new SimpleWebSocketService();
  }

  initialize(config: { sessionToken: string }) {
    this.sessionToken = config.sessionToken;
    this.apiService.setSessionToken(config.sessionToken);
    this.webSocketService.setSessionToken(config.sessionToken);
  }

  getAPIService(): SimpleAPIService {
    return this.apiService;
  }

  getWebSocketService(): SimpleWebSocketService {
    return this.webSocketService;
  }

  cleanup() {
    this.webSocketService.disconnectAll();
  }
}

// ============================================
// Global Service Layer Instance
// ============================================

export const simpleServiceLayerManager = new SimpleServiceLayerManager();

// ============================================
// Convenience Functions
// ============================================

export function createSimpleServiceLayer(sessionToken?: string) {
  const manager = new SimpleServiceLayerManager();
  if (sessionToken) {
    manager.initialize({ sessionToken });
  }
  return manager;
}
