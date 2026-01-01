/**
 * React Hooks for Enhanced WebSocket Client
 * Provides React hooks for WebSocket functionality
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { EnhancedSmartCityWebSocketClient } from './EnhancedSmartCityWebSocketClient';
import { getGlobalConfig } from '../config';

// Hook for WebSocket connection management
export function useWebSocketConnection() {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsClientRef = useRef<EnhancedSmartCityWebSocketClient | null>(null);
  const config = getGlobalConfig();

  const connect = useCallback(async () => {
    if (!wsClientRef.current) {
      wsClientRef.current = new EnhancedSmartCityWebSocketClient();
    }

    setIsConnecting(true);
    setError(null);

    try {
      await wsClientRef.current.connect();
      setIsConnected(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection failed');
    } finally {
      setIsConnecting(false);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (wsClientRef.current) {
      wsClientRef.current.disconnect();
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    // Auto-connect if Smart City is enabled
    if (config.getSection('smartCity').enabled) {
      connect();
    }

    return () => {
      if (wsClientRef.current) {
        wsClientRef.current.shutdown();
      }
    };
  }, [connect]);

  return {
    isConnected,
    isConnecting,
    error,
    connect,
    disconnect,
    wsClient: wsClientRef.current,
  };
}

// Hook for Smart City session management
export function useSmartCitySession() {
  const { wsClient } = useWebSocketConnection();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionStatus, setSessionStatus] = useState<string>('disconnected');

  const createSession = useCallback(async (sessionData: any) => {
    if (!wsClient) throw new Error('WebSocket not connected');
    
    const newSessionId = await wsClient.createSession(sessionData);
    setSessionId(newSessionId);
    setSessionStatus('created');
    return newSessionId;
  }, [wsClient]);

  const validateSession = useCallback(async (sessionId: string) => {
    if (!wsClient) throw new Error('WebSocket not connected');
    
    const isValid = await wsClient.validateSession(sessionId);
    setSessionStatus(isValid ? 'valid' : 'invalid');
    return isValid;
  }, [wsClient]);

  const getStatus = useCallback(async (sessionId: string) => {
    if (!wsClient) throw new Error('WebSocket not connected');
    
    const status = await wsClient.getSessionStatus(sessionId);
    setSessionStatus(status);
    return status;
  }, [wsClient]);

  return {
    sessionId,
    sessionStatus,
    createSession,
    validateSession,
    getStatus,
  };
}

// Hook for message queuing
export function useMessageQueue() {
  const { wsClient } = useWebSocketConnection();
  const [queueStats, setQueueStats] = useState(wsClient?.getQueueStats() || {
    queueSize: 0,
    maxQueueSize: 100,
    processing: false,
    messagesByPriority: { high: 0, normal: 0, low: 0 },
  });

  const sendMessage = useCallback(async (
    message: any, 
    priority: 'HIGH' | 'NORMAL' | 'LOW' = 'NORMAL'
  ) => {
    if (!wsClient) throw new Error('WebSocket not connected');
    
    await wsClient.sendMessage(message, priority);
    setQueueStats(wsClient.getQueueStats());
  }, [wsClient]);

  const clearQueue = useCallback(() => {
    if (wsClient) {
      wsClient.clearQueue();
      setQueueStats(wsClient.getQueueStats());
    }
  }, [wsClient]);

  // Update queue stats periodically
  useEffect(() => {
    if (!wsClient) return;

    const interval = setInterval(() => {
      setQueueStats(wsClient.getQueueStats());
    }, 1000);

    return () => clearInterval(interval);
  }, [wsClient]);

  return {
    queueStats,
    sendMessage,
    clearQueue,
  };
}

// Hook for connection health monitoring
export function useConnectionHealth() {
  const { wsClient } = useWebSocketConnection();
  const [poolStats, setPoolStats] = useState(wsClient?.getPoolStats() || {
    totalConnections: 0,
    maxConnections: 5,
    healthyConnections: 0,
    unhealthyConnections: 0,
  });

  // Update pool stats periodically
  useEffect(() => {
    if (!wsClient) return;

    const interval = setInterval(() => {
      setPoolStats(wsClient.getPoolStats());
    }, 5000);

    return () => clearInterval(interval);
  }, [wsClient]);

  return {
    poolStats,
  };
} 