/**
 * useUnifiedAgentChat Hook
 * 
 * Unified React hook for all agent communications (Guide + Liaison).
 * Uses single WebSocket connection with message routing.
 * 
 * Phase 5: Unified WebSocket Architecture
 * 
 * Features:
 * - Single WebSocket connection per user
 * - Message routing based on agent_type and pillar
 * - Conversation context management
 * - Agent switching without reconnection
 * - AGUI component support
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { webSocketConnectionRegistry } from '@/shared/managers/WebSocketConnectionRegistry';
import { getWebSocketUrl } from '@/shared/config/api-config';

export type AgentType = 'guide' | 'liaison';
export type PillarType = 'content' | 'insights' | 'operations' | 'business_outcomes';

export interface UnifiedChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  agent_type: AgentType;
  pillar?: PillarType;
  conversation_id?: string;
  metadata?: {
    data?: any; // AGUI components, analysis results, etc.
    visualization?: any; // Visualization components
    intent?: any;
    [key: string]: any;
  };
}

export interface UseUnifiedAgentChatReturn {
  // State
  messages: UnifiedChatMessage[];
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  currentAgent: AgentType | null;
  currentPillar: PillarType | null;
  conversationId: string | null;
  
  // Actions
  sendMessage: (message: string, agentType?: AgentType, pillar?: PillarType) => Promise<void>;
  switchAgent: (agentType: AgentType, pillar?: PillarType) => void;
  clearMessages: (conversationId?: string) => void;
  connect: () => Promise<void>;
  disconnect: () => void;
  
  // Conversation management
  getConversationMessages: (conversationId: string) => UnifiedChatMessage[];
  setConversationId: (conversationId: string) => void;
}

export interface UseUnifiedAgentChatOptions {
  sessionToken?: string;
  autoConnect?: boolean;
  initialAgent?: AgentType;
  initialPillar?: PillarType;
  onMessage?: (message: UnifiedChatMessage) => void;
  onError?: (error: string) => void;
  onAgentSwitch?: (agentType: AgentType, pillar?: PillarType) => void;
}

export function useUnifiedAgentChat(
  options: UseUnifiedAgentChatOptions = {}
): UseUnifiedAgentChatReturn {
  const {
    sessionToken,
    autoConnect = true,
    initialAgent = 'guide',
    initialPillar,
    onMessage,
    onError,
    onAgentSwitch
  } = options;

  const [messages, setMessages] = useState<UnifiedChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentAgent, setCurrentAgent] = useState<AgentType | null>(initialAgent);
  const [currentPillar, setCurrentPillar] = useState<PillarType | null>(initialPillar || null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 1000;

  // Generate conversation ID
  const generateConversationId = useCallback((agentType: AgentType, pillar?: PillarType): string => {
    const pillarPart = pillar ? `_${pillar}` : '';
    return `${agentType}${pillarPart}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  // Get WebSocket URL - use centralized config (NO hardcoded values)
  const getWebSocketURLCallback = useCallback((): string => {
    return getWebSocketUrl(sessionToken);
  }, [sessionToken]);

  // Connect to unified WebSocket
  const connect = useCallback(async () => {
    // ✅ Safety check: Don't connect if sessionToken is missing, empty, or invalid
    if (!sessionToken || typeof sessionToken !== 'string' || sessionToken.trim() === '' || sessionToken === 'token_placeholder') {
      setError("Session token required");
      return;
    }

    // ✅ Check registry for existing connection
    const existingConnection = webSocketConnectionRegistry.getConnection(sessionToken);
    if (existingConnection && existingConnection.readyState === WebSocket.OPEN) {
      // Use existing connection
      wsRef.current = existingConnection;
      setIsConnected(true);
      setIsLoading(false);
      setError(null);
      return;
    }

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      // Already connected
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      const wsURL = getWebSocketURLCallback();
      console.log('🔌 [useUnifiedAgentChat] Connecting to WebSocket:', {
        url: wsURL.replace(/\?session_token=.*/, '?session_token=***'), // Mask token in logs
        hasToken: !!sessionToken,
        tokenLength: sessionToken?.length || 0
      });
      
      const ws = new WebSocket(wsURL);
      
      // ✅ Register connection in registry
      webSocketConnectionRegistry.registerConnection(sessionToken, ws);

      ws.onopen = () => {
        console.log('✅ Unified Agent WebSocket connected');
        setIsConnected(true);
        setIsLoading(false);
        reconnectAttemptsRef.current = 0;
        
        // Generate initial conversation ID if not set
        if (!conversationId && currentAgent) {
          const newConversationId = generateConversationId(currentAgent, currentPillar || undefined);
          setConversationId(newConversationId);
        }
      };

      ws.onmessage = (event) => {
        try {
          const response = JSON.parse(event.data);
          
          // ✅ Handle heartbeat ping (keepalive) - respond with pong
          if (response.type === 'heartbeat' && response.action === 'ping') {
            // Respond to server heartbeat ping
            try {
              ws.send(JSON.stringify({
                type: 'heartbeat',
                action: 'pong',
                timestamp: Date.now(),
                connection_id: response.connection_id
              }));
              // Don't update UI state for heartbeat - it's just keepalive
              return;
            } catch (pongError) {
              console.warn('[useUnifiedAgentChat] Failed to send heartbeat pong:', pongError);
            }
            return;
          }
          
          // Handle error responses
          if (response.type === 'error') {
            const errorMsg = response.message || 'Error from agent';
            setError(errorMsg);
            if (onError) {
              onError(errorMsg);
            }
            return;
          }

          // Handle chat responses
          if (response.type === 'response' || response.message) {
            const assistantMessage: UnifiedChatMessage = {
              id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
              role: 'assistant',
              content: response.message || response.response || 'Response received',
              timestamp: new Date(),
              agent_type: response.agent_type || currentAgent || 'guide',
              pillar: response.pillar || currentPillar || undefined,
              conversation_id: response.conversation_id || conversationId || undefined,
              metadata: {
                data: response.data,
                visualization: response.visualization,
                intent: response.intent,
                ...response.metadata
              }
            };

            setMessages(prev => [...prev, assistantMessage]);
            
            // Update conversation ID if provided
            if (response.conversation_id && response.conversation_id !== conversationId) {
              setConversationId(response.conversation_id);
            }
            
            if (onMessage) {
              onMessage(assistantMessage);
            }
          }
        } catch (parseError) {
          console.error('Error parsing agent message:', parseError);
          setError('Error parsing message');
          if (onError) {
            onError('Error parsing message');
          }
        }
      };

      ws.onerror = (error) => {
        console.error('❌ Unified Agent WebSocket error:', error);
        console.error('   WebSocket URL:', wsURL);
        console.error('   Session Token:', sessionToken ? `${sessionToken.substring(0, 20)}...` : 'missing');
        console.error('   Ready State:', ws.readyState);
        
        // Provide more specific error messages
        let errorMessage = 'WebSocket connection error';
        if (ws.readyState === WebSocket.CONNECTING) {
          errorMessage = 'Failed to establish WebSocket connection. Please check your network connection.';
        } else if (ws.readyState === WebSocket.CLOSING || ws.readyState === WebSocket.CLOSED) {
          errorMessage = 'WebSocket connection closed unexpectedly. Please try reconnecting.';
        }
        
        setError(errorMessage);
        setIsConnected(false);
        setIsLoading(false);
        if (onError) {
          onError(errorMessage);
        }
      };

      ws.onclose = (event) => {
        console.log('🔌 Unified Agent WebSocket disconnected:', {
          code: event.code,
          reason: event.reason,
          wasClean: event.wasClean,
          readyState: ws.readyState
        });
        
        setIsConnected(false);
        setIsLoading(false);
        wsRef.current = null;

        // Provide user-friendly error messages based on close codes
        if (event.code !== 1000) {
          let errorMessage = 'WebSocket connection closed';
          if (event.code === 4003) {
            errorMessage = 'Connection rejected: Origin not allowed';
          } else if (event.code === 4004) {
            errorMessage = 'Connection rejected: Connection limit exceeded';
          } else if (event.code === 4005) {
            errorMessage = 'Connection rejected: Server at capacity';
          } else if (event.code === 1006) {
            errorMessage = 'Connection closed abnormally. Please check your network connection.';
          } else if (event.code === 1011) {
            errorMessage = 'Server error. Please try again later.';
          }
          setError(errorMessage);
          if (onError) {
            onError(errorMessage);
          }
        }

        // ✅ Only auto-reconnect if autoConnect is enabled AND not intentionally closed
        // This prevents retry loops when connection is deferred (Option B)
        if (autoConnect && event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          const delay = reconnectDelay * reconnectAttemptsRef.current;
          console.log(`🔄 Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (!autoConnect) {
          // If autoConnect is disabled, don't retry - connection is deferred
          console.log('[useUnifiedAgentChat] Auto-reconnect disabled (autoConnect: false)');
        }
      };

      wsRef.current = ws;
    } catch (err: any) {
      setError(err.message || 'Failed to connect to Unified Agent WebSocket');
      setIsLoading(false);
      setIsConnected(false);
      if (onError) {
        onError(err.message || 'Failed to connect to Unified Agent WebSocket');
      }
    }
  }, [sessionToken, getWebSocketURLCallback, conversationId, currentAgent, currentPillar, onMessage, onError, generateConversationId, autoConnect, maxReconnectAttempts, reconnectDelay]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected');
      wsRef.current = null;
    }
    
    // ✅ Remove from registry
    if (sessionToken) {
      webSocketConnectionRegistry.removeConnection(sessionToken);
    }
    
    setIsConnected(false);
    reconnectAttemptsRef.current = 0;
  }, [sessionToken]);

  // Send message to agent
  const sendMessage = useCallback(async (
    message: string,
    agentType: AgentType = currentAgent || 'guide',
    pillar?: PillarType
  ) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      throw new Error("Not connected to Unified Agent WebSocket");
    }

    if (!message.trim()) {
      return;
    }

    try {
      // Update current agent/pillar if different
      if (agentType !== currentAgent || (pillar && pillar !== currentPillar)) {
        setCurrentAgent(agentType);
        if (pillar) {
          setCurrentPillar(pillar);
        }
        
        // Generate new conversation ID for new agent/pillar
        const newConversationId = generateConversationId(agentType, pillar);
        setConversationId(newConversationId);
        
        if (onAgentSwitch) {
          onAgentSwitch(agentType, pillar);
        }
      }

      // Use current conversation ID or generate one
      const activeConversationId = conversationId || generateConversationId(agentType, pillar || currentPillar || undefined);
      if (!conversationId) {
        setConversationId(activeConversationId);
      }

      // Add user message to local state immediately
      const userMessage: UnifiedChatMessage = {
        id: `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        role: 'user',
        content: message,
        timestamp: new Date(),
        agent_type: agentType,
        pillar: pillar || currentPillar || undefined,
        conversation_id: activeConversationId
      };

      setMessages(prev => [...prev, userMessage]);

      // NEW: Send to backend in channel-based message format (Post Office Gateway)
      // Channel format: "guide" or "pillar:content", "pillar:insights", etc.
      const channel = agentType === 'guide' 
        ? 'guide' 
        : `pillar:${pillar || currentPillar || 'content'}`;
      
      const messagePayload = {
        channel: channel,
        intent: "chat", // Default intent, can be extended later
        payload: {
          message: message,
          conversation_id: activeConversationId,
          agent_type: agentType, // Keep for backward compatibility during transition
          pillar: pillar || currentPillar || undefined
        }
      };

      wsRef.current.send(JSON.stringify(messagePayload));
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      throw err;
    }
  }, [currentAgent, currentPillar, conversationId, generateConversationId, onAgentSwitch]);

  // Switch agent without reconnecting
  const switchAgent = useCallback((agentType: AgentType, pillar?: PillarType) => {
    setCurrentAgent(agentType);
    if (pillar) {
      setCurrentPillar(pillar);
    } else if (agentType === 'guide') {
      // Guide agent doesn't have a pillar
      setCurrentPillar(null);
    }

    // Generate new conversation ID for new agent/pillar
    const newConversationId = generateConversationId(agentType, pillar);
    setConversationId(newConversationId);

    if (onAgentSwitch) {
      onAgentSwitch(agentType, pillar);
    }
  }, [generateConversationId, onAgentSwitch]);

  // Clear messages (optionally for specific conversation)
  const clearMessages = useCallback((targetConversationId?: string) => {
    if (targetConversationId) {
      setMessages(prev => prev.filter(msg => msg.conversation_id !== targetConversationId));
    } else {
      setMessages([]);
    }
  }, []);

  // Get messages for specific conversation
  const getConversationMessages = useCallback((targetConversationId: string): UnifiedChatMessage[] => {
    return messages.filter(msg => msg.conversation_id === targetConversationId);
  }, [messages]);

  // Auto-connect on mount if enabled
  useEffect(() => {
    // ✅ CRITICAL: Only connect if autoConnect is explicitly true
    // If autoConnect is false, do NOT attempt any connection (Option B: defer connection)
    if (!autoConnect) {
      // Explicitly disabled - don't connect, don't retry, just return
      // This prevents any connection attempts when connection is deferred
      if (wsRef.current) {
        disconnect();
      }
      return;
    }
    
    // ✅ Safety check: Only connect if autoConnect is explicitly true AND sessionToken is valid
    // This prevents connections when:
    // - sessionToken is undefined, null, empty, or placeholder
    // - Token is too short (likely invalid)
    const isValidToken = sessionToken && 
      typeof sessionToken === 'string' && 
      sessionToken.trim() !== '' && 
      sessionToken !== 'token_placeholder' &&
      sessionToken.length > 10; // Ensure token is substantial
    
    if (isValidToken) {
      // ✅ Add small delay to ensure token is fully validated and ready
      // This prevents race conditions where connection attempts happen before token is ready
      const connectTimer = setTimeout(() => {
        connect();
      }, 150); // 150ms delay to ensure state is fully settled
      
      return () => {
        clearTimeout(connectTimer);
        disconnect();
      };
    } else {
      // If we shouldn't connect, make sure we're disconnected
      if (wsRef.current) {
        disconnect();
      }
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, sessionToken, connect, disconnect]);

  return {
    // State
    messages,
    isConnected,
    isLoading,
    error,
    currentAgent,
    currentPillar,
    conversationId,
    
    // Actions
    sendMessage,
    switchAgent,
    clearMessages,
    connect,
    disconnect,
    
    // Conversation management
    getConversationMessages,
    setConversationId
  };
}

