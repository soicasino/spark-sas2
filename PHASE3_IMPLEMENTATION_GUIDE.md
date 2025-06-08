# 🚀 Phase 3: Advanced Features Implementation Guide

## ✅ **Phase 3 Complete Implementation**

Phase 3 adds **real-time capabilities**, **authentication**, and **enterprise-grade error handling** to your SAS FastAPI integration.

---

## 🔗 **3.1 WebSocket Integration - COMPLETED ✅**

### **Real-time Data Streaming**

Your Next.js application can now receive live updates from the slot machine without polling!

#### **Available WebSocket Events:**

- `meters` - Live meter updates (balance, games played, etc.)
- `machine_events` - Lock/unlock/restart events
- `bill_events` - Bill acceptor enable/disable events
- `system_status` - Connection status, health checks

#### **Connect from Next.js:**

```javascript
// Connect to WebSocket with authentication
const ws = new WebSocket("ws://localhost:8000/ws/live-updates?token=your_jwt_token");

// Subscribe to specific events
ws.onopen = () => {
  ws.send(
    JSON.stringify({
      action: "subscribe",
      events: ["meters", "machine_events"],
    })
  );
};

// Handle real-time updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Live update:", data);

  // Update your React state
  if (data.event_type === "meters") {
    setMeters(data.data.meters);
    setFormattedDisplay(data.data.formatted_display);
  }
};
```

#### **WebSocket Endpoints:**

- `WS /ws/live-updates` - Real-time data stream
- `GET /ws/info` - WebSocket connection info

---

## 🔐 **3.2 Authentication & Authorization - COMPLETED ✅**

### **JWT-based Security**

Secure your SAS API with industry-standard JWT authentication.

#### **Authentication Endpoints:**

- `POST /api/auth/login` - Get access token
- `POST /api/auth/refresh` - Refresh expired token
- `POST /api/auth/logout` - Invalidate token
- `GET /api/auth/me` - Get user profile

#### **Login from Next.js:**

```javascript
// Login and get JWT token
const response = await fetch("http://localhost:8000/api/auth/login", {
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
  },
  body: new URLSearchParams({
    username: "admin",
    password: "admin123", // Change default credentials!
  }),
});

const { access_token, refresh_token } = await response.json();

// Store tokens securely
localStorage.setItem("access_token", access_token);
localStorage.setItem("refresh_token", refresh_token);

// Use token for API calls
const metersResponse = await fetch("http://localhost:8000/api/meters/basic", {
  headers: {
    Authorization: `Bearer ${access_token}`,
  },
});
```

#### **Protected Endpoints:**

All API endpoints now require authentication. Include the JWT token in the `Authorization` header.

#### **Default Credentials (CHANGE IN PRODUCTION!):**

- Username: `admin`
- Password: `admin123`

---

## 🛡️ **3.3 Enhanced Error Handling - COMPLETED ✅**

### **Structured Error Responses**

Professional error handling with standardized error codes and detailed logging.

#### **Error Response Format:**

```json
{
  "success": false,
  "message": "Authentication failed",
  "timestamp": "2024-01-15T10:30:45.123456",
  "error_code": "AUTH_001",
  "details": {
    "reason": "Invalid credentials"
  }
}
```

#### **Error Code Categories:**

- **AUTH_xxx** - Authentication errors
- **SAS_xxx** - SAS communication errors
- **API_xxx** - Request validation errors
- **SYS_xxx** - System errors
- **WS_xxx** - WebSocket errors

#### **Error Handling in Next.js:**

```javascript
const handleApiCall = async () => {
  try {
    const response = await fetch("/api/meters/basic");
    const data = await response.json();

    if (!data.success) {
      // Handle structured errors
      switch (data.error_code) {
        case "AUTH_001":
          // Redirect to login
          router.push("/login");
          break;
        case "SAS_002":
          // Show SAS communication error
          setError("Slot machine communication failed");
          break;
        default:
          setError(data.message);
      }
      return;
    }

    // Success - use the data
    setMeters(data.meters);
  } catch (error) {
    setError("Network error");
  }
};
```

---

## 🔧 **Configuration & Setup**

### **Environment Variables**

Create a `.env` file in your project root:

```bash
# Security (REQUIRED - Change in production!)
SECRET_KEY=your-super-secret-key-change-this-now
DEFAULT_USERNAME=admin
DEFAULT_PASSWORD=admin123

# Optional Settings
DEBUG=true
LOG_LEVEL=INFO
```

### **Install Dependencies**

```bash
pip install -r requirements.txt
```

### **Run the Enhanced API**

```bash
python run_api.py
```

### **Access Points:**

- **API Documentation**: http://localhost:8000/docs
- **WebSocket Test**: http://localhost:8000/ws/info
- **Health Check**: http://localhost:8000/health
- **Login**: POST http://localhost:8000/api/auth/login

---

## 📊 **Real-time Dashboard Example**

Here's a complete React component example for a real-time SAS dashboard:

```jsx
import { useState, useEffect } from "react";

export default function SASRealtimeDashboard() {
  const [meters, setMeters] = useState({});
  const [status, setStatus] = useState("disconnected");
  const [token, setToken] = useState(null);

  // Authentication
  useEffect(() => {
    const login = async () => {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username: "admin", password: "admin123" }),
      });
      const data = await response.json();
      setToken(data.access_token);
    };
    login();
  }, []);

  // WebSocket connection
  useEffect(() => {
    if (!token) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/live-updates?token=${token}`);

    ws.onopen = () => {
      setStatus("connected");
      ws.send(
        JSON.stringify({
          action: "subscribe",
          events: ["meters", "system_status"],
        })
      );
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.event_type === "meters") {
        setMeters(data.data.formatted_display || {});
      }
    };

    ws.onclose = () => setStatus("disconnected");

    return () => ws.close();
  }, [token]);

  return (
    <div className="p-6">
      <h1>SAS Real-time Dashboard</h1>
      <div className={`status ${status}`}>Status: {status}</div>

      <div className="meters-grid">
        {Object.entries(meters).map(([key, value]) => (
          <div key={key} className="meter-card">
            <h3>{key.replace("_", " ").toUpperCase()}</h3>
            <p>{value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🎯 **Next Steps (Phase 4)**

Phase 3 is complete! Consider these enhancements for Phase 4:

1. **Advanced Analytics** - Historical data tracking
2. **Multi-machine Support** - Handle multiple slot machines
3. **Audit Logging** - Compliance and security logs
4. **Performance Monitoring** - Metrics and alerting
5. **Mobile App Support** - React Native integration

---

## ⚠️ **Production Checklist**

Before deploying to production:

- [ ] Change default username/password
- [ ] Set strong SECRET_KEY
- [ ] Configure HTTPS/WSS
- [ ] Set up proper CORS origins
- [ ] Enable rate limiting
- [ ] Configure log rotation
- [ ] Set up monitoring/alerts

**Your SAS system now has enterprise-grade real-time capabilities!** 🎉
