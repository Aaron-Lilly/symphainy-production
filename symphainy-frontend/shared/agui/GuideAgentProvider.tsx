/**
 * Guide Agent Provider - Sophisticated Architecture
 * 
 * Provides the Guide Agent functionality using the new sophisticated architecture.
 * Integrates with GlobalSessionProvider, AuthProvider, and WebSocketService.
 */

"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useAuth } from './AuthProvider';
import { useGlobalSession } from './GlobalSessionProvider';
// Service layer will be dynamically imported when needed

// ============================================================================
// GUIDE AGENT TYPES
// ============================================================================

export interface ConversationMessage {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    intent?: string;
    pillar?: string;
    confidence?: number;
    suggested_actions?: string[];
  };
}

export interface GuidanceResponse {
  success: boolean;
  guidance?: {
    intent_analysis: {
      primary_intent: string;
      confidence: number;
      related_intents: string[];
    };
    recommended_actions: string[];
    suggested_data_types: string[];
    pillar_routing: string;
    next_steps: string[];
    conversation_context: any;
  };
  error?: string;
}

export interface GuideAgentState {
  isInitialized: boolean;
  isConnected: boolean;
  currentGuidance: GuidanceResponse | null;
  conversationHistory: ConversationMessage[];
  isLoading: boolean;
  error: string | null;
  connectionId: string | null; // Track WebSocket connection ID
}

export interface JourneyRequest {
  business_outcome: string;
  journey_type: string;
}

export interface JourneyResponse {
  success: boolean;
  journey_id?: string;
  business_outcome: string;
  journey_type: string;
  status: string;
  current_step: string;
  guide_agent_prompt: string;
  next_steps: string[];
  journey_metadata: {
    created_at: string;
    tenant_id: string;
    user_id: string;
  };
  error?: string;
}

export interface SolutionRequest {
  business_outcome: string;
  solution_intent: string;
}

export interface SolutionResponse {
  success: boolean;
  solution_id?: string;
  business_outcome: string;
  solution_intent: string;
  status: string;
  current_step: string;
  guide_agent_prompt: string;
  next_steps: string[];
  solution_metadata: {
    created_at: string;
    tenant_id: string;
    user_id: string;
  };
  error?: string;
}

export interface GuideAgentContextType {
  state: GuideAgentState;
  sendMessage: (message: string) => Promise<GuidanceResponse>;
  clearConversation: () => void;
  getGuidance: (intent: string) => Promise<GuidanceResponse>;
  createJourney: (request: JourneyRequest) => Promise<JourneyResponse>;
  createSolution: (request: SolutionRequest) => Promise<SolutionResponse>;
  initializeGuideAgent: () => Promise<void>;
}

// ============================================================================
// GUIDE AGENT CONTEXT
// ============================================================================

const GuideAgentContext = createContext<GuideAgentContextType | undefined>(undefined);

// ============================================================================
// GUIDE AGENT PROVIDER
// ============================================================================

export const GuideAgentProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  const { guideSessionToken } = useGlobalSession();
  const [websocket, setWebsocket] = useState<any>(null);
  const [serviceLayerInitialized, setServiceLayerInitialized] = useState(false);

  const [state, setState] = useState<GuideAgentState>({
    isInitialized: false,
    isConnected: false,
    currentGuidance: null,
    conversationHistory: [],
    isLoading: false,
    error: null,
    connectionId: null,
  });

  // Initialize Guide Agent
  const initializeGuideAgent = async () => {
    if (!isAuthenticated || !guideSessionToken || !websocket || !serviceLayerInitialized) {
      return;
    }

    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      // Connect to Unified Agent WebSocket (Phase 5: Unified WebSocket Architecture)
      // Using /api/ws/agent endpoint with agent_type routing
      const connectionId = await websocket.connect('/api/ws/agent', {
        requireAuth: true,
        autoReconnect: true,
        heartbeat: true
      });

      // Store connection ID in state
      setState(prev => ({ ...prev, connectionId }));

      // Subscribe to Unified Agent messages (Phase 5: Unified WebSocket Architecture)
      // Backend sends: { type: "response", agent_type: "guide", message: "...", ... }
      websocket.subscribe(connectionId, 'message', (wsMessage) => {
        console.log("Received Unified Agent message:", wsMessage);
        
        try {
          // Backend sends JSON directly, so wsMessage.data should be the response object
          const response = typeof wsMessage.data === 'string' ? JSON.parse(wsMessage.data) : wsMessage.data;
          
          // Handle different response types (unified format)
          if ((response.type === 'response' || response.type === 'chat_response') && response.agent_type === 'guide') {
            // Convert backend response to GuidanceResponse format
            const guidanceResponse: GuidanceResponse = {
              success: true,
              guidance: {
                intent_analysis: response.intent || { primary_intent: 'general', confidence: 0.8, related_intents: [] },
                recommended_actions: [response.message],
                suggested_data_types: [],
                pillar_routing: response.intent?.target_domain || '',
                next_steps: [],
                conversation_context: response.guidance_response || {}
              }
            };

            setState(prev => ({
              ...prev,
              currentGuidance: guidanceResponse,
              isConnected: true,
              isLoading: false,
              error: null,
            }));

            // Add agent response to conversation history
            const agentMessage: ConversationMessage = {
              id: `agent-${Date.now()}`,
              type: 'agent',
              content: response.message || 'Response received',
              timestamp: new Date(),
              metadata: {
                intent: response.intent?.primary_intent,
                pillar: response.intent?.target_domain,
                confidence: response.intent?.confidence,
                suggested_actions: [response.message],
              }
            };

            setState(prev => ({
              ...prev,
              conversationHistory: [...prev.conversationHistory, agentMessage]
            }));
          } else if (response.type === 'error') {
            setState(prev => ({
              ...prev,
              error: response.message || 'Error from Guide Agent',
              isLoading: false,
            }));
          }
        } catch (parseError) {
          console.error("Error parsing Guide Agent response:", parseError);
          setState(prev => ({
            ...prev,
            error: "Error parsing guidance response",
            isLoading: false,
          }));
        }
      });

      setState(prev => ({
        ...prev,
        isInitialized: true,
        isConnected: true,
        isLoading: false,
        error: null,
      }));

    } catch (error: any) {
      console.error("Failed to initialize Guide Agent:", error);
      setState(prev => ({
        ...prev,
        error: error.message || "Failed to initialize Guide Agent",
        isLoading: false,
        isConnected: false,
      }));
    }
  };

  // Send message to Guide Agent
  const sendMessage = async (message: string): Promise<GuidanceResponse> => {
    if (!websocket || !guideSessionToken) {
      throw new Error("Guide Agent not initialized");
    }

    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      // Add user message to conversation history
      const userMessage: ConversationMessage = {
        id: `user-${Date.now()}`,
        type: 'user',
        content: message,
        timestamp: new Date(),
      };

      setState(prev => ({
        ...prev,
        conversationHistory: [...prev.conversationHistory, userMessage]
      }));

      // Send message to Guide Agent via Unified WebSocket (Phase 5: Unified WebSocket Architecture)
      // Backend expects: { "agent_type": "guide", "message": "user message", "conversation_id": "..." }
      const messageToSend = {
        agent_type: 'guide',
        message: message,
        conversation_id: state.connectionId || undefined
      };

      // Use stored connection ID
      const connectionId = state.connectionId;
      
      if (!connectionId) {
        throw new Error("Guide Agent connection not initialized");
      }

      if (!websocket.isConnected(connectionId)) {
        throw new Error("Guide Agent connection not connected");
      }

      await websocket.send(connectionId, messageToSend);

      // Return a promise that resolves when we get the response
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error("Guide Agent response timeout"));
        }, 30000);

        // Listen for the response (this will be handled by the subscribe callback above)
        const checkForResponse = () => {
          if (state.currentGuidance) {
            clearTimeout(timeout);
            resolve(state.currentGuidance);
          } else if (state.error) {
            clearTimeout(timeout);
            reject(new Error(state.error));
          } else {
            setTimeout(checkForResponse, 100);
          }
        };
        
        checkForResponse();
      });

    } catch (error: any) {
      setState(prev => ({
        ...prev,
        error: error.message || "Failed to send message to Guide Agent",
        isLoading: false,
      }));
      throw error;
    }
  };

  // Get guidance for specific intent
  const getGuidance = async (intent: string): Promise<GuidanceResponse> => {
    return sendMessage(`I need guidance for: ${intent}`);
  };

  // Create solution (calls backend Solution Manager via Solution-Driven Architecture)
  const createSolution = async (request: SolutionRequest): Promise<SolutionResponse> => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      // Call Solution Manager API endpoint (Solution-Driven Architecture)
      const response = await fetch('/api/v1/solution/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(guideSessionToken && { 'Authorization': `Bearer ${guideSessionToken}` }),
        },
        body: JSON.stringify({
          solution_type: request.solution_intent || 'mvp',
          requirements: {
            business_outcome: request.business_outcome,
            user_id: user?.id || 'anonymous',
            tenant_id: user?.tenant_id || 'default',
          }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Transform Solution Manager response to SolutionResponse format
      const solutionResponse: SolutionResponse = {
        success: data.success || false,
        solution_id: data.solution_id || data.result?.solution_id,
        business_outcome: request.business_outcome,
        solution_intent: request.solution_intent || 'mvp',
        status: data.design_status || data.status || 'created',
        current_step: data.current_step || 'initialization',
        guide_agent_prompt: data.guide_agent_prompt || 'Solution created successfully. Let\'s begin your journey!',
        next_steps: data.next_steps || data.journey?.next_steps || ['Begin solution implementation'],
        solution_metadata: {
          created_at: data.created_at || new Date().toISOString(),
          tenant_id: user?.tenant_id || 'default',
          user_id: user?.id || 'anonymous',
        },
        error: data.error,
      };
      
      if (solutionResponse.success) {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: null,
        }));
      } else {
        setState(prev => ({
          ...prev,
          error: solutionResponse.error || "Failed to create solution",
          isLoading: false,
        }));
      }

      return solutionResponse;

    } catch (error: any) {
      setState(prev => ({
        ...prev,
        error: error.message || "Failed to create solution",
        isLoading: false,
      }));
      throw error;
    }
  };

  // Clear conversation history
  const clearConversation = () => {
    setState(prev => ({
      ...prev,
      conversationHistory: [],
      currentGuidance: null,
      error: null,
    }));
  };

  // Load service layer dynamically
  useEffect(() => {
    if (typeof window !== 'undefined' && isAuthenticated && guideSessionToken) {
      const loadServiceLayer = async () => {
        try {
          const { SimpleWebSocketService } = await import('@/shared/services/SimpleServiceLayer');
          const webSocketService = new SimpleWebSocketService();
          webSocketService.setSessionToken(guideSessionToken);
          setWebsocket(webSocketService);
          setServiceLayerInitialized(true);
        } catch (error) {
          console.error('Failed to load service layer:', error);
        }
      };
      loadServiceLayer();
    }
  }, [isAuthenticated, guideSessionToken]);

  // Initialize when authenticated and service layer is ready
  useEffect(() => {
    if (isAuthenticated && guideSessionToken && serviceLayerInitialized && !state.isInitialized) {
      initializeGuideAgent();
    }
  }, [isAuthenticated, guideSessionToken, serviceLayerInitialized, state.isInitialized]);

  const contextValue: GuideAgentContextType = {
    state,
    sendMessage,
    clearConversation,
    getGuidance,
    createJourney: async (request: JourneyRequest): Promise<JourneyResponse> => {
      // For now, return a mock response
      // TODO: Implement actual journey creation
      return {
        success: true,
        journey_id: `journey_${Date.now()}`,
        business_outcome: request.business_outcome,
        journey_type: request.journey_type,
        status: "created",
        current_step: "initialization",
        guide_agent_prompt: "Journey created successfully",
        next_steps: ["Begin journey implementation"],
        journey_metadata: {
          created_at: new Date().toISOString(),
          tenant_id: user?.tenant_id || "default",
          user_id: user?.id || "default"
        }
      };
    },
    createSolution,
    initializeGuideAgent,
  };

  return (
    <GuideAgentContext.Provider value={contextValue}>
      {children}
    </GuideAgentContext.Provider>
  );
};

// ============================================================================
// GUIDE AGENT HOOK
// ============================================================================

export const useGuideAgent = (): GuideAgentContextType => {
  const context = useContext(GuideAgentContext);
  if (context === undefined) {
    throw new Error('useGuideAgent must be used within a GuideAgentProvider');
  }
  return context;
};
