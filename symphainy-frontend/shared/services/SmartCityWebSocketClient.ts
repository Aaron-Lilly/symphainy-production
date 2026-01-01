/**
 * Smart City WebSocket Client
 * Enhanced frontend client for Smart City chat system integration
 * Now uses the enhanced WebSocket functionality
 */

import {
  WebSocketMessage,
  ChatMessage,
  WorkflowRequest,
  WebSocketResponse,
  ChatResponse,
  WorkflowResponse,
  ErrorResponse,
  SmartCityWebSocketClient as ISmartCityWebSocketClient,
  createChatMessage,
  createWorkflowRequest,
  isErrorResponse,
  isChatResponse,
  isWorkflowResponse
} from '../types/smart-city-api';
import { EnhancedSmartCityWebSocketClient } from '../websocket/EnhancedSmartCityWebSocketClient';
import { getGlobalConfig } from '../config';

export class SmartCityWebSocketClient implements ISmartCityWebSocketClient {
  private enhancedClient: EnhancedSmartCityWebSocketClient;
  private config = getGlobalConfig();

  constructor() {
    this.enhancedClient = new EnhancedSmartCityWebSocketClient();
  }

  async connect(): Promise<void> {
    await this.enhancedClient.connect();
  }

  disconnect(): void {
    this.enhancedClient.disconnect();
  }

  async sendMessage(message: WebSocketMessage): Promise<void> {
    await this.enhancedClient.sendMessage(message);
  }

  async sendChatMessage(message: string, session_token: string, file_uuid?: string): Promise<ChatResponse> {
    const chatMessage = createChatMessage(message, session_token, file_uuid);
    
    return new Promise((resolve, reject) => {
      const messageHandler = (response: WebSocketResponse) => {
        if (isChatResponse(response)) {
          this.enhancedClient.onMessage(messageHandler);
          resolve(response);
        } else if (isErrorResponse(response)) {
          this.enhancedClient.onMessage(messageHandler);
          reject(new Error(response.error_code));
        }
      };

      this.enhancedClient.onMessage(messageHandler);
      this.sendMessage(chatMessage).catch(reject);
    });
  }

  async sendWorkflowRequest(workflow_type: string, session_token: string): Promise<WorkflowResponse> {
    const workflowRequest = createWorkflowRequest(workflow_type, session_token);
    
    return new Promise((resolve, reject) => {
      const messageHandler = (response: WebSocketResponse) => {
        if (isWorkflowResponse(response)) {
          this.enhancedClient.onMessage(messageHandler);
          resolve(response);
        } else if (isErrorResponse(response)) {
          this.enhancedClient.onMessage(messageHandler);
          reject(new Error(response.error_code));
        }
      };

      this.enhancedClient.onMessage(messageHandler);
      this.sendMessage(workflowRequest).catch(reject);
    });
  }

  // Event handlers
  onMessage(callback: (response: WebSocketResponse) => void): void {
    this.enhancedClient.onMessage(callback);
  }

  onError(callback: (error: Error) => void): void {
    this.enhancedClient.onError(callback);
  }

  onConnect(callback: () => void): void {
    this.enhancedClient.onConnect(callback);
  }

  onDisconnect(callback: () => void): void {
    this.enhancedClient.onDisconnect(callback);
  }

  isConnected(): boolean {
    return this.enhancedClient.isConnected();
  }

  // Enhanced Smart City functionality
  async routeSession(sessionId: string, destination: string): Promise<void> {
    return this.enhancedClient.routeSession(sessionId, destination);
  }

  async validateSession(sessionId: string): Promise<boolean> {
    return this.enhancedClient.validateSession(sessionId);
  }

  async createSession(sessionData: any): Promise<string> {
    return this.enhancedClient.createSession(sessionData);
  }

  async storeSession(sessionId: string, sessionData: any): Promise<void> {
    return this.enhancedClient.storeSession(sessionId, sessionData);
  }

  async retrieveSession(sessionId: string): Promise<any> {
    return this.enhancedClient.retrieveSession(sessionId);
  }

  async orchestrateSession(sessionId: string, workflow: string): Promise<void> {
    return this.enhancedClient.orchestrateSession(sessionId, workflow);
  }

  async getSessionStatus(sessionId: string): Promise<string> {
    return this.enhancedClient.getSessionStatus(sessionId);
  }

  // Queue management
  getQueueStats() {
    return this.enhancedClient.getQueueStats();
  }

  clearQueue(): void {
    this.enhancedClient.clearQueue();
  }

  // Connection pool management
  async getConnection(connectionId: string) {
    return this.enhancedClient.getConnection(connectionId);
  }

  releaseConnection(connectionId: string): void {
    this.enhancedClient.releaseConnection(connectionId);
  }

  getConnectionHealth(connectionId: string) {
    return this.enhancedClient.getConnectionHealth(connectionId);
  }

  getPoolStats() {
    return this.enhancedClient.getPoolStats();
  }

  // Convenience methods for specific workflows
  async startFileAnalysisWorkflow(session_token: string): Promise<WorkflowResponse> {
    return this.sendWorkflowRequest('file_analysis', session_token);
  }

  async startProcessOptimizationWorkflow(session_token: string): Promise<WorkflowResponse> {
    return this.sendWorkflowRequest('process_optimization', session_token);
  }

  async startStrategicPlanningWorkflow(session_token: string): Promise<WorkflowResponse> {
    return this.sendWorkflowRequest('strategic_planning', session_token);
  }

  // Additional convenience methods
  async getSessionInfo(session_token: string): Promise<ChatResponse> {
    return this.sendChatMessage('get_session_info', session_token);
  }

  async listFiles(session_token: string): Promise<ChatResponse> {
    return this.sendChatMessage('list_files', session_token);
  }

  async uploadFile(session_token: string, file_uuid: string): Promise<ChatResponse> {
    return this.sendChatMessage('upload_file', session_token, file_uuid);
  }

  async analyzeData(session_token: string, file_uuid?: string): Promise<ChatResponse> {
    return this.sendChatMessage('analyze_data', session_token, file_uuid);
  }

  async createVisualization(session_token: string, file_uuid?: string): Promise<ChatResponse> {
    return this.sendChatMessage('create_visualization', session_token, file_uuid);
  }

  async createWorkflow(session_token: string): Promise<ChatResponse> {
    return this.sendChatMessage('create_workflow', session_token);
  }

  async optimizeProcess(session_token: string): Promise<ChatResponse> {
    return this.sendChatMessage('optimize_process', session_token);
  }

  async createStrategicPlan(session_token: string): Promise<ChatResponse> {
    return this.sendChatMessage('create_strategic_plan', session_token);
  }

  async createRoadmap(session_token: string): Promise<ChatResponse> {
    return this.sendChatMessage('create_roadmap', session_token);
  }

  // Cleanup
  shutdown(): void {
    this.enhancedClient.shutdown();
  }
}

// Export instance for backward compatibility
export const smartCityWebSocketClient = new SmartCityWebSocketClient(); 