/**
 * useAuthAwareWebSocket Hook
 * 
 * Auth-aware WebSocket connection hook that ensures connections only happen
 * when authentication is fully confirmed. This prevents race conditions between
 * auth state restoration and WebSocket connection attempts.
 * 
 * Features:
 * - Waits for auth state to be confirmed before connecting
 * - Validates session token before connection
 * - Handles connection lifecycle (connect, disconnect, reconnect)
 * - Distinguishes between auth errors and connection errors
 * - Provides clear error states
 */

"use client";

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/shared/agui/AuthProvider';
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
import {
  createErrorFromCloseEvent,
  createErrorFromError,
  getUserFriendlyMessage,
  shouldRedirectToLogin,
  WebSocketError
} from '@/shared/utils/websocketErrorHandler';

export interface UseAuthAwareWebSocketOptions {
  /**
   * WebSocket URL or function that returns URL
   * Can include session_token as query param or will be added automatically
   */
  url: string | (() => string);
  
  /**
   * Auto-connect when auth is confirmed
   * @default true
   */
  autoConnect?: boolean;
  
  /**
   * Callback when connection is established
   */
  onOpen?: (event: Event) => void;
  
  /**
   * Callback when message is received
   */
  onMessage?: (event: MessageEvent) => void;
  
  /**
   * Callback when connection closes
   */
  onClose?: (event: CloseEvent) => void;
  
  /**
   * Callback when error occurs
   * Receives error type: 'auth' | 'connection' | 'server' | 'unknown'
   */
  onError?: (error: Error, type: 'auth' | 'connection' | 'server' | 'unknown') => void;
  
  /**
   * Enable auto-reconnect on connection errors (not auth errors)
   * @default true
   */
  autoReconnect?: boolean;
  
  /**
   * Max reconnect attempts
   * @default 5
   */
  maxReconnectAttempts?: number;
  
  /**
   * Reconnect delay in ms (exponential backoff)
   * @default 1000
   */
  reconnectDelay?: number;
  
  /**
   * Protocols for WebSocket connection
   */
  protocols?: string | string[];
}

export interface UseAuthAwareWebSocketReturn {
  /**
   * WebSocket instance (null if not connected)
   */
  socket: WebSocket | null;
  
  /**
   * Connection state
   */
  isConnected: boolean;
  
  /**
   * Is connecting (including auth check)
   */
  isLoading: boolean;
  
  /**
   * Error message (if any)
   */
  error: string | null;
  
  /**
   * Error type: 'auth' | 'connection' | 'server' | 'unknown' | null
   */
  errorType: 'auth' | 'connection' | 'server' | 'unknown' | null;
  
  /**
   * Manually connect (will wait for auth if needed)
   */
  connect: () => Promise<void>;
  
  /**
   * Manually disconnect
   */
  disconnect: () => void;
  
  /**
   * Send message (only if connected)
   */
  send: (data: string | ArrayBuffer | Blob) => void;
  
  /**
   * Reconnect (useful for manual retry)
   */
  reconnect: () => Promise<void>;
}

export function useAuthAwareWebSocket(
  options: UseAuthAwareWebSocketOptions
): UseAuthAwareWebSocketReturn {
  const {
    url,
    autoConnect = true,
    onOpen,
    onMessage,
    onClose,
    onError,
    autoReconnect = true,
    maxReconnectAttempts = 5,
    reconnectDelay = 1000,
    protocols
  } = options;

  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { guideSessionToken } = useGlobalSession();

  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorType, setErrorType] = useState<'auth' | 'connection' | 'server' | 'unknown' | null>(null);

  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isIntentionallyDisconnectedRef = useRef(false);

  /**
   * Get WebSocket URL with session token
   */
  const getWebSocketURL = useCallback((): string => {
    const baseURL = typeof url === 'function' ? url() : url;
    
    // If URL already has query params, append session_token
    // Otherwise, add it as first param
    const separator = baseURL.includes('?') ? '&' : '?';
    const tokenParam = guideSessionToken 
      ? `${separator}session_token=${encodeURIComponent(guideSessionToken)}`
      : '';
    
    return `${baseURL}${tokenParam}`;
  }, [url, guideSessionToken]);

  /**
   * Check if we can connect (auth is ready)
   */
  const canConnect = useCallback((): boolean => {
    // Must not be loading auth
    if (authLoading) {
      return false;
    }
    
    // Must be authenticated
    if (!isAuthenticated) {
      return false;
    }
    
    // Must have valid session token
    if (!guideSessionToken || 
        guideSessionToken.trim() === '' || 
        guideSessionToken === 'token_placeholder') {
      return false;
    }
    
    return true;
  }, [authLoading, isAuthenticated, guideSessionToken]);

  /**
   * Handle WebSocket connection
   */
  const connect = useCallback(async (): Promise<void> => {
    // Check if we can connect (auth must be ready)
    if (!canConnect()) {
      const errorMsg = authLoading 
        ? 'Waiting for authentication...'
        : !isAuthenticated
        ? 'Authentication required'
        : 'Invalid session token';
      
      setError(errorMsg);
      setErrorType('auth');
      setIsLoading(false);
      
      if (onError) {
        onError(new Error(errorMsg), 'auth');
      }
      
      // If not authenticated, redirect to login
      if (!authLoading && !isAuthenticated) {
        router.push('/login');
      }
      
      return;
    }

    // Don't connect if already connected
    if (socket && socket.readyState === WebSocket.OPEN) {
      return;
    }

    // Don't connect if already connecting
    if (socket && (socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      setErrorType(null);
      isIntentionallyDisconnectedRef.current = false;

      const wsURL = getWebSocketURL();
      const ws = new WebSocket(wsURL, protocols);

      ws.onopen = (event) => {
        console.log('[useAuthAwareWebSocket] ✅ Connected');
        setIsConnected(true);
        setIsLoading(false);
        setError(null);
        setErrorType(null);
        reconnectAttemptsRef.current = 0;
        setSocket(ws);
        
        if (onOpen) {
          onOpen(event);
        }
      };

      ws.onmessage = (event) => {
        if (onMessage) {
          onMessage(event);
        }
      };

      ws.onerror = (event) => {
        console.error('[useAuthAwareWebSocket] ❌ WebSocket error:', event);
        
        // Create error object with proper categorization
        const wsError = createErrorFromError(event);
        const userMessage = getUserFriendlyMessage(wsError);
        
        setError(userMessage);
        setErrorType(wsError.type);
        setIsConnected(false);
        setIsLoading(false);
        
        if (onError) {
          onError(new Error(wsError.message), wsError.type);
        }
      };

      ws.onclose = (event) => {
        console.log('[useAuthAwareWebSocket] 🔌 Disconnected:', event.code, event.reason);
        setIsConnected(false);
        setIsLoading(false);
        setSocket(null);

        // Create error object from close event
        const wsError = createErrorFromCloseEvent(event);
        const userMessage = getUserFriendlyMessage(wsError);
        
        // Set error state
        if (event.code !== 1000) { // Not normal closure
          setError(userMessage);
          setErrorType(wsError.type);
        }

        // Handle auth errors - redirect to login, don't reconnect
        if (shouldRedirectToLogin(wsError)) {
          if (onError) {
            onError(new Error(wsError.message), 'auth');
          }
          router.push('/login');
          return;
        }

        if (onClose) {
          onClose(event);
        }

        // Auto-reconnect on retryable errors (not auth errors, not intentional disconnects)
        if (
          !isIntentionallyDisconnectedRef.current &&
          autoReconnect &&
          wsError.retryable &&
          reconnectAttemptsRef.current < maxReconnectAttempts &&
          event.code !== 1000 // Not normal closure
        ) {
          reconnectAttemptsRef.current += 1;
          const delay = reconnectDelay * Math.pow(2, reconnectAttemptsRef.current - 1); // Exponential backoff
          
          console.log(`[useAuthAwareWebSocket] 🔄 Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts && wsError.retryable) {
          setError('Max reconnection attempts reached. Please refresh the page.');
          setErrorType('connection');
          
          if (onError) {
            onError(new Error('Max reconnection attempts reached'), 'connection');
          }
        }
      };

      setSocket(ws);
    } catch (err: any) {
      console.error('[useAuthAwareWebSocket] ❌ Connection failed:', err);
      setError(err.message || 'Failed to connect');
      setErrorType('connection');
      setIsLoading(false);
      setIsConnected(false);
      
      if (onError) {
        onError(err, 'connection');
      }
    }
  }, [canConnect, authLoading, isAuthenticated, socket, getWebSocketURL, protocols, autoReconnect, maxReconnectAttempts, reconnectDelay, onOpen, onMessage, onClose, onError, router]);

  /**
   * Disconnect WebSocket
   */
  const disconnect = useCallback((): void => {
    isIntentionallyDisconnectedRef.current = true;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (socket) {
      socket.close(1000, 'User disconnected');
      setSocket(null);
    }
    
    setIsConnected(false);
    reconnectAttemptsRef.current = 0;
  }, [socket]);

  /**
   * Reconnect WebSocket
   */
  const reconnect = useCallback(async (): Promise<void> => {
    disconnect();
    reconnectAttemptsRef.current = 0;
    await connect();
  }, [disconnect, connect]);

  /**
   * Send message
   */
  const send = useCallback((data: string | ArrayBuffer | Blob): void => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket is not connected');
    }
    
    socket.send(data);
  }, [socket]);

  /**
   * Auto-connect when auth is ready
   */
  useEffect(() => {
    if (autoConnect && canConnect() && !socket) {
      connect();
    } else if (!canConnect() && socket) {
      // Disconnect if auth is no longer valid
      disconnect();
    }
  }, [autoConnect, canConnect, socket, connect, disconnect]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    socket,
    isConnected,
    isLoading: isLoading || authLoading, // Include auth loading state
    error,
    errorType,
    connect,
    disconnect,
    send,
    reconnect
  };
}

