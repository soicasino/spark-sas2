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

    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: "Network error" }));
      throw new Error(errorData.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Card Reader API
  async getCardReaderStatus() {
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
}

// Types for API responses
export interface CardReaderStatus {
  success: boolean;
  data: {
    status: string;
    card_present: boolean;
    card_number?: string;
    last_event?: string;
    timestamp: string;
  };
  message: string;
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
