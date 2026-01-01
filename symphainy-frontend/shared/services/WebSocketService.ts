/**
 * WebSocket Service
 * 
 * Provides WebSocket connection management with connection pooling,
 * automatic reconnection, message queuing, and session integration.
 * Abstracts WebSocket interactions from components for better
 * maintainability and reliability.
 */

// WebSocketService is a pure service class, no React imports needed

// ============================================
// Types and Interfaces
// ============================================

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: number;
  id?: string;
}

export interface WebSocketConfig {
  baseURL: string;
  reconnectAttempts: number;
  reconnectDelay: number;
  maxReconnectDelay: number;
  heartbeatInterval: number;
  heartbeatTimeout: number;
  messageQueueSize: number;
}

export interface WebSocketConnection {
  id: string;
  url: string;
  ws: WebSocket;
  status: 'connecting' | 'connected' | 'disconnected' | 'error';
  reconnectAttempts: number;
  lastHeartbeat: number;
  messageQueue: WebSocketMessage[];
  eventListeners: Map<string, Set<(message: WebSocketMessage) => void>>;
}

export interface WebSocketError {
  message: string;
  code: string;
  connectionId?: string;
  retryable: boolean;
}

export type WebSocketEventListener = (message: WebSocketMessage) => void;

// ============================================
// WebSocket Service Class
// ============================================

export class WebSocketService {
  private config: WebSocketConfig;
  private connections: Map<string, WebSocketConnection> = new Map();
  private sessionContext?: any; // Will be injected
  private heartbeatTimers: Map<string, NodeJS.Timeout> = new Map();
  private reconnectTimers: Map<string, NodeJS.Timeout> = new Map();

  constructor(config: Partial<WebSocketConfig> = {}) {
    // Use configured API URL (Traefik route, not :8000)
    // Use centralized API config (NO hardcoded values)
    const { getApiUrl } = require('@/shared/config/api-config');
    const apiBaseURL = getApiUrl();
    const API_URL = apiBaseURL.replace(':8000', '').replace(/\/$/, ''); // Remove port 8000 and trailing slash
    const defaultWSURL = API_URL.replace(/^http/, 'ws');
    
    this.config = {
      baseURL: defaultWSURL,
      reconnectAttempts: 5,
      reconnectDelay: 1000,
      maxReconnectDelay: 30000,
      heartbeatInterval: 30000, // 30 seconds
      heartbeatTimeout: 10000, // 10 seconds
      messageQueueSize: 100,
      ...config,
    };
  }

  // ============================================
  // Connection Management
  // ============================================

  async connect(endpoint: string, options: {
    requireAuth?: boolean;
    autoReconnect?: boolean;
    heartbeat?: boolean;
  } = {}): Promise<string> {
    const {
      requireAuth = true,
      autoReconnect = true,
      heartbeat = true,
    } = options;

    const connectionId = this.generateConnectionId(endpoint);
    
    // Check if connection already exists
    if (this.connections.has(connectionId)) {
      const existing = this.connections.get(connectionId)!;
      if (existing.status === 'connected') {
        return connectionId;
      }
      // Clean up existing connection
      this.disconnect(connectionId);
    }

    // Build WebSocket URL
    let url = endpoint.startsWith('ws') ? endpoint : `${this.config.baseURL}${endpoint}`;
    
    // Add authentication if required
    if (requireAuth && this.sessionContext?.sessionState?.globalToken) {
      const separator = url.includes('?') ? '&' : '?';
      url += `${separator}token=${this.sessionContext.sessionState.globalToken}`;
    }

    // Create WebSocket connection
    const ws = new WebSocket(url);
    
    // Create connection object
    const connection: WebSocketConnection = {
      id: connectionId,
      url,
      ws,
      status: 'connecting',
      reconnectAttempts: 0,
      lastHeartbeat: Date.now(),
      messageQueue: [],
      eventListeners: new Map(),
    };

    // Set up event handlers
    this.setupEventHandlers(connection, autoReconnect, heartbeat);
    
    // Store connection
    this.connections.set(connectionId, connection);

    // Wait for connection to establish
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error(`WebSocket connection timeout: ${endpoint}`));
      }, 10000);

      ws.onopen = () => {
        clearTimeout(timeout);
        connection.status = 'connected';
        connection.lastHeartbeat = Date.now();
        
        // Start heartbeat if enabled
        if (heartbeat) {
          this.startHeartbeat(connectionId);
        }
        
        // Process queued messages
        this.processMessageQueue(connectionId);
        
        resolve(connectionId);
      };

      ws.onerror = (error) => {
        clearTimeout(timeout);
        connection.status = 'error';
        reject(new Error(`WebSocket connection error: ${error}`));
      };
    });
  }

  disconnect(connectionId: string): void {
    const connection = this.connections.get(connectionId);
    if (!connection) return;

    // Stop heartbeat and reconnect timers
    this.stopHeartbeat(connectionId);
    this.stopReconnect(connectionId);

    // Close WebSocket
    if (connection.ws.readyState === WebSocket.OPEN) {
      connection.ws.close();
    }

    // Remove connection
    this.connections.delete(connectionId);
  }

  disconnectAll(): void {
    const connectionIds = Array.from(this.connections.keys());
    for (const connectionId of connectionIds) {
      this.disconnect(connectionId);
    }
  }

  // ============================================
  // Message Handling
  // ============================================

  send(connectionId: string, message: WebSocketMessage): Promise<void> {
    const connection = this.connections.get(connectionId);
    if (!connection) {
      throw new Error(`WebSocket connection not found: ${connectionId}`);
    }

    // Add timestamp if not provided
    if (!message.timestamp) {
      message.timestamp = Date.now();
    }

    // Add message ID if not provided
    if (!message.id) {
      message.id = this.generateMessageId();
    }

    // Queue message if not connected
    if (connection.status !== 'connected') {
      this.queueMessage(connectionId, message);
      return Promise.resolve();
    }

    // Send message
    try {
      connection.ws.send(JSON.stringify(message));
      return Promise.resolve();
    } catch (error) {
      // Queue message on send failure
      this.queueMessage(connectionId, message);
      return Promise.reject(error);
    }
  }

  subscribe(connectionId: string, eventType: string, listener: WebSocketEventListener): () => void {
    const connection = this.connections.get(connectionId);
    if (!connection) {
      throw new Error(`WebSocket connection not found: ${connectionId}`);
    }

    if (!connection.eventListeners.has(eventType)) {
      connection.eventListeners.set(eventType, new Set());
    }

    connection.eventListeners.get(eventType)!.add(listener);

    // Return unsubscribe function
    return () => {
      const listeners = connection.eventListeners.get(eventType);
      if (listeners) {
        listeners.delete(listener);
        if (listeners.size === 0) {
          connection.eventListeners.delete(eventType);
        }
      }
    };
  }

  // ============================================
  // Connection Status
  // ============================================

  getConnectionStatus(connectionId: string): string | null {
    const connection = this.connections.get(connectionId);
    return connection?.status || null;
  }

  isConnected(connectionId: string): boolean {
    const connection = this.connections.get(connectionId);
    return connection?.status === 'connected' || false;
  }

  getActiveConnections(): string[] {
    return Array.from(this.connections.keys()).filter(id => 
      this.connections.get(id)?.status === 'connected'
    );
  }

  // ============================================
  // Private Helper Methods
  // ============================================

  private setupEventHandlers(
    connection: WebSocketConnection,
    autoReconnect: boolean,
    heartbeat: boolean
  ): void {
    const { ws, id: connectionId } = connection;

    ws.onopen = () => {
      connection.status = 'connected';
      connection.lastHeartbeat = Date.now();
      connection.reconnectAttempts = 0;
      
      if (heartbeat) {
        this.startHeartbeat(connectionId);
      }
      
      this.processMessageQueue(connectionId);
      this.emitEvent(connectionId, 'connected', { connectionId });
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        connection.lastHeartbeat = Date.now();
        
        // Handle heartbeat responses
        if (message.type === 'heartbeat') {
          return;
        }
        
        // Emit message to listeners
        this.emitEvent(connectionId, message.type, message);
        this.emitEvent(connectionId, 'message', message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onclose = (event) => {
      connection.status = 'disconnected';
      this.stopHeartbeat(connectionId);
      
      this.emitEvent(connectionId, 'disconnected', { 
        connectionId, 
        code: event.code, 
        reason: event.reason 
      });

      // Auto-reconnect if enabled
      if (autoReconnect && connection.reconnectAttempts < this.config.reconnectAttempts) {
        this.scheduleReconnect(connectionId);
      }
    };

    ws.onerror = (error) => {
      connection.status = 'error';
      this.emitEvent(connectionId, 'error', { 
        connectionId, 
        error: error.toString() 
      });
    };
  }

  private emitEvent(connectionId: string, eventType: string, data: any): void {
    const connection = this.connections.get(connectionId);
    if (!connection) return;

    const listeners = connection.eventListeners.get(eventType);
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(data);
        } catch (error) {
          console.error('WebSocket event listener error:', error);
        }
      });
    }
  }

  private queueMessage(connectionId: string, message: WebSocketMessage): void {
    const connection = this.connections.get(connectionId);
    if (!connection) return;

    // Add to queue
    connection.messageQueue.push(message);
    
    // Limit queue size
    if (connection.messageQueue.length > this.config.messageQueueSize) {
      connection.messageQueue.shift();
    }
  }

  private processMessageQueue(connectionId: string): void {
    const connection = this.connections.get(connectionId);
    if (!connection || connection.status !== 'connected') return;

    // Send all queued messages
    while (connection.messageQueue.length > 0) {
      const message = connection.messageQueue.shift()!;
      try {
        connection.ws.send(JSON.stringify(message));
      } catch (error) {
        // Re-queue message on failure
        connection.messageQueue.unshift(message);
        break;
      }
    }
  }

  private startHeartbeat(connectionId: string): void {
    this.stopHeartbeat(connectionId);

    const timer = setInterval(() => {
      const connection = this.connections.get(connectionId);
      if (!connection || connection.status !== 'connected') {
        this.stopHeartbeat(connectionId);
        return;
      }

      // Check if heartbeat is overdue
      const now = Date.now();
      if (now - connection.lastHeartbeat > this.config.heartbeatTimeout) {
        console.warn('WebSocket heartbeat timeout, reconnecting...');
        this.reconnect(connectionId);
        return;
      }

      // Send heartbeat
      this.send(connectionId, {
        type: 'heartbeat',
        data: { timestamp: now },
        timestamp: now,
      }).catch(() => {
        // Heartbeat failed, reconnect
        this.reconnect(connectionId);
      });
    }, this.config.heartbeatInterval);

    this.heartbeatTimers.set(connectionId, timer);
  }

  private stopHeartbeat(connectionId: string): void {
    const timer = this.heartbeatTimers.get(connectionId);
    if (timer) {
      clearInterval(timer);
      this.heartbeatTimers.delete(connectionId);
    }
  }

  private scheduleReconnect(connectionId: string): void {
    this.stopReconnect(connectionId);

    const connection = this.connections.get(connectionId);
    if (!connection) return;

    connection.reconnectAttempts++;
    
    // Calculate delay with exponential backoff
    const delay = Math.min(
      this.config.reconnectDelay * Math.pow(2, connection.reconnectAttempts - 1),
      this.config.maxReconnectDelay
    );

    const timer = setTimeout(() => {
      this.reconnect(connectionId);
    }, delay);

    this.reconnectTimers.set(connectionId, timer);
  }

  private stopReconnect(connectionId: string): void {
    const timer = this.reconnectTimers.get(connectionId);
    if (timer) {
      clearTimeout(timer);
      this.reconnectTimers.delete(connectionId);
    }
  }

  private async reconnect(connectionId: string): Promise<void> {
    const connection = this.connections.get(connectionId);
    if (!connection) return;

    try {
      // Close existing connection
      if (connection.ws.readyState === WebSocket.OPEN) {
        connection.ws.close();
      }

      // Create new connection
      const newWs = new WebSocket(connection.url);
      connection.ws = newWs;
      connection.status = 'connecting';

      // Set up event handlers
      this.setupEventHandlers(connection, true, true);

    } catch (error) {
      console.error('WebSocket reconnection failed:', error);
      connection.status = 'error';
    }
  }

  private generateConnectionId(endpoint: string): string {
    return `ws_${endpoint.replace(/[^a-zA-Z0-9]/g, '_')}_${Date.now()}`;
  }

  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // ============================================
  // Session Integration
  // ============================================

  setSessionContext(sessionContext: any) {
    this.sessionContext = sessionContext;
  }

  // ============================================
  // Configuration Management
  // ============================================

  updateConfig(updates: Partial<WebSocketConfig>) {
    this.config = { ...this.config, ...updates };
  }

  getConfig(): WebSocketConfig {
    return { ...this.config };
  }
}

// ============================================
// Global WebSocket Service Instance
// ============================================

export const webSocketService = new WebSocketService();

// ============================================
// WebSocket Service Export
// ============================================

// webSocketService is already exported above

// ============================================
// Convenience Functions
// ============================================

export async function wsConnect(endpoint: string, options?: {
  requireAuth?: boolean;
  autoReconnect?: boolean;
  heartbeat?: boolean;
}): Promise<string> {
  return webSocketService.connect(endpoint, options);
}

export function wsDisconnect(connectionId: string): void {
  webSocketService.disconnect(connectionId);
}

export function wsSend(connectionId: string, message: WebSocketMessage): Promise<void> {
  return webSocketService.send(connectionId, message);
}

export function wsSubscribe(
  connectionId: string, 
  eventType: string, 
  listener: WebSocketEventListener
): () => void {
  return webSocketService.subscribe(connectionId, eventType, listener);
} 