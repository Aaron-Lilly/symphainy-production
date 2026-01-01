/**
 * useExperienceChat Hook
 * 
 * ⚠️ DEPRECATED: This hook is deprecated and will be removed in a future release.
 * 
 * Migration Guide:
 * - For Guide Agent: Use `useUnifiedAgentChat({ initialAgent: 'guide' })` from `@/shared/hooks/useUnifiedAgentChat`
 * - For Liaison Agents: Use `useUnifiedAgentChat({ initialAgent: 'liaison', initialPillar: 'content' | 'insights' | 'operations' | 'business_outcomes' })`
 * 
 * The unified hook provides:
 * - Single WebSocket connection for all agents
 * - Better resource efficiency
 * - Agent switching without reconnection
 * - Conversation history management
 * 
 * Phase 5: Unified WebSocket Architecture - Replaced by useUnifiedAgentChat
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useSetAtom } from 'jotai';
import { chatbotAgentInfoAtom, mainChatbotOpenAtom } from '@/shared/atoms/chatbot-atoms';

interface ChatMessage {
  id: string;
  agent: 'guide' | 'specialist';
  sender: 'user' | 'bot';
  message: string;
  timestamp: Date;
}

interface UseExperienceChatProps {
  sessionToken: string;
  onContextUpdate?: (context: any) => void;
}

export function useExperienceChat({ sessionToken, onContextUpdate }: UseExperienceChatProps) {
  const setAgentTitle = useSetAtom(chatbotAgentInfoAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [activeAgent, setActiveAgent] = useState<'guide' | 'specialist'>('guide');
  const [isLoading, setIsLoading] = useState(false);

  // WebSocket connections
  const [guideWebSocket, setGuideWebSocket] = useState<WebSocket | null>(null);
  const [specialistWebSocket, setSpecialistWebSocket] = useState<WebSocket | null>(null);

  // Initialize WebSocket connections
  useEffect(() => {
    if (!sessionToken) return;

    // Production: Use Traefik route (port 80, no :8000)
    // Use centralized API config (NO hardcoded values)
    const { getWebSocketUrl } = require('@/shared/config/api-config');
    const API_URL = getWebSocketUrl(sessionToken).replace(/\?.*$/, '').replace(/^ws/, 'http'); // Convert back to HTTP for base URL
    
    // Guide Agent WebSocket (Phase 6: Updated endpoint)
    const guideWs = new WebSocket(`${API_URL.replace('http', 'ws')}/api/ws/guide${sessionToken ? `?session_token=${sessionToken}` : ''}`);
    
    guideWs.onopen = () => {
      console.log('Guide WebSocket connected');
      setIsConnected(true);
    };
    
    guideWs.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        // Backend sends: { type: "chat_response", agent_type: "guide", message: "...", ... }
        const message = data.message || data.data || 'Message received';
        addMessage('guide', 'bot', message);
      } catch (error) {
        console.error('Error parsing guide message:', error);
      }
    };
    
    guideWs.onerror = (error) => {
      console.error('Guide WebSocket error:', error);
      setIsConnected(false);
    };
    
    guideWs.onclose = () => {
      console.log('Guide WebSocket disconnected');
      setIsConnected(false);
    };

    setGuideWebSocket(guideWs);

    // Cleanup on unmount
    return () => {
      guideWs.close();
    };
  }, [sessionToken]);

  // Initialize Specialist WebSocket when needed
  const initializeSpecialistWebSocket = useCallback(() => {
    if (specialistWebSocket) return;

    // Production: Use Traefik route (port 80, no :8000)
    // Use centralized API config (NO hardcoded values)
    const { getWebSocketUrl } = require('@/shared/config/api-config');
    const API_URL = getWebSocketUrl(sessionToken).replace(/\?.*$/, '').replace(/^ws/, 'http'); // Convert back to HTTP for base URL
    
    const specialistWs = new WebSocket(`${API_URL.replace('http', 'ws')}/api/ws/agent-wise-chat`);
    
    specialistWs.onopen = () => {
      console.log('Specialist WebSocket connected');
    };
    
    specialistWs.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        addMessage('specialist', 'bot', data.data || data.message || 'Message received');
      } catch (error) {
        console.error('Error parsing specialist message:', error);
      }
    };
    
    specialistWs.onerror = (error) => {
      console.error('Specialist WebSocket error:', error);
    };
    
    specialistWs.onclose = () => {
      console.log('Specialist WebSocket disconnected');
    };

    setSpecialistWebSocket(specialistWs);
  }, [specialistWebSocket]);

  const addMessage = useCallback((agent: 'guide' | 'specialist', sender: 'user' | 'bot', message: string) => {
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      agent,
      sender,
      message,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, newMessage]);
    
    // Update context if callback provided
    if (onContextUpdate) {
      onContextUpdate({
        agent,
        message,
        timestamp: newMessage.timestamp
      });
    }
  }, [onContextUpdate]);

  const sendMessage = useCallback(async (message: string, agent: 'guide' | 'specialist' = activeAgent) => {
    if (!sessionToken) return;

    setIsLoading(true);
    
    try {
      // Add user message to chat
      addMessage(agent, 'user', message);

      if (agent === 'guide') {
        // Send to Guide Agent (Phase 6: Updated message format)
        // Backend expects: { "message": "user message" }
        if (guideWebSocket && guideWebSocket.readyState === WebSocket.OPEN) {
          guideWebSocket.send(JSON.stringify({
            message: message
          }));
        }
      } else {
        // Send to Experience Specialist (Phase 6: Deprecated)
        // Note: Specialist agent endpoint is deprecated. Use useLiaisonChat hook for pillar-specific agents.
        console.warn('useExperienceChat: Specialist agent is deprecated. Use useLiaisonChat hook for liaison agents.');
        // Specialist WebSocket is disabled - migration needed to useLiaisonChat
      }
    } catch (error) {
      console.error('Error sending message:', error);
      addMessage(agent, 'bot', 'Sorry, there was an error sending your message.');
    } finally {
      setIsLoading(false);
    }
  }, [sessionToken, activeAgent, guideWebSocket, specialistWebSocket, addMessage, initializeSpecialistWebSocket]);

  const startGuideChat = useCallback(() => {
    setAgentTitle({
      title: "Experience Guide",
      agent: "GuideAgent",
      file_url: "",
      additional_info: "Your AI guide for the Experience pillar journey"
    });
    setActiveAgent('guide');
    setMainChatbotOpen(true);
  }, [setAgentTitle, setMainChatbotOpen]);

  const startSpecialistChat = useCallback(() => {
    setAgentTitle({
      title: "Experience Specialist",
      agent: "ExperienceSpecialistAgent",
      file_url: "",
      additional_info: "Technical expert for roadmap and POC generation"
    });
    setActiveAgent('specialist');
    setMainChatbotOpen(true);
    
    // Initialize specialist WebSocket if not already done
    if (!specialistWebSocket) {
      initializeSpecialistWebSocket();
    }
  }, [setAgentTitle, setMainChatbotOpen, specialistWebSocket, initializeSpecialistWebSocket]);

  const getAgentMessages = useCallback((agent: 'guide' | 'specialist') => {
    return messages.filter(msg => msg.agent === agent);
  }, [messages]);

  const clearMessages = useCallback((agent?: 'guide' | 'specialist') => {
    if (agent) {
      setMessages(prev => prev.filter(msg => msg.agent !== agent));
    } else {
      setMessages([]);
    }
  }, []);

  return {
    // State
    messages,
    isConnected,
    activeAgent,
    isLoading,
    
    // Actions
    sendMessage,
    startGuideChat,
    startSpecialistChat,
    getAgentMessages,
    clearMessages,
    setActiveAgent,
    
    // WebSocket instances (for advanced usage)
    guideWebSocket,
    specialistWebSocket
  };
}