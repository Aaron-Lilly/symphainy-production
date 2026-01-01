/**
 * useLiaisonChat Hook
 * 
 * ⚠️ DEPRECATED: This hook is deprecated and will be removed in a future release.
 * 
 * Migration Guide:
 * Use `useUnifiedAgentChat({ initialAgent: 'liaison', initialPillar: pillar })` from `@/shared/hooks/useUnifiedAgentChat`
 * 
 * Example migration:
 * ```typescript
 * // Old:
 * const { messages, sendMessage } = useLiaisonChat('insights', { sessionToken });
 * 
 * // New:
 * const { messages, sendMessage } = useUnifiedAgentChat({
 *   sessionToken,
 *   initialAgent: 'liaison',
 *   initialPillar: 'insights'
 * });
 * ```
 * 
 * The unified hook provides:
 * - Single WebSocket connection for all agents (Guide + Liaison)
 * - Better resource efficiency
 * - Agent switching without reconnection
 * - Conversation history management
 * 
 * Phase 5: Unified WebSocket Architecture - Replaced by useUnifiedAgentChat
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { webSocketService, WebSocketMessage } from '../services/WebSocketService';

export type PillarType = 'content' | 'insights' | 'operations' | 'business_outcomes';

export interface LiaisonChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  pillar?: PillarType;
  metadata?: {
    agent_type?: string;
    session_id?: string;
    intent?: any;
  };
}

export interface UseLiaisonChatReturn {
  messages: LiaisonChatMessage[];
  sendMessage: (message: string) => Promise<void>;
  connected: boolean;
  isLoading: boolean;
  error: string | null;
  clearMessages: () => void;
}

export interface UseLiaisonChatOptions {
  sessionToken?: string;
  autoConnect?: boolean;
  onMessage?: (message: LiaisonChatMessage) => void;
  onError?: (error: string) => void;
}

export function useLiaisonChat(
  pillar: PillarType,
  options: UseLiaisonChatOptions = {}
): UseLiaisonChatReturn {
  const {
    sessionToken,
    autoConnect = true,
    onMessage,
    onError
  } = options;

  const [messages, setMessages] = useState<LiaisonChatMessage[]>([]);
  const [connected, setConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const connectionIdRef = useRef<string | null>(null);
  const unsubscribeRef = useRef<(() => void) | null>(null);

  // Connect to Liaison Agent WebSocket
  const connect = useCallback(async () => {
    if (!sessionToken) {
      setError("Session token required");
      return;
    }

    if (connectionIdRef.current) {
      // Already connected
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // Build WebSocket URL with session token
      const endpoint = `/api/ws/liaison/${pillar}?session_token=${sessionToken}`;
      
      // Connect via WebSocketService
      const connectionId = await webSocketService.connect(endpoint, {
        requireAuth: false, // Token is in query param
        autoReconnect: true,
        heartbeat: true
      });

      connectionIdRef.current = connectionId;
      setConnected(true);

      // Subscribe to messages
      const unsubscribe = webSocketService.subscribe(connectionId, 'message', (wsMessage: WebSocketMessage) => {
        try {
          // Backend sends: { type: "chat_response", agent_type: "liaison", pillar: "...", message: "...", ... }
          const response = typeof wsMessage.data === 'string' ? JSON.parse(wsMessage.data) : wsMessage.data;

          // Handle conversation restoration
          if (response.type === 'conversation_restored' && response.messages) {
            const restoredMessages: LiaisonChatMessage[] = response.messages.map((msg: any, index: number) => ({
              id: `restored-${index}`,
              role: msg.role || 'assistant',
              content: msg.content || msg.message || '',
              timestamp: new Date(msg.timestamp || Date.now()),
              pillar: pillar,
              metadata: {
                agent_type: response.agent_type,
                session_id: response.session_id
              }
            }));
            setMessages(restoredMessages);
            return;
          }

          // Handle chat response
          if (response.type === 'chat_response' && response.agent_type === 'liaison') {
            const assistantMessage: LiaisonChatMessage = {
              id: `msg-${Date.now()}`,
              role: 'assistant',
              content: response.message || 'Response received',
              timestamp: new Date(),
              pillar: pillar,
              metadata: {
                agent_type: response.agent_type,
                session_id: response.session_id,
                intent: response.intent
              }
            };

            setMessages(prev => [...prev, assistantMessage]);
            
            if (onMessage) {
              onMessage(assistantMessage);
            }
          } else if (response.type === 'error') {
            const errorMsg = response.message || 'Error from Liaison Agent';
            setError(errorMsg);
            if (onError) {
              onError(errorMsg);
            }
          }
        } catch (parseError) {
          console.error('Error parsing Liaison Agent message:', parseError);
          setError('Error parsing message');
        }
      });

      unsubscribeRef.current = unsubscribe;

      // Subscribe to connection events
      webSocketService.subscribe(connectionId, 'connected', () => {
        setConnected(true);
        setIsLoading(false);
      });

      webSocketService.subscribe(connectionId, 'disconnected', () => {
        setConnected(false);
      });

      webSocketService.subscribe(connectionId, 'error', (errorMsg: any) => {
        setError(errorMsg.error || 'WebSocket error');
        setConnected(false);
        setIsLoading(false);
        if (onError) {
          onError(errorMsg.error || 'WebSocket error');
        }
      });

      setIsLoading(false);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to Liaison Agent');
      setIsLoading(false);
      setConnected(false);
      if (onError) {
        onError(err.message || 'Failed to connect to Liaison Agent');
      }
    }
  }, [pillar, sessionToken, onMessage, onError]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (connectionIdRef.current) {
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
        unsubscribeRef.current = null;
      }
      webSocketService.disconnect(connectionIdRef.current);
      connectionIdRef.current = null;
      setConnected(false);
    }
  }, []);

  // Auto-connect on mount if enabled
  useEffect(() => {
    if (autoConnect && sessionToken) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, sessionToken, connect, disconnect]);

  // Send message to Liaison Agent
  const sendMessage = useCallback(async (message: string) => {
    if (!connectionIdRef.current || !connected) {
      throw new Error("Not connected to Liaison Agent");
    }

    if (!message.trim()) {
      return;
    }

    try {
      // Add user message to local state immediately
      const userMessage: LiaisonChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: message,
        timestamp: new Date(),
        pillar: pillar
      };

      setMessages(prev => [...prev, userMessage]);

      // Send to backend (backend expects: { "message": "user message" })
      // The backend WebSocket endpoint does: message_data = await websocket.receive_json()
      // and then: user_message = message_data.get("message", "")
      // So it expects the JSON to have "message" at the top level.
      // WebSocketService.send() does JSON.stringify(message), so we need to send
      // a message object that, when stringified, has "message" at the top level.
      // We'll access the WebSocket connection directly to send the correct format.
      const connection = (webSocketService as any).connections?.get(connectionIdRef.current);
      if (!connection) {
        throw new Error("WebSocket connection not found");
      }
      
      if (connection.ws && connection.ws.readyState === WebSocket.OPEN) {
        // Send directly in the format backend expects: { "message": "..." }
        connection.ws.send(JSON.stringify({ message: message }));
      } else {
        throw new Error("WebSocket connection not ready");
      }
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      throw err;
    }
  }, [connected, pillar]);

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    sendMessage,
    connected,
    isLoading,
    error,
    clearMessages
  };
}

