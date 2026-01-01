/**
 * Message Queuing and Retry System
 * Handles message queuing for offline scenarios and retry logic
 */

import { WebSocketMessage } from './core';

export interface QueuedMessage {
  id: string;
  message: WebSocketMessage;
  priority: number;
  retryCount: number;
  maxRetries: number;
  timestamp: number;
  expiresAt: number;
}

export interface MessageQueueConfig {
  maxQueueSize: number;
  defaultRetries: number;
  retryDelay: number;
  messageTimeout: number;
  priorityLevels: {
    HIGH: number;
    NORMAL: number;
    LOW: number;
  };
}

export class MessageQueue {
  private queue: QueuedMessage[] = [];
  private config: MessageQueueConfig;
  private processing = false;

  constructor(config: Partial<MessageQueueConfig> = {}) {
    this.config = {
      maxQueueSize: 100,
      defaultRetries: 3,
      retryDelay: 1000,
      messageTimeout: 30000,
      priorityLevels: {
        HIGH: 1,
        NORMAL: 2,
        LOW: 3,
      },
      ...config,
    };
  }

  // Add message to queue
  enqueue(
    message: WebSocketMessage,
    priority: 'HIGH' | 'NORMAL' | 'LOW' = 'NORMAL',
    maxRetries?: number
  ): string {
    if (this.queue.length >= this.config.maxQueueSize) {
      throw new Error('Message queue is full');
    }

    const queuedMessage: QueuedMessage = {
      id: this.generateMessageId(),
      message,
      priority: this.config.priorityLevels[priority],
      retryCount: 0,
      maxRetries: maxRetries || this.config.defaultRetries,
      timestamp: Date.now(),
      expiresAt: Date.now() + this.config.messageTimeout,
    };

    this.queue.push(queuedMessage);
    this.sortQueue();
    
    return queuedMessage.id;
  }

  // Get next message from queue
  dequeue(): QueuedMessage | null {
    if (this.queue.length === 0) {
      return null;
    }

    const message = this.queue.shift()!;
    
    // Check if message has expired
    if (Date.now() > message.expiresAt) {
      console.warn(`Message ${message.id} has expired`);
      return this.dequeue(); // Try next message
    }

    return message;
  }

  // Mark message as successfully sent
  markSuccess(messageId: string): void {
    const index = this.queue.findIndex(msg => msg.id === messageId);
    if (index !== -1) {
      this.queue.splice(index, 1);
    }
  }

  // Mark message for retry
  markForRetry(messageId: string): boolean {
    const message = this.queue.find(msg => msg.id === messageId);
    if (!message) {
      return false;
    }

    message.retryCount++;
    
    if (message.retryCount > message.maxRetries) {
      console.error(`Message ${messageId} exceeded max retries`);
      this.removeMessage(messageId);
      return false;
    }

    // Re-queue with exponential backoff
    message.timestamp = Date.now() + (this.config.retryDelay * Math.pow(2, message.retryCount - 1));
    this.sortQueue();
    
    return true;
  }

  // Remove message from queue
  removeMessage(messageId: string): void {
    const index = this.queue.findIndex(msg => msg.id === messageId);
    if (index !== -1) {
      this.queue.splice(index, 1);
    }
  }

  // Get queue statistics
  getStats() {
    return {
      queueSize: this.queue.length,
      maxQueueSize: this.config.maxQueueSize,
      processing: this.processing,
      messagesByPriority: {
        high: this.queue.filter(msg => msg.priority === this.config.priorityLevels.HIGH).length,
        normal: this.queue.filter(msg => msg.priority === this.config.priorityLevels.NORMAL).length,
        low: this.queue.filter(msg => msg.priority === this.config.priorityLevels.LOW).length,
      },
    };
  }

  // Clear expired messages
  clearExpired(): number {
    const now = Date.now();
    const initialSize = this.queue.length;
    this.queue = this.queue.filter(msg => now <= msg.expiresAt);
    return initialSize - this.queue.length;
  }

  // Clear entire queue
  clear(): void {
    this.queue = [];
  }

  // Set processing state
  setProcessing(processing: boolean): void {
    this.processing = processing;
  }

  // Private methods
  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private sortQueue(): void {
    this.queue.sort((a, b) => {
      // Sort by priority first
      if (a.priority !== b.priority) {
        return a.priority - b.priority;
      }
      // Then by timestamp
      return a.timestamp - b.timestamp;
    });
  }
} 