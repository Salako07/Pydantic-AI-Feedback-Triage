import type { Feedback } from '../types';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export type WebSocketMessageHandler = (feedback: Feedback) => void;

export class FeedbackWebSocket {
  private ws: WebSocket | null = null;
  private handlers: WebSocketMessageHandler[] = [];
  private reconnectInterval = 3000;
  private reconnectTimer: number | null = null;

  connect(): void {
    try {
      this.ws = new WebSocket(`${WS_BASE_URL}/ws/feedbacks`);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        if (this.reconnectTimer) {
          clearTimeout(this.reconnectTimer);
          this.reconnectTimer = null;
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'feedbacks:new' && message.data) {
            this.handlers.forEach(handler => handler(message.data));
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.scheduleReconnect();
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect(): void {
    if (!this.reconnectTimer) {
      this.reconnectTimer = window.setTimeout(() => {
        console.log('Attempting to reconnect WebSocket...');
        this.connect();
      }, this.reconnectInterval);
    }
  }

  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  subscribe(handler: WebSocketMessageHandler): () => void {
    this.handlers.push(handler);
    return () => {
      this.handlers = this.handlers.filter(h => h !== handler);
    };
  }

  send(data: unknown): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}

export const feedbackWebSocket = new FeedbackWebSocket();
