/**
 * WebSocket Manager
 * 
 * Manages the single WebSocket connection to /smart-chat endpoint.
 * Handles connection, reconnection, and message routing to appropriate agents.
 */


// ============================================
// WebSocket Manager Types
// ============================================

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: number;
  id?: string;
}

export interface AgentMessage {
  message: string;
  session_token: string;
  agent_type: 'guide' | 'content' | 'insights' | 'operations' | 'business-outcomes';
  current_pillar?: string;
  file_context?: any;
}

export interface AgentResponse {
  success: boolean;
  content?: string;
  agent?: string;
  current_pillar?: string;
  suggestions?: string[];
  tenant_id?: string;
  conversation_id?: string;
  intent_type?: string;
  error?: string;
  timestamp?: string;
}

export interface WebSocketConfig {
  baseURL: string;
  reconnectAttempts: number;
  reconnectDelay: number;
  maxReconnectDelay: number;
  heartbeatInterval: number;
  heartbeatTimeout: number;
}

// ============================================
// WebSocket Manager Class
// ============================================

export class WebSocketManager {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private sessionToken: string = '';
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectDelay: number = 1000;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private isConnecting: boolean = false;
  private messageHandlers: Map<string, (response: AgentResponse) => void> = new Map();
  private connectionHandlers: Array<(connected: boolean) => void> = [];

  constructor(config?: Partial<WebSocketConfig>) {
    // Use centralized API config (NO hardcoded values)
    const { getWebSocketUrl } = require('@/shared/config/api-config');
    // Get base WebSocket URL (without token - token will be added when connecting)
    const apiUrl = require('@/shared/config/api-config').getApiUrl();
    const defaultWSURL = apiUrl.replace(/^http/, 'ws');
    
    this.config = {
      baseURL: defaultWSURL,
      reconnectAttempts: 5,
      reconnectDelay: 1000,
      maxReconnectDelay: 30000,
      heartbeatInterval: 30000,
      heartbeatTimeout: 10000,
      ...config
    };
  }

  // ============================================
  // Connection Management
  // ============================================

  async connect(sessionToken: string): Promise<void> {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;
    this.sessionToken = sessionToken;

    try {
      const wsUrl = `${this.config.baseURL}/smart-chat`;
      this.ws = new WebSocket(wsUrl);

      await new Promise<void>((resolve, reject) => {
        if (!this.ws) {
          reject(new Error('WebSocket creation failed'));
          return;
        }

        this.ws.onopen = () => {
          console.log('🔗 WebSocket connected to /smart-chat');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.notifyConnectionHandlers(true);
          resolve();
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(event);
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          this.isConnecting = false;
          this.stopHeartbeat();
          this.notifyConnectionHandlers(false);
          
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };
      });

    } catch (error) {
      this.isConnecting = false;
      throw error;
    }
  }

  disconnect(): void {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.notifyConnectionHandlers(false);
  }

  // ============================================
  // Message Handling
  // ============================================

  async sendMessage(message: AgentMessage): Promise<AgentResponse> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected');
    }

    const messageId = `msg_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    
    return new Promise((resolve, reject) => {
      // Store the handler for this message
      this.messageHandlers.set(messageId, resolve);

      // Send the message
      this.ws!.send(JSON.stringify({
        ...message,
        id: messageId,
        timestamp: Date.now()
      }));

      // Set timeout for response
      setTimeout(() => {
        if (this.messageHandlers.has(messageId)) {
          this.messageHandlers.delete(messageId);
          reject(new Error('Message timeout'));
        }
      }, 30000); // 30 second timeout
    });
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const response: AgentResponse = JSON.parse(event.data);
      
      // If response has an ID, route to specific handler
      if (response.conversation_id) {
        const handler = this.messageHandlers.get(response.conversation_id);
        if (handler) {
          handler(response);
          this.messageHandlers.delete(response.conversation_id);
          return;
        }
      }

      // Otherwise, broadcast to all handlers (for general messages)
      this.messageHandlers.forEach((handler) => {
        handler(response);
      });

    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  // ============================================
  // Agent-Specific Methods
  // ============================================

  async sendToGuideAgent(message: string, currentPillar?: string, fileContext?: any): Promise<AgentResponse> {
    return this.sendMessage({
      message,
      session_token: this.sessionToken,
      agent_type: 'guide',
      current_pillar: currentPillar,
      file_context: fileContext
    });
  }

  async sendToContentAgent(message: string, fileContext?: any): Promise<AgentResponse> {
    return this.sendMessage({
      message,
      session_token: this.sessionToken,
      agent_type: 'content',
      current_pillar: 'content',
      file_context: fileContext
    });
  }

  async sendToInsightsAgent(message: string, fileContext?: any): Promise<AgentResponse> {
    return this.sendMessage({
      message,
      session_token: this.sessionToken,
      agent_type: 'insights',
      current_pillar: 'insights',
      file_context: fileContext
    });
  }

  async sendToOperationsAgent(message: string, fileContext?: any): Promise<AgentResponse> {
    return this.sendMessage({
      message,
      session_token: this.sessionToken,
      agent_type: 'operations',
      current_pillar: 'operations',
      file_context: fileContext
    });
  }

  async sendToExperienceAgent(message: string, fileContext?: any): Promise<AgentResponse> {
    return this.sendMessage({
      message,
      session_token: this.sessionToken,
      agent_type: 'business-outcomes',
      current_pillar: 'business-outcomes',
      file_context: fileContext
    });
  }

  // ============================================
  // Connection Status
  // ============================================

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  onConnectionChange(handler: (connected: boolean) => void): () => void {
    this.connectionHandlers.push(handler);
    return () => {
      const index = this.connectionHandlers.indexOf(handler);
      if (index > -1) {
        this.connectionHandlers.splice(index, 1);
      }
    };
  }

  private notifyConnectionHandlers(connected: boolean): void {
    this.connectionHandlers.forEach(handler => handler(connected));
  }

  // ============================================
  // Heartbeat and Reconnection
  // ============================================

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected()) {
        this.ws!.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
      }
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private scheduleReconnect(): void {
    this.reconnectAttempts++;
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.config.maxReconnectDelay
    );

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      if (this.sessionToken) {
        this.connect(this.sessionToken).catch(console.error);
      }
    }, delay);
  }
}

// ============================================
// Global WebSocket Manager Instance
// ============================================

export const webSocketManager = new WebSocketManager();
