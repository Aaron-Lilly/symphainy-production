/**
 * Enhanced Smart City WebSocket Client
 * Combines core WebSocket functionality with Smart City integration
 */

import { SmartCityWebSocketCore } from './core';
import { SmartCityWebSocketIntegration } from './smart_city_integration';
import { MessageQueue } from './message_queue';
import { ConnectionManager } from './connection';
import { getGlobalConfig } from '../config';

export class EnhancedSmartCityWebSocketClient {
  private wsCore: SmartCityWebSocketCore;
  private smartCityIntegration: SmartCityWebSocketIntegration;
  private messageQueue: MessageQueue;
  private connectionManager: ConnectionManager;
  private config = getGlobalConfig();

  constructor() {
    this.wsCore = new SmartCityWebSocketCore();
    this.smartCityIntegration = new SmartCityWebSocketIntegration(this.wsCore);
    this.messageQueue = new MessageQueue();
    this.connectionManager = new ConnectionManager();
  }

  // Connection management
  async connect(): Promise<void> {
    await this.wsCore.connect();
  }

  disconnect(): void {
    this.wsCore.disconnect();
  }

  isConnected(): boolean {
    return this.wsCore.isConnected();
  }

  // Message handling with queuing
  async sendMessage(message: any, priority: 'HIGH' | 'NORMAL' | 'LOW' = 'NORMAL'): Promise<void> {
    if (this.wsCore.isConnected()) {
      try {
        await this.wsCore.sendMessage(message);
      } catch (error) {
        // Queue message if sending fails
        this.messageQueue.enqueue(message, priority);
        throw error;
      }
    } else {
      // Queue message if not connected
      this.messageQueue.enqueue(message, priority);
    }
  }

  // Smart City integration methods
  async routeSession(sessionId: string, destination: string): Promise<void> {
    return this.smartCityIntegration.routeSession(sessionId, destination);
  }

  async validateSession(sessionId: string): Promise<boolean> {
    return this.smartCityIntegration.validateSession(sessionId);
  }

  async createSession(sessionData: any): Promise<string> {
    return this.smartCityIntegration.createSession(sessionData);
  }

  async storeSession(sessionId: string, sessionData: any): Promise<void> {
    return this.smartCityIntegration.storeSession(sessionId, sessionData);
  }

  async retrieveSession(sessionId: string): Promise<any> {
    return this.smartCityIntegration.retrieveSession(sessionId);
  }

  async orchestrateSession(sessionId: string, workflow: string): Promise<void> {
    return this.smartCityIntegration.orchestrateSession(sessionId, workflow);
  }

  async getSessionStatus(sessionId: string): Promise<string> {
    return this.smartCityIntegration.getSessionStatus(sessionId);
  }

  async deleteSession(sessionId: string): Promise<void> {
    // For now, just log the deletion
    console.log('Session deleted:', sessionId);
    // In a real implementation, this would call the backend to delete the session
  }

  // Event handlers
  onMessage(callback: (message: any) => void): () => void {
    return this.wsCore.onMessage(callback);
  }

  onError(callback: (error: Error) => void): () => void {
    return this.wsCore.onError(callback);
  }

  onConnect(callback: () => void): () => void {
    return this.wsCore.onConnect(callback);
  }

  onDisconnect(callback: () => void): () => void {
    return this.wsCore.onDisconnect(callback);
  }

  // Queue management
  getQueueStats() {
    return this.messageQueue.getStats();
  }

  clearQueue(): void {
    this.messageQueue.clear();
  }

  // Connection pool management
  async getConnection(connectionId: string) {
    return this.connectionManager.getConnection(connectionId);
  }

  releaseConnection(connectionId: string): void {
    this.connectionManager.releaseConnection(connectionId);
  }

  getConnectionHealth(connectionId: string) {
    return this.connectionManager.getConnectionHealth(connectionId);
  }

  getPoolStats() {
    return this.connectionManager.getPoolStats();
  }

  // Cleanup
  shutdown(): void {
    this.wsCore.disconnect();
    this.messageQueue.clear();
    this.connectionManager.shutdown();
  }
} 