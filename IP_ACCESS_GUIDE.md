# SAS API - IP-based Access Control Guide

The SAS API now uses **IP-based access control** instead of authentication tokens. Only whitelisted IP addresses can access the API endpoints.

## 🌐 Default Configuration

By default, the following IPs/networks are allowed:

- `127.0.0.1` - localhost
- `::1` - localhost IPv6
- `192.168.1.0/24` - Common local network
- `10.0.0.0/8` - Private network range
- `172.16.0.0/12` - Private network range

## 🔧 Managing IP Access

### Check Your IP

```bash
curl http://localhost:8000/api/access/my-ip
```

**Response:**

```json
{
  "success": true,
  "your_ip": "192.168.1.100",
  "is_allowed": true,
  "message": "Your IP: 192.168.1.100 (✅ Allowed)",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### List Allowed IPs

```bash
curl http://localhost:8000/api/access/allowed-ips
```

### Add New IP/Network

```bash
curl -X POST http://localhost:8000/api/access/allowed-ips \
  -H "Content-Type: application/json" \
  -d '{
    "ip_or_network": "203.0.113.0/24",
    "description": "Office network"
  }'
```

### Remove IP/Network

```bash
curl -X DELETE http://localhost:8000/api/access/allowed-ips/203.0.113.0%2F24
```

## 📡 Using the API

### Example: Get System Status

```bash
curl http://localhost:8000/api/system/status
```

### Example: Get Card Reader Status

```bash
curl http://localhost:8000/api/card-reader/status
```

### Example: Lock Machine

```bash
curl -X POST http://localhost:8000/api/machine/lock \
  -H "Content-Type: application/json" \
  -d '{"lock_code": "01", "timeout_minutes": 10}'
```

## 🔌 WebSocket Integration

WebSockets also use IP-based access control:

```javascript
// Connect to WebSocket (no token needed)
const ws = new WebSocket("ws://localhost:8000/ws/live-updates");

// Subscribe to events
ws.onopen = () => {
  ws.send(
    JSON.stringify({
      action: "subscribe",
      events: ["card_events", "meters", "machine_events"],
    })
  );
};

// Handle real-time events
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Real-time update:", data);
};
```

## 🛡️ Security Considerations

1. **Production Setup**: Change default IP ranges in production
2. **Network Security**: Use VPN or private networks for remote access
3. **Firewall**: Configure firewall rules to restrict access to port 8000
4. **Proxy**: Use reverse proxy (nginx) for additional security layers

## 🌍 Network Formats

The API supports various IP/network formats:

- **Single IP**: `192.168.1.100`
- **CIDR Notation**: `192.168.1.0/24`
- **IPv6**: `2001:db8::1` or `2001:db8::/32`

## ⚠️ Error Responses

If your IP is not whitelisted:

```json
{
  "success": false,
  "error_code": "ACCESS_DENIED",
  "message": "Access denied for IP: 203.0.113.50",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 🔄 Migration from JWT

If you were previously using JWT tokens, simply remove the `Authorization: Bearer` headers from your requests. The API will now automatically check your IP address.

### Before (JWT):

```bash
curl -H "Authorization: Bearer your_jwt_token" \
  http://localhost:8000/api/meters/all
```

### Now (IP-based):

```bash
curl http://localhost:8000/api/meters/all
```

## 📋 Available Endpoints

All endpoints are now protected by IP access control:

- **System**: `/api/system/*`
- **Meters**: `/api/meters/*`
- **Bill Acceptor**: `/api/bill-acceptor/*`
- **Card Reader**: `/api/card-reader/*`
- **Machine Control**: `/api/machine/*`
- **Access Management**: `/api/access/*`
- **WebSocket**: `/ws/live-updates`

Visit `http://localhost:8000/docs` for complete API documentation.

## 🐛 Troubleshooting

1. **403 Access Denied**: Your IP is not whitelisted

   - Check your IP: `GET /api/access/my-ip`
   - Add your IP: `POST /api/access/allowed-ips`

2. **Behind Proxy/Load Balancer**: Ensure proper headers are set

   - `X-Forwarded-For`
   - `X-Real-IP`

3. **IPv6 Issues**: Make sure IPv6 format is correct
   - Use `::1` for localhost
   - Use proper CIDR notation for networks
