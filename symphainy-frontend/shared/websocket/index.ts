/**
 * WebSocket Management Orchestrator
 * Provides unified access to all WebSocket functionality
 */

// Export core functionality
export { SmartCityWebSocketCore } from './core';
export type { 
  WebSocketConfig, 
  WebSocketState, 
  WebSocketMessage 
} from './core';

// Export Smart City integration
export { SmartCityWebSocketIntegration } from './smart_city_integration';
export type { 
  TrafficCopMessage,
  ArchiveMessage,
  ConductorMessage,
  PostOfficeMessage,
  SmartCityMessage
} from './smart_city_integration';

// Export message queuing
export { MessageQueue } from './message_queue';
export type { 
  QueuedMessage, 
  MessageQueueConfig 
} from './message_queue';

// Export connection management
export { ConnectionManager } from './connection';
export type { 
  ConnectionHealth, 
  ConnectionPoolConfig 
} from './connection';

// Export enhanced WebSocket client
export { EnhancedSmartCityWebSocketClient } from './EnhancedSmartCityWebSocketClient'; 