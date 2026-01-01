/**
 * Smart City API Contracts - TypeScript Interfaces
 * Comprehensive type definitions for the Smart City chat system
 */

// ============================================================================
// ENUMS
// ============================================================================

export enum AgentType {
  GUIDE_AGENT = "guide_agent",
  CONTENT_SPECIALIST = "content_specialist",
  INSIGHTS_SPECIALIST = "insights_specialist",
  OPERATIONS_SPECIALIST = "operations_specialist",
  EXPERIENCE_SPECIALIST = "experience_specialist"
}

export enum PillarType {
  GUIDE = "guide",
  CONTENT = "content",
  INSIGHTS = "insights",
  OPERATIONS = "operations",
  EXPERIENCE = "experience"
}

export enum MessageType {
  CHAT_MESSAGE = "chat_message",
  WORKFLOW_REQUEST = "workflow_request",
  WORKFLOW_STATUS = "workflow_status",
  SESSION_REQUEST = "session_request",
  ERROR_MESSAGE = "error_message"
}

export enum ErrorCode {
  INVALID_MESSAGE_FORMAT = "INVALID_MESSAGE_FORMAT",
  SESSION_NOT_FOUND = "SESSION_NOT_FOUND",
  AGENT_NOT_AVAILABLE = "AGENT_NOT_AVAILABLE",
  WORKFLOW_NOT_FOUND = "WORKFLOW_NOT_FOUND",
  FILE_NOT_FOUND = "FILE_NOT_FOUND",
  WEBSOCKET_PROCESSING_ERROR = "WEBSOCKET_PROCESSING_ERROR",
  SERVICE_EXECUTION_ERROR = "SERVICE_EXECUTION_ERROR"
}

// ============================================================================
// WEB SOCKET MESSAGE INTERFACES
// ============================================================================

export interface WebSocketMessage {
  message: string;
  session_token: string;
  file_uuid?: string;
  message_type?: MessageType;
  timestamp?: string;
}

export interface ChatMessage extends WebSocketMessage {
  message_type: MessageType.CHAT_MESSAGE;
}

export interface WorkflowRequest extends WebSocketMessage {
  message_type: MessageType.WORKFLOW_REQUEST;
  workflow_type: string;
}

export interface WorkflowStatusRequest extends WebSocketMessage {
  message_type: MessageType.WORKFLOW_STATUS;
}

export interface SessionRequest extends WebSocketMessage {
  message_type: MessageType.SESSION_REQUEST;
  action: string;
}

// ============================================================================
// WEB SOCKET RESPONSE INTERFACES
// ============================================================================

export interface WebSocketResponse {
  success: boolean;
  content: string;
  agent?: AgentType;
  session_token: string;
  timestamp: string;
}

export interface ChatResponse extends WebSocketResponse {
  current_pillar: PillarType;
  pillar_transition: boolean;
  session_context: SessionContext;
}

export interface WorkflowResponse extends WebSocketResponse {
  workflow_id?: string;
  workflow_type?: string;
  steps?: string[];
  status?: string;
}

export interface ErrorResponse extends WebSocketResponse {
  success: false;
  error_code: ErrorCode;
  error_details: Record<string, any>;
  original_message?: string;
}

// ============================================================================
// SESSION INTERFACES
// ============================================================================

export interface SessionContext {
  pillar_history: PillarHistoryEntry[];
  current_pillar: PillarType;
  session_age: string;
  active_workflow?: string;
  workflow_type?: string;
}

export interface PillarHistoryEntry {
  pillar: PillarType;
  agent: AgentType;
  timestamp: string;
  message: string;
}

export interface SessionData {
  session_token: string;
  user_id: string;
  current_pillar: PillarType;
  pillar_states: Record<string, any>;
  journey_history: any[];
  created_at: string;
  last_activity: string;
  context: Record<string, any>;
}

// ============================================================================
// FILE INTERFACES
// ============================================================================

// FileMetadata is now imported from canonical types
import { FileMetadata } from './file';

export interface FileUploadRequest {
  file_name: string;
  file_type: string;
  file_size: number;
  session_token: string;
}

export interface FileUploadResponse {
  success: boolean;
  file_uuid: string;
  file_url?: string;
  message: string;
}

// ============================================================================
// WORKFLOW INTERFACES
// ============================================================================

export interface WorkflowStep {
  step_id: string;
  step_name: string;
  step_type: string;
  status: string;
  agent: AgentType;
  started_at?: string;
  completed_at?: string;
}

export interface WorkflowData {
  workflow_id: string;
  workflow_type: string;
  session_id: string;
  status: string;
  steps: WorkflowStep[];
  created_at: string;
  updated_at: string;
  data: Record<string, any>;
}

// ============================================================================
// HEALTH CHECK INTERFACES
// ============================================================================

export interface ComponentHealth {
  component: string;
  status: string;
  message?: string;
  last_check: string;
}

export interface SystemHealth {
  overall_status: string;
  components: ComponentHealth[];
  timestamp: string;
  version: string;
}

// ============================================================================
// API CLIENT INTERFACES
// ============================================================================

export interface SmartCityWebSocketClient {
  connect(): Promise<void>;
  disconnect(): void;
  sendMessage(message: WebSocketMessage): Promise<void>;
  onMessage(callback: (response: WebSocketResponse) => void): void;
  onError(callback: (error: Error) => void): void;
  onConnect(callback: () => void): void;
  onDisconnect(callback: () => void): void;
  isConnected(): boolean;
}

export interface SmartCityAPIClient {
  // WebSocket methods
  sendChatMessage(message: string, session_token: string, file_uuid?: string): Promise<ChatResponse>;
  sendWorkflowRequest(workflow_type: string, session_token: string): Promise<WorkflowResponse>;
  getWorkflowStatus(session_token: string): Promise<WorkflowResponse>;
  
  // REST methods
  getSession(session_token: string): Promise<SessionData>;
  createSession(user_id: string): Promise<SessionData>;
  updateSession(session_token: string, updates: Partial<SessionData>): Promise<SessionData>;
  
  // File methods
  uploadFile(file: File, session_token: string): Promise<FileUploadResponse>;
  getFiles(session_token: string): Promise<FileMetadata[]>;
  getFile(file_uuid: string): Promise<FileMetadata>;
  
  // Health methods
  getSystemHealth(): Promise<SystemHealth>;
  getComponentHealth(component: string): Promise<ComponentHealth>;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type SmartCityResponse = ChatResponse | WorkflowResponse | ErrorResponse;

export type WebSocketMessageType = 
  | ChatMessage 
  | WorkflowRequest 
  | WorkflowStatusRequest 
  | SessionRequest;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export function createChatMessage(
  message: string, 
  session_token: string, 
  file_uuid?: string
): ChatMessage {
  return {
    message,
    session_token,
    file_uuid,
    message_type: MessageType.CHAT_MESSAGE,
    timestamp: new Date().toISOString()
  };
}

export function createWorkflowRequest(
  workflow_type: string,
  session_token: string,
  message: string = "Start workflow"
): WorkflowRequest {
  return {
    message,
    session_token,
    message_type: MessageType.WORKFLOW_REQUEST,
    workflow_type,
    timestamp: new Date().toISOString()
  };
}

export function isErrorResponse(response: SmartCityResponse): response is ErrorResponse {
  return !response.success && 'error_code' in response;
}

export function isChatResponse(response: SmartCityResponse): response is ChatResponse {
  return response.success && 'current_pillar' in response;
}

export function isWorkflowResponse(response: SmartCityResponse): response is WorkflowResponse {
  return response.success && ('workflow_id' in response || 'workflow_type' in response);
} 