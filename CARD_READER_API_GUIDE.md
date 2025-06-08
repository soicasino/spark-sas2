# Card Reader API Guide

This guide explains how to use the card reader endpoints and real-time WebSocket events for detecting card insertion and removal.

## Card Reader Endpoints

### 1. Get Card Reader Status

**GET** `/api/card-reader/status`

Returns current card reader status and card information.

```bash
curl -H "Authorization: Bearer your_jwt_token" \
  http://localhost:8000/api/card-reader/status
```

**Response:**

```json
{
  "success": true,
  "card_inserted": true,
  "card_number": "12345678",
  "port_name": "/dev/ttyUSB0",
  "reader_connected": true,
  "formatted_display": {
    "card_status": "🟢 Card Inserted",
    "card_number": "12345678",
    "reader_status": "🟢 Connected",
    "port_name": "/dev/ttyUSB0"
  },
  "timestamp": "2024-01-20T15:30:45.123456"
}
```

### 2. Eject Card

**POST** `/api/card-reader/eject`

Sends an eject command to remove the currently inserted card.

```bash
curl -X POST \
  -H "Authorization: Bearer your_jwt_token" \
  http://localhost:8000/api/card-reader/eject
```

**Response:**

```json
{
  "success": true,
  "event_type": "card_ejected",
  "card_number": "12345678",
  "formatted_display": {
    "action": "🚪 Card Eject Command Sent",
    "status": "✅ Success",
    "message": "Card eject command sent successfully"
  },
  "message": "Card eject command sent successfully",
  "timestamp": "2024-01-20T15:35:10.789012"
}
```

### 3. Get Last Card Info

**GET** `/api/card-reader/last-card`

Returns information about the last detected card (whether currently inserted or not).

```bash
curl -H "Authorization: Bearer your_jwt_token" \
  http://localhost:8000/api/card-reader/last-card
```

**Response:**

```json
{
  "success": true,
  "card_inserted": false,
  "card_number": "12345678",
  "port_name": "/dev/ttyUSB0",
  "reader_connected": true,
  "formatted_display": {
    "last_card": "12345678",
    "current_status": "🔴 Not Currently Inserted",
    "reader_status": "🟢 Connected"
  },
  "timestamp": "2024-01-20T15:40:22.456789"
}
```

## Real-Time WebSocket Events

### WebSocket Connection

Connect to WebSocket for real-time card events:

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/live-updates?token=your_jwt_token");

// Subscribe to card events
ws.onopen = () => {
  ws.send(
    JSON.stringify({
      type: "subscribe",
      events: ["card_events"],
    })
  );
};
```

### Card Insertion Event

Triggered when a card is inserted into the reader:

```json
{
  "type": "card_events",
  "data": {
    "event_type": "card_inserted",
    "card_number": "12345678",
    "formatted_display": {
      "event": "🎴 Card Inserted",
      "card_number": "12345678",
      "timestamp": "15:30:45",
      "status": "🟢 Active"
    },
    "timestamp": "2024-01-20T15:30:45.123456"
  },
  "timestamp": "2024-01-20T15:30:45.123456"
}
```

### Card Removal Event

Triggered when a card is removed from the reader:

```json
{
  "type": "card_events",
  "data": {
    "event_type": "card_removed",
    "card_number": "12345678",
    "formatted_display": {
      "event": "🎴 Card Removed",
      "card_number": "12345678",
      "timestamp": "15:35:10",
      "status": "🔴 Removed"
    },
    "timestamp": "2024-01-20T15:35:10.789012"
  },
  "timestamp": "2024-01-20T15:35:10.789012"
}
```

### Card Ejection Event

Triggered when eject command is sent:

```json
{
  "type": "card_events",
  "data": {
    "event_type": "card_ejected",
    "card_number": "12345678",
    "formatted_display": {
      "action": "🚪 Card Eject Command Sent",
      "status": "✅ Success",
      "message": "Card eject command sent successfully"
    },
    "timestamp": "2024-01-20T15:35:10.789012"
  },
  "timestamp": "2024-01-20T15:35:10.789012"
}
```

## Next.js Integration Examples

### React Component for Card Reader Status

```jsx
import { useState, useEffect } from "react";

export default function CardReaderStatus() {
  const [cardStatus, setCardStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);

  // Get authentication token
  useEffect(() => {
    const getToken = async () => {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username: "admin", password: "admin123" }),
      });
      const data = await response.json();
      setToken(data.access_token);
    };
    getToken();
  }, []);

  // Fetch card reader status
  useEffect(() => {
    if (!token) return;

    const fetchStatus = async () => {
      try {
        const response = await fetch("/api/card-reader/status", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await response.json();
        setCardStatus(data);
      } catch (error) {
        console.error("Error fetching card status:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, [token]);

  const handleEjectCard = async () => {
    if (!token) return;

    try {
      const response = await fetch("/api/card-reader/eject", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json();
      console.log("Eject result:", data);
    } catch (error) {
      console.error("Error ejecting card:", error);
    }
  };

  if (loading) return <div>Loading card reader status...</div>;

  return (
    <div className="card-reader-status">
      <h2>Card Reader Status</h2>

      {cardStatus?.reader_connected ? (
        <div>
          <p>📡 {cardStatus.formatted_display.reader_status}</p>
          <p>🎴 {cardStatus.formatted_display.card_status}</p>

          {cardStatus.card_inserted && (
            <div>
              <p>Card Number: {cardStatus.card_number}</p>
              <button onClick={handleEjectCard}>🚪 Eject Card</button>
            </div>
          )}
        </div>
      ) : (
        <p>❌ Card reader not connected</p>
      )}
    </div>
  );
}
```

### Real-Time Card Events with WebSocket

```jsx
import { useState, useEffect } from "react";

export default function CardEventMonitor() {
  const [cardEvents, setCardEvents] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState("disconnected");
  const [token, setToken] = useState(null);

  // Get authentication token
  useEffect(() => {
    const getToken = async () => {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username: "admin", password: "admin123" }),
      });
      const data = await response.json();
      setToken(data.access_token);
    };
    getToken();
  }, []);

  // WebSocket connection for real-time events
  useEffect(() => {
    if (!token) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/live-updates?token=${token}`);

    ws.onopen = () => {
      setConnectionStatus("connected");
      // Subscribe to card events only
      ws.send(
        JSON.stringify({
          type: "subscribe",
          events: ["card_events"],
        })
      );
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "card_events") {
        setCardEvents((prev) => [
          {
            id: Date.now(),
            ...data.data,
          },
          ...prev.slice(0, 9), // Keep last 10 events
        ]);
      }
    };

    ws.onclose = () => setConnectionStatus("disconnected");
    ws.onerror = () => setConnectionStatus("error");

    return () => ws.close();
  }, [token]);

  return (
    <div className="card-event-monitor">
      <h2>Card Reader Events</h2>

      <div className={`connection-status ${connectionStatus}`}>Status: {connectionStatus}</div>

      <div className="events-list">
        {cardEvents.length === 0 ? (
          <p>No card events yet...</p>
        ) : (
          cardEvents.map((event) => (
            <div key={event.id} className={`event ${event.event_type}`}>
              <div className="event-header">
                <span className="event-type">{event.formatted_display.event}</span>
                <span className="timestamp">{event.formatted_display.timestamp}</span>
              </div>
              <div className="event-details">
                <p>Card: {event.card_number}</p>
                <p>{event.formatted_display.status}</p>
              </div>
            </div>
          ))
        )}
      </div>

      <style jsx>{`
        .connection-status.connected {
          color: green;
        }
        .connection-status.disconnected {
          color: red;
        }
        .connection-status.error {
          color: orange;
        }

        .event.card_inserted {
          border-left: 4px solid green;
        }
        .event.card_removed {
          border-left: 4px solid red;
        }
        .event.card_ejected {
          border-left: 4px solid orange;
        }

        .event {
          margin: 10px 0;
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }

        .event-header {
          display: flex;
          justify-content: space-between;
          font-weight: bold;
        }

        .event-details {
          margin-top: 5px;
          font-size: 0.9em;
          color: #666;
        }
      `}</style>
    </div>
  );
}
```

## Error Handling

All card reader endpoints use the standardized error response format:

```json
{
  "success": false,
  "error_code": "SAS_007",
  "message": "Failed to get card reader status: Card reader not initialized",
  "timestamp": "2024-01-20T15:30:45.123456"
}
```

### Common Error Codes

- `SAS_007`: Failed to get card reader status
- `SAS_008`: Card reader not initialized (for eject operations)
- `SAS_009`: Card reader not connected
- `SAS_010`: Failed to send card eject command
- `SAS_011`: Failed to eject card (general error)
- `SAS_012`: Failed to get last card info
- `API_003`: Failed to get card reader status (API level)
- `API_004`: Failed to eject card (API level)
- `API_005`: Failed to get last card info (API level)

## Testing

### Manual Testing with curl

```bash
# 1. Login to get token
TOKEN=$(curl -s -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  http://localhost:8000/api/auth/login | jq -r '.access_token')

# 2. Check card reader status
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/card-reader/status | jq '.'

# 3. Get last card info
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/card-reader/last-card | jq '.'

# 4. Eject card (if one is inserted)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/card-reader/eject | jq '.'
```

### WebSocket Testing with wscat

```bash
# Install wscat if not already installed
npm install -g wscat

# Connect and subscribe to card events
wscat -c "ws://localhost:8000/ws/live-updates?token=your_jwt_token"

# Send subscription message
{"type": "subscribe", "events": ["card_events"]}
```

## Integration Notes

1. **Authentication Required**: All endpoints require JWT authentication
2. **Real-Time Updates**: Use WebSocket events for immediate card detection
3. **Polling Alternative**: For systems that can't use WebSockets, poll the status endpoint
4. **Error Handling**: Always check the `success` field in responses
5. **Card Reader Hardware**: Ensure card reader is connected and properly configured
6. **Thread Safety**: All operations are thread-safe with the existing SAS communication

## Production Considerations

1. **Security**: Change default admin credentials before production
2. **Rate Limiting**: Consider implementing rate limiting for API endpoints
3. **Logging**: Monitor card reader events for security and debugging
4. **Hardware Monitoring**: Implement alerts for card reader disconnections
5. **Error Recovery**: Handle card reader communication failures gracefully
