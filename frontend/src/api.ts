import axios, { AxiosInstance } from 'axios';
import { GenerationResult, StreamMessage } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await this.client.get('/api/health');
    return response.data;
  }

  async generateCode(requirements: string): Promise<GenerationResult> {
    const response = await this.client.post('/api/generate', {
      requirements,
    });
    return response.data;
  }

  async generateCodeStream(
    requirements: string,
    onMessage: (message: StreamMessage) => void,
    onError: (error: string) => void,
    onComplete: () => void
  ): Promise<void> {
    try {
      const eventSource = new EventSource(
        `${API_BASE_URL}/api/generate-stream?requirements=${encodeURIComponent(requirements)}`
      );
      let streamOpened = false;
      let streamCompleted = false;

      eventSource.addEventListener('open', () => {
        streamOpened = true;
      });

      eventSource.addEventListener('message', (event) => {
        try {
          const message = JSON.parse(event.data) as StreamMessage;
          onMessage(message);
          if (message.type === 'complete') {
            streamCompleted = true;
            eventSource.close();
            onComplete();
          }
        } catch (e) {
          console.error('Failed to parse message:', e);
        }
      });

      eventSource.addEventListener('error', (event) => {
        eventSource.close();
        if (!streamCompleted && !streamOpened) {
          const errorMessage = (event as ErrorEvent).message || 'Stream connection failed';
          onError(errorMessage);
        }
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      onError(errorMessage);
    }
  }
}

export const apiClient = new APIClient();
