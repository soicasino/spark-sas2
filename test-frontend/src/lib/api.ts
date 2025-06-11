/**
 * API Client for SAS Backend Communication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class SASApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    console.log(`Making API request to: ${url}`);

    try {
      const response = await fetch(url, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        ...options,
      });

      console.log(`Response status: ${response.status} ${response.statusText}`);

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.detail || errorMessage;
          console.error("API Error Response:", errorData);
        } catch (parseError) {
          // If we can't parse the error response, try to get text
          try {
            const errorText = await response.text();
            console.error("API Error Text:", errorText);
            errorMessage = errorText || errorMessage;
          } catch {
            console.error("Could not parse error response");
          }
        }
        throw new Error(errorMessage);
      }

      return response.json();
    } catch (error) {
      console.error(`API request failed for ${url}:`, error);
      throw error;
    }
  }

  // Card Reader API
  async getCardReaderStatus() {
    console.log(`Card Reader API - Base URL: ${this.baseUrl}`);
    return this.request("/api/card-reader/status");
  }

  async getLastCard() {
    return this.request("/api/card-reader/last-card");
  }

  async ejectCard() {
    return this.request("/api/card-reader/eject", { method: "POST" });
  }

  // Meters API
  async getAllMeters(meterType = "basic", gameId = 1) {
    return this.request(`/api/meters/all?meter_type=${meterType}&game_id=${gameId}`);
  }

  async getBasicMeters() {
    return this.request("/api/meters/basic");
  }

  async getExtendedMeters() {
    return this.request("/api/meters/extended");
  }

  async getBalance() {
    return this.request("/api/meters/balance");
  }

  async requestMeters(meterType: string) {
    return this.request("/api/meters/request", {
      method: "POST",
      body: JSON.stringify({ meter_type: meterType }),
    });
  }

  // Bill Acceptor API
  async getBillAcceptorStatus() {
    return this.request("/api/bill-acceptor/status");
  }

  async enableBillAcceptor() {
    return this.request("/api/bill-acceptor/enable", { method: "POST" });
  }

  async disableBillAcceptor() {
    return this.request("/api/bill-acceptor/disable", { method: "POST" });
  }

  async controlBillAcceptor(action: string) {
    return this.request("/api/bill-acceptor/control", {
      method: "POST",
      body: JSON.stringify({ action }),
    });
  }

  async resetBillAcceptor() {
    return this.request("/api/bill-acceptor/reset", { method: "POST" });
  }

  // Machine Control API
  async getMachineStatus() {
    return this.request("/api/machine/status");
  }

  async lockMachine() {
    return this.request("/api/machine/lock", { method: "POST" });
  }

  async unlockMachine() {
    return this.request("/api/machine/unlock", { method: "POST" });
  }

  async controlMachine(action: string, amount?: number) {
    const body: any = { action };
    if (amount !== undefined) {
      body.amount = amount;
    }
    return this.request("/api/machine/control", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  async emergencyStop() {
    return this.request("/api/machine/emergency-stop", { method: "POST" });
  }

  // System Status API
  async getSystemStatus() {
    return this.request("/api/system/status");
  }

  async getSystemHealth() {
    return this.request("/api/system/health");
  }

  // Event Management API
  async getEventStats() {
    return this.request("/api/events/stats");
  }

  async getUnsyncedEvents(eventType?: string, limit = 100) {
    const params = new URLSearchParams();
    if (eventType) params.append("event_type", eventType);
    params.append("limit", limit.toString());
    return this.request(`/api/events/unsynced?${params}`);
  }

  async getSyncStatus() {
    return this.request("/api/events/sync-status");
  }

  async forceSync() {
    return this.request("/api/events/force-sync", { method: "POST" });
  }

  async testNextJSConnection() {
    return this.request("/api/events/test-nextjs-connection", { method: "POST" });
  }

  async testGameEvent(eventType = "test_game_started") {
    return this.request(`/api/events/test-game-event?event_type=${eventType}`, { method: "POST" });
  }

  async testCardEvent(eventType = "card_inserted") {
    return this.request(`/api/events/test-card-event?event_type=${eventType}`, { method: "POST" });
  }
}

// Global API client instance
export const sasApi = new SASApiClient();

// WebSocket connection for live updates
export class SASWebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor(private url: string = `${API_BASE_URL.replace("http", "ws")}/ws/live-updates`) {}

  connect(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log("WebSocket connected");
        this.reconnectAttempts = 0;

        // Subscribe to card events and other important events
        this.send({
          type: "subscribe",
          events: ["card_events", "meters", "machine_events", "bill_events"],
        });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      this.ws.onclose = () => {
        console.log("WebSocket disconnected");
        this.attemptReconnect(onMessage, onError);
      };

      this.ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        if (onError) onError(error);
      };
    } catch (error) {
      console.error("Failed to connect WebSocket:", error);
      if (onError) onError(error as Event);
    }
  }

  private attemptReconnect(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

      setTimeout(() => {
        this.connect(onMessage, onError);
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}

// Types for API responses
export interface CardReaderStatus {
  success: boolean;
  card_inserted: boolean;
  card_number?: string;
  port_name?: string;
  reader_connected: boolean;
  formatted_display: {
    card_status: string;
    card_number: string;
    reader_status: string;
    port_name: string;
  };
  error_code?: string;
  message?: string;
  timestamp: string;
}

export interface MeterData {
  success: boolean;
  data: {
    meters: Record<string, any>;
    timestamp: string;
    game_id?: number;
    meter_type?: string;
  };
  message: string;
}

export interface BillAcceptorStatus {
  success: boolean;
  data: {
    enabled: boolean;
    status: string;
    last_bill_amount?: number;
    total_inserted?: number;
    timestamp: string;
  };
  message: string;
}

export interface EventStats {
  success: boolean;
  data: {
    is_online: boolean;
    nextjs_url: string;
    failed_attempts: number;
    unsynced_events: {
      game: number;
      card: number;
      total: number;
    };
    sync_status: any;
  };
  message: string;
}
