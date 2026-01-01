/**
 * Core WebSocket Client
 * Enhanced WebSocket client with Smart City integration
 */

import { getGlobalConfig } from '../config';

export interface WebSocketConfig {
  url: string;
  reconnectAttempts: number;
  reconnectDelay: number;
  heartbeatInterval: number;
}

export interface WebSocketState {
  isConnected: boolean;
  isConnecting: boolean;
  reconnectAttempts: number;
  lastError: string | null;
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: number;
  sessionId?: string;
}

export class SmartCityWebSocketCore {
  private ws: WebSocket | null = null;
  private config = getGlobalConfig();
  private state: WebSocketState = {
    isConnected: false,
    isConnecting: false,
    reconnectAttempts: 0,
    lastError: null,
  };

  private messageCallbacks: ((message: WebSocketMessage) => void)[] = [];
  private errorCallbacks: ((error: Error) => void)[] = [];
  private connectCallbacks: (() => void)[] = [];
  private disconnectCallbacks: (() => void)[] = [];
  private heartbeatInterval: NodeJS.Timeout | null = null;

  // Connection management
  async connect(): Promise<void> {
    if (this.state.isConnecting || this.state.isConnected) {
      return;
    }

    const wsConfig = this.config.getSection('websocket');
    this.state.isConnecting = true;
    this.state.lastError = null;

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(wsConfig.url);
        
        this.ws.onopen = () => {
          console.log('Smart City WebSocket connected');
          this.state.isConnected = true;
          this.state.isConnecting = false;
          this.state.reconnectAttempts = 0;
          this.startHeartbeat();
          this.connectCallbacks.forEach(callback => callback());
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.messageCallbacks.forEach(callback => callback(message));
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
            this.handleError(new Error('Invalid message format'));
          }
        };

        this.ws.onerror = (error) => {
          console.error('Smart City WebSocket error:', error);
          this.handleError(new Error('WebSocket error'));
          reject(new Error('WebSocket connection failed'));
        };

        this.ws.onclose = () => {
          console.log('Smart City WebSocket disconnected');
          this.state.isConnected = false;
          this.state.isConnecting = false;
          this.stopHeartbeat();
          this.disconnectCallbacks.forEach(callback => callback());
          this.attemptReconnect();
        };

      } catch (error) {
        this.state.isConnecting = false;
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.state.isConnected = false;
    this.state.isConnecting = false;
    this.stopHeartbeat();
  }

  // Message handling
  async sendMessage(message: WebSocketMessage): Promise<void> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected');
    }

    return new Promise((resolve, reject) => {
      try {
        this.ws!.send(JSON.stringify(message));
        resolve();
      } catch (error) {
        reject(error);
      }
    });
  }

  // Event handlers
  onMessage(callback: (message: WebSocketMessage) => void): () => void {
    this.messageCallbacks.push(callback);
    return () => {
      this.messageCallbacks = this.messageCallbacks.filter(cb => cb !== callback);
    };
  }

  onError(callback: (error: Error) => void): () => void {
    this.errorCallbacks.push(callback);
    return () => {
      this.errorCallbacks = this.errorCallbacks.filter(cb => cb !== callback);
    };
  }

  onConnect(callback: () => void): () => void {
    this.connectCallbacks.push(callback);
    return () => {
      this.connectCallbacks = this.connectCallbacks.filter(cb => cb !== callback);
    };
  }

  onDisconnect(callback: () => void): () => void {
    this.disconnectCallbacks.push(callback);
    return () => {
      this.disconnectCallbacks = this.disconnectCallbacks.filter(cb => cb !== callback);
    };
  }

  // State management
  getState(): WebSocketState {
    return { ...this.state };
  }

  isConnected(): boolean {
    return this.state.isConnected;
  }

  // Private methods
  private handleError(error: Error): void {
    this.state.lastError = error.message;
    this.errorCallbacks.forEach(callback => callback(error));
  }

  private attemptReconnect(): void {
    const wsConfig = this.config.getSection('websocket');
    if (this.state.reconnectAttempts < wsConfig.reconnectAttempts) {
      setTimeout(() => {
        this.state.reconnectAttempts++;
        console.log(`Attempting to reconnect (${this.state.reconnectAttempts}/${wsConfig.reconnectAttempts})`);
        this.connect();
      }, wsConfig.reconnectDelay * this.state.reconnectAttempts);
    }
  }

  private startHeartbeat(): void {
    const wsConfig = this.config.getSection('websocket');
    this.heartbeatInterval = setInterval(() => {
      if (this.state.isConnected) {
        this.sendMessage({
          type: 'heartbeat',
          data: { timestamp: Date.now() },
          timestamp: Date.now(),
        });
      }
    }, wsConfig.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
} 