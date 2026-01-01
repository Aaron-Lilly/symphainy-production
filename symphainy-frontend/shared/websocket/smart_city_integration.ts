/**
 * Smart City Integration for WebSocket Client
 * Integrates WebSocket with Smart City components
 */

import { SmartCityWebSocketCore, WebSocketMessage } from './core';
import { getGlobalConfig } from '../config';

// Smart City component interfaces
export interface TrafficCopMessage {
  type: 'traffic_cop';
  action: 'route' | 'validate' | 'create_session';
  data: any;
  sessionId?: string;
  timestamp: number;
}

export interface ArchiveMessage {
  type: 'archive';
  action: 'store' | 'retrieve' | 'update' | 'delete';
  data: any;
  sessionId?: string;
  timestamp: number;
}

export interface ConductorMessage {
  type: 'conductor';
  action: 'orchestrate' | 'get_status' | 'workflow';
  data: any;
  sessionId?: string;
  timestamp: number;
}

export interface PostOfficeMessage {
  type: 'post_office';
  action: 'send' | 'deliver' | 'queue';
  data: any;
  sessionId?: string;
  timestamp: number;
}

export type SmartCityMessage = 
  | TrafficCopMessage 
  | ArchiveMessage 
  | ConductorMessage 
  | PostOfficeMessage;

export class SmartCityWebSocketIntegration {
  private wsCore: SmartCityWebSocketCore;
  private config = getGlobalConfig();

  constructor(wsCore: SmartCityWebSocketCore) {
    this.wsCore = wsCore;
  }

  // Traffic Cop integration
  async routeSession(sessionId: string, destination: string): Promise<void> {
    const message: TrafficCopMessage = {
      type: 'traffic_cop',
      action: 'route',
      data: { destination, sessionId },
      sessionId,
      timestamp: Date.now(),
    };
    await this.wsCore.sendMessage(message);
  }

  async validateSession(sessionId: string): Promise<boolean> {
    const message: TrafficCopMessage = {
      type: 'traffic_cop',
      action: 'validate',
      data: { sessionId },
      sessionId,
      timestamp: Date.now(),
    };
    await this.wsCore.sendMessage(message);
    
    // Return promise that resolves when validation response is received
    return new Promise((resolve) => {
      const unsubscribe = this.wsCore.onMessage((response) => {
        if (response.type === 'traffic_cop' && response.data.sessionId === sessionId) {
          unsubscribe();
          resolve(response.data.isValid || false);
        }
      });
    });
  }

  async createSession(sessionData: any): Promise<string> {
    const message: TrafficCopMessage = {
      type: 'traffic_cop',
      action: 'create_session',
      data: sessionData,
      timestamp: Date.now(),
    };
    await this.wsCore.sendMessage(message);
    
    // Return promise that resolves when session creation response is received
    return new Promise((resolve) => {
      const unsubscribe = this.wsCore.onMessage((response) => {
        if (response.type === 'traffic_cop' && response.data.sessionToken) {
          unsubscribe();
          resolve(response.data.sessionToken);
        }
      });
    });
  }

  // Archive integration
  async storeSession(sessionId: string, sessionData: any): Promise<void> {
    const message: ArchiveMessage = {
      type: 'archive',
      action: 'store',
      data: { sessionId, sessionData },
      sessionId,
      timestamp: Date.now(),
    };
    await this.wsCore.sendMessage(message);
  }

  async retrieveSession(sessionId: string): Promise<any> {
    const message: ArchiveMessage = {
      type: 'archive',
      action: 'retrieve',
      data: { sessionId },
      sessionId,
      timestamp: Date.now(),
    };
    await this.wsCore.sendMessage(message);
    
    // Return promise that resolves when retrieval response is received
    return new Promise((resolve) => {
      const unsubscribe = this.wsCore.onMessage((response) => {
        if (response.type === 'archive' && response.data.sessionId === sessionId) {
          unsubscribe();
          resolve(response.data.sessionData);
        }
      });
    });
  }

  async updateSession(sessionId: string, sessionData: any): Promise<void> {
    const message: ArchiveMessage = {
      type: 'archive',
      action: 'update',
      data: { sessionId, sessionData },
      sessionId,
      timestamp: Date.now(),
    };
    await this.wsCore.sendMessage(message);
  }

  async deleteSession(sessionId: string): Promise<void> {
    const message: ArchiveMessage = {
      type: 'archive',
      action: 'delete',
      data: { sessionId },
      sessionId,
      timestamp: Date.now(),
    };
    await this.wsCore.sendMessage(message);
  }

  // Conductor integration
  async orchestrateSession(sessionId: string, workflow: string): Promise<void> {
    const message: ConductorMessage = {
      type: 'conductor',
      action: 'orchestrate',
      data: { sessionId, workflow },
      sessionId,
      timestamp: Date.now(),
    };
    await this.wsCore.sendMessage(message);
  }

  async getSessionStatus(sessionId: string): Promise<string> {
    const message: ConductorMessage = {
      type: 'conductor',
      action: 'get_status',
      data: { sessionId },
      sessionId,
      timestamp: Date.now(),
    };
    await this.wsCore.sendMessage(message);
    
    // Return promise that resolves when status response is received
    return new Promise((resolve) => {
      const unsubscribe = this.wsCore.onMessage((response) => {
        if (response.type === 'conductor' && response.data.sessionId === sessionId) {
          unsubscribe();
          resolve(response.data.status || 'unknown');
        }
      });
    });
  }

  async startWorkflow(sessionId: string, workflowType: string): Promise<void> {
    const message: ConductorMessage = {
      type: 'conductor',
      action: 'workflow',
      data: { sessionId, workflowType },
      sessionId,
      timestamp: Date.now(),
    };
    await this.wsCore.sendMessage(message);
  }

  // Post Office integration
  async sendMessage(sessionId: string, messageData: any): Promise<void> {
    const message: PostOfficeMessage = {
      type: 'post_office',
      action: 'send',
      data: { sessionId, messageData },
      sessionId,
      timestamp: Date.now(),
    };
    await this.wsCore.sendMessage(message);
  }

  async deliverMessage(sessionId: string, messageId: string): Promise<void> {
    const message: PostOfficeMessage = {
      type: 'post_office',
      action: 'deliver',
      data: { sessionId, messageId },
      sessionId,
      timestamp: Date.now(),
    };
    await this.wsCore.sendMessage(message);
  }

  async queueMessage(sessionId: string, messageData: any): Promise<void> {
    const message: PostOfficeMessage = {
      type: 'post_office',
      action: 'queue',
      data: { sessionId, messageData },
      sessionId,
      timestamp: Date.now(),
    };
    await this.wsCore.sendMessage(message);
  }
} 