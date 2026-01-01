/**
 * Connection Management
 * Handles WebSocket connection pooling and health monitoring
 */

import { SmartCityWebSocketCore } from './core';
import { getGlobalConfig } from '../config';

export interface ConnectionHealth {
  isHealthy: boolean;
  latency: number;
  lastHeartbeat: number;
  errorCount: number;
  reconnectCount: number;
}

export interface ConnectionPoolConfig {
  maxConnections: number;
  healthCheckInterval: number;
  maxLatency: number;
  maxErrors: number;
}

export class ConnectionManager {
  private connections: Map<string, SmartCityWebSocketCore> = new Map();
  private healthData: Map<string, ConnectionHealth> = new Map();
  private config = getGlobalConfig();
  private poolConfig: ConnectionPoolConfig;
  private healthCheckInterval: NodeJS.Timeout | null = null;

  constructor(poolConfig: Partial<ConnectionPoolConfig> = {}) {
    this.poolConfig = {
      maxConnections: 5,
      healthCheckInterval: 30000,
      maxLatency: 1000,
      maxErrors: 3,
      ...poolConfig,
    };
    this.startHealthMonitoring();
  }

  // Get or create connection
  async getConnection(connectionId: string): Promise<SmartCityWebSocketCore> {
    if (this.connections.has(connectionId)) {
      const connection = this.connections.get(connectionId)!;
      if (connection.isConnected()) {
        return connection;
      }
    }

    if (this.connections.size >= this.poolConfig.maxConnections) {
      throw new Error('Connection pool is full');
    }

    const connection = new SmartCityWebSocketCore();
    await connection.connect();
    
    this.connections.set(connectionId, connection);
    this.healthData.set(connectionId, {
      isHealthy: true,
      latency: 0,
      lastHeartbeat: Date.now(),
      errorCount: 0,
      reconnectCount: 0,
    });

    // Set up connection monitoring
    this.setupConnectionMonitoring(connectionId, connection);

    return connection;
  }

  // Release connection
  releaseConnection(connectionId: string): void {
    const connection = this.connections.get(connectionId);
    if (connection) {
      connection.disconnect();
      this.connections.delete(connectionId);
      this.healthData.delete(connectionId);
    }
  }

  // Get connection health
  getConnectionHealth(connectionId: string): ConnectionHealth | null {
    return this.healthData.get(connectionId) || null;
  }

  // Get all connection health data
  getAllConnectionHealth(): Map<string, ConnectionHealth> {
    return new Map(this.healthData);
  }

  // Check if connection is healthy
  isConnectionHealthy(connectionId: string): boolean {
    const health = this.healthData.get(connectionId);
    if (!health) return false;

    const now = Date.now();
    const timeSinceHeartbeat = now - health.lastHeartbeat;
    
    return health.isHealthy && 
           health.errorCount < this.poolConfig.maxErrors &&
           timeSinceHeartbeat < this.poolConfig.healthCheckInterval * 2;
  }

  // Force health check
  async performHealthCheck(connectionId: string): Promise<boolean> {
    const connection = this.connections.get(connectionId);
    if (!connection) return false;

    const startTime = Date.now();
    
    try {
      await connection.sendMessage({
        type: 'health_check',
        data: { timestamp: startTime },
        timestamp: startTime,
      });
      
      const latency = Date.now() - startTime;
      const health = this.healthData.get(connectionId)!;
      
      health.latency = latency;
      health.lastHeartbeat = Date.now();
      health.isHealthy = latency < this.poolConfig.maxLatency;
      
      return health.isHealthy;
    } catch (error) {
      const health = this.healthData.get(connectionId)!;
      health.errorCount++;
      health.isHealthy = false;
      return false;
    }
  }

  // Clean up unhealthy connections
  cleanupUnhealthyConnections(): number {
    let cleanedCount = 0;
    
    for (const [connectionId, health] of Array.from(this.healthData.entries())) {
      if (!this.isConnectionHealthy(connectionId)) {
        this.releaseConnection(connectionId);
        cleanedCount++;
      }
    }
    
    return cleanedCount;
  }

  // Get connection pool statistics
  getPoolStats() {
    return {
      totalConnections: this.connections.size,
      maxConnections: this.poolConfig.maxConnections,
      healthyConnections: Array.from(this.healthData.values()).filter(h => h.isHealthy).length,
      unhealthyConnections: Array.from(this.healthData.values()).filter(h => !h.isHealthy).length,
    };
  }

  // Shutdown all connections
  shutdown(): void {
    this.stopHealthMonitoring();
    
    for (const [connectionId] of Array.from(this.connections.entries())) {
      this.releaseConnection(connectionId);
    }
  }

  // Private methods
  private setupConnectionMonitoring(connectionId: string, connection: SmartCityWebSocketCore): void {
    // Monitor connection state
    connection.onConnect(() => {
      const health = this.healthData.get(connectionId)!;
      health.reconnectCount++;
      health.errorCount = 0;
      health.isHealthy = true;
    });

    connection.onDisconnect(() => {
      const health = this.healthData.get(connectionId)!;
      health.isHealthy = false;
    });

    connection.onError((error) => {
      const health = this.healthData.get(connectionId)!;
      health.errorCount++;
      health.isHealthy = false;
    });
  }

  private startHealthMonitoring(): void {
    this.healthCheckInterval = setInterval(() => {
      this.performHealthChecks();
    }, this.poolConfig.healthCheckInterval);
  }

  private stopHealthMonitoring(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
  }

  private async performHealthChecks(): Promise<void> {
    const healthChecks = Array.from(this.connections.keys()).map(async (connectionId) => {
      await this.performHealthCheck(connectionId);
    });
    
    await Promise.all(healthChecks);
    this.cleanupUnhealthyConnections();
  }
} 