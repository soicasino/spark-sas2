# 🚀 Complete SAS FastAPI Endpoint Reference

## ✅ **Consistent Response Format**

**Every endpoint** now returns both **raw data** and **formatted display values** for immediate use in your Next.js application.

### 📋 **Standard Response Structure**

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:45.123456",
  "execution_time_ms": 1250.5,
  "status": "success",

  // Raw data for calculations
  "data_section": {
    "raw_values": "for calculations and logic"
  },

  // Ready-to-display formatted strings
  "formatted_display": {
    "display_values": "ready for UI with icons, currency, etc."
  }
}
```

---

## 📊 **Meter Endpoints**

### `GET /api/meters/basic`

**Returns**: Basic meter set with money formatting

```json
{
  "success": true,
  "message": "Successfully retrieved 8 meter values",
  "meter_type": "basic",
  "status": "success",
  "meters": {
    "total_turnover": 152450.75,
    "total_win": 142800.25,
    "current_credits": 125.5,
    "games_played": 1542
  },
  "formatted_display": {
    "total_turnover": "152,450.75 TL",
    "total_win": "142,800.25 TL",
    "current_credits": "125.50 TL",
    "games_played": "1,542"
  }
}
```

### `GET /api/meters/extended`

**Returns**: Extended meter set

### `GET /api/meters/all`

**Returns**: All available meters

### `GET /api/meters/balance`

**Returns**: Current balance information

```json
{
  "success": true,
  "status": "success",
  "balance": {
    "cashable_amount": 1250.75,
    "restricted_amount": 500.0,
    "nonrestricted_amount": 250.25,
    "total_balance": 2001.0
  },
  "formatted_display": {
    "cashable_amount": "1,250.75 TL",
    "restricted_amount": "500.00 TL",
    "nonrestricted_amount": "250.25 TL",
    "total_balance": "2,001.00 TL"
  },
  "message": "Balance retrieved successfully"
}
```

---

## 🖥️ **System Status Endpoints**

### `GET /api/system/status`

**Returns**: Complete system status with visual indicators

```json
{
  "success": true,
  "status": "success",
  "system": {
    "sas_connected": true,
    "last_communication": "2024-01-15T10:30:45.123456",
    "asset_number": "12345678",
    "sas_version": "1.12",
    "port_info": "/dev/ttyUSB0",
    "service_running": true,
    "initialized": true,
    "sas_address": "01",
    "device_type": 8
  },
  "formatted_display": {
    "connection_status": "🟢 Connected",
    "last_communication": "Last Contact: 2 minutes ago",
    "asset_number": "Asset #: 12345678",
    "port_info": "Port: /dev/ttyUSB0",
    "service_status": "✅ Running",
    "initialization": "✅ Ready",
    "sas_info": "SAS 01 (Type 8)"
  },
  "message": "System status retrieved successfully"
}
```

### `GET /api/system/sas-version`

**Returns**: SAS version information

```json
{
  "success": true,
  "status": "success",
  "version_info": {
    "command_sent": true,
    "sas_address": "01",
    "device_type_id": 8,
    "port_name": "/dev/ttyUSB0",
    "baud_rate": 19200
  },
  "formatted_display": {
    "sas_address": "Address: 01",
    "device_type": "Device Type: 8",
    "connection": "Port: /dev/ttyUSB0 @ 19200 baud",
    "status": "✅ SAS Version Request Sent"
  },
  "message": "SAS version request sent successfully"
}
```

### `GET /api/system/asset-number`

**Returns**: Asset number information

```json
{
  "success": true,
  "status": "success",
  "asset_info": {
    "command_sent": true,
    "asset_number": "12345678",
    "sas_address": "01",
    "port_info": "/dev/ttyUSB0"
  },
  "formatted_display": {
    "asset_number": "Asset #: 12345678",
    "sas_address": "SAS Address: 01",
    "port": "Connected to: /dev/ttyUSB0",
    "status": "✅ Asset Number Request Sent"
  },
  "message": "Asset number request sent successfully"
}
```

---

## 💵 **Bill Acceptor Endpoints**

### `POST /api/bill-acceptor/enable`

**Returns**: Bill acceptor enabled confirmation

```json
{
  "success": true,
  "status": "success",
  "bill_acceptor": {
    "action": "enabled",
    "enabled": true,
    "is_open": 1,
    "device_type": 1
  },
  "formatted_display": {
    "action": "✅ Bill Acceptor Enabled",
    "status": "Status: ENABLED",
    "device": "Device Type: 1",
    "operation": "Enable command sent successfully"
  },
  "message": "Bill acceptor enabled successfully"
}
```

### `POST /api/bill-acceptor/disable`

**Returns**: Bill acceptor disabled confirmation

```json
{
  "success": true,
  "status": "success",
  "bill_acceptor": {
    "action": "disabled",
    "enabled": false,
    "is_open": 0,
    "device_type": 1
  },
  "formatted_display": {
    "action": "🚫 Bill Acceptor Disabled",
    "status": "Status: DISABLED",
    "device": "Device Type: 1",
    "operation": "Disable command sent successfully"
  },
  "message": "Bill acceptor disabled successfully"
}
```

---

## 🔐 **Machine Control Endpoints**

### `POST /api/machine/lock`

**Returns**: Machine lock confirmation

```json
{
  "success": true,
  "status": "success",
  "machine_control": {
    "action": "lock",
    "locked": true,
    "sas_address": "01",
    "command_sent": true
  },
  "formatted_display": {
    "action": "🔒 Machine Locked",
    "status": "Status: LOCKED",
    "sas_info": "SAS Address: 01",
    "operation": "Lock command sent successfully"
  },
  "message": "Machine lock command sent successfully"
}
```

### `POST /api/machine/unlock`

**Returns**: Machine unlock confirmation

```json
{
  "success": true,
  "status": "success",
  "machine_control": {
    "action": "unlock",
    "locked": false,
    "sas_address": "01",
    "command_sent": true
  },
  "formatted_display": {
    "action": "🔓 Machine Unlocked",
    "status": "Status: UNLOCKED",
    "sas_info": "SAS Address: 01",
    "operation": "Unlock command sent successfully"
  },
  "message": "Machine unlock command sent successfully"
}
```

### `POST /api/machine/restart`

**Returns**: Machine restart confirmation

```json
{
  "success": true,
  "status": "success",
  "machine_control": {
    "action": "restart",
    "restart_initiated": true,
    "sas_address": "01",
    "command_sent": true
  },
  "formatted_display": {
    "action": "🔄 Machine Restart Initiated",
    "status": "Status: RESTARTING",
    "sas_info": "SAS Address: 01",
    "operation": "Restart command sent successfully",
    "warning": "⚠️ Machine will be unavailable during restart"
  },
  "message": "Machine restart command sent successfully"
}
```

---

## 🎯 **Next.js Usage Examples**

### **Display Formatted Values**

```typescript
const MetersDisplay = () => {
  const [metersData, setMetersData] = useState(null);

  const fetchMeters = async () => {
    const response = await fetch("http://localhost:8000/api/meters/basic");
    const data = await response.json();

    if (data.success) {
      // Use formatted_display for immediate UI display
      console.log("Turnover:", data.formatted_display.total_turnover); // "152,450.75 TL"
      console.log("Credits:", data.formatted_display.current_credits); // "125.50 TL"

      // Use raw meters for calculations
      const profit = data.meters.total_turnover - data.meters.total_win;

      setMetersData(data);
    }
  };

  return (
    <div>
      {metersData && (
        <>
          <h3>💰 {metersData.formatted_display.total_turnover}</h3>
          <p>🎮 {metersData.formatted_display.games_played}</p>
        </>
      )}
    </div>
  );
};
```

### **Machine Control Actions**

```typescript
const MachineControls = () => {
  const [status, setStatus] = useState("");

  const lockMachine = async () => {
    const response = await fetch("http://localhost:8000/api/machine/lock", {
      method: "POST",
    });
    const data = await response.json();

    if (data.success) {
      // Display formatted status
      setStatus(data.formatted_display.action); // "🔒 Machine Locked"
    }
  };

  return (
    <div>
      <button onClick={lockMachine}>Lock Machine</button>
      <p>{status}</p>
    </div>
  );
};
```

### **System Status Dashboard**

```typescript
const SystemDashboard = () => {
  const [systemStatus, setSystemStatus] = useState(null);

  const fetchStatus = async () => {
    const response = await fetch("http://localhost:8000/api/system/status");
    const data = await response.json();

    if (data.success) {
      setSystemStatus(data);
    }
  };

  return (
    <div className="dashboard">
      {systemStatus && (
        <>
          <div className="status-card">
            <h3>{systemStatus.formatted_display.connection_status}</h3>
            <p>{systemStatus.formatted_display.last_communication}</p>
            <p>{systemStatus.formatted_display.asset_number}</p>
          </div>
        </>
      )}
    </div>
  );
};
```

---

## 🚀 **Benefits of This Approach**

### ✅ **For Frontend Development**

- **Zero formatting needed** - values ready for display
- **Icons and symbols included** - consistent UI elements
- **Consistent structure** - same pattern across all endpoints
- **Type safety** - predictable response format

### ✅ **For Data Processing**

- **Raw numeric values** - for calculations and logic
- **Structured data** - easy to process programmatically
- **Error handling** - consistent error response format
- **Metadata included** - execution times, timestamps, etc.

### ✅ **For Debugging**

- **Human readable** - formatted values easy to verify
- **Complete context** - raw data + display format
- **Status indicators** - visual feedback on operations
- **Detailed messages** - clear success/error descriptions

---

## 📝 **API Base URL**

- **Development**: `http://localhost:8000`
- **Documentation**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

All endpoints follow this consistent pattern for maximum developer experience! 🎉
