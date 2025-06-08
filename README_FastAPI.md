# SAS FastAPI Integration

This project integrates your existing SAS (Slot Accounting System) communication code with FastAPI to provide REST API endpoints for your Next.js application.

## Architecture Overview

### Phase 1 & 2 Implementation Complete ✅

- **SAS Web Service**: Thread-safe wrapper around your existing SAS communication
- **FastAPI Application**: RESTful API with comprehensive endpoints
- **Request/Response Models**: Pydantic models for type safety and validation
- **Routers**: Organized endpoints for different functionalities

## Project Structure

```
├── main.py                     # FastAPI application entry point
├── sas_web_service.py         # Thread-safe SAS wrapper service
├── run_api.py                 # Server launcher script
├── requirements.txt           # Dependencies
├── models/
│   ├── __init__.py
│   ├── requests.py            # Pydantic request models
│   └── responses.py           # Pydantic response models
├── routers/
│   ├── __init__.py
│   ├── system_status.py       # System health and info endpoints
│   ├── meters.py              # Meter reading endpoints
│   ├── bill_acceptor.py       # Bill acceptor control endpoints
│   └── machine_control.py     # Machine lock/unlock endpoints
└── [your existing SAS files]
```

## Available API Endpoints

### System Status & Information

- `GET /api/system/status` - Comprehensive system status
- `GET /api/system/health` - Simple health check
- `GET /api/system/asset-number` - Get machine asset number
- `GET /api/system/sas-version` - Get SAS protocol version
- `GET /api/system/ports` - Port information

### Meters & Balance

- `GET /api/meters/basic` - Basic meters (turnover, win, games played)
- `GET /api/meters/extended` - Extended meters with AFT, bonus, etc.
- `GET /api/meters/balance` - Current balance information
- `GET /api/meters/all?meter_type=basic&game_id=1` - Flexible meter requests
- `POST /api/meters/request` - POST request with JSON body

### Bill Acceptor Control

- `POST /api/bill-acceptor/enable` - Enable bill acceptor
- `POST /api/bill-acceptor/disable` - Disable bill acceptor
- `POST /api/bill-acceptor/control` - Control with JSON body
- `GET /api/bill-acceptor/status` - Get bill acceptor status
- `POST /api/bill-acceptor/reset` - Reset bill acceptor

### Machine Control

- `POST /api/machine/lock` - Lock the machine
- `POST /api/machine/unlock` - Unlock the machine
- `POST /api/machine/control` - Control with JSON body
- `GET /api/machine/status` - Get machine status
- `POST /api/machine/restart` - Restart machine (placeholder)
- `POST /api/machine/emergency-stop` - Emergency stop

### Documentation & Overview

- `GET /` - API information and status
- `GET /api` - Detailed endpoint overview
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation
- `GET /health` - Simple health check

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the FastAPI Server

#### Development Mode (auto-reload)

```bash
python run_api.py
```

#### Production Mode

```bash
python run_api.py --production
```

#### Alternative: Direct uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **API Overview**: http://localhost:8000/api
- **Health Check**: http://localhost:8000/health

## Usage Examples

### From Next.js Application

```javascript
// Get system status
const response = await fetch("http://localhost:8000/api/system/status");
const data = await response.json();

// Get basic meters
const meters = await fetch("http://localhost:8000/api/meters/basic");
const meterData = await meters.json();

// Lock machine
const lockResponse = await fetch("http://localhost:8000/api/machine/lock", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
});

// Enable bill acceptor
const billResponse = await fetch("http://localhost:8000/api/bill-acceptor/enable", {
  method: "POST",
});

// Control machine with parameters
const controlResponse = await fetch("http://localhost:8000/api/machine/control", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    action: "lock",
    lock_code: "00",
    timeout: 9000,
  }),
});
```

### Using curl

```bash
# Check health
curl http://localhost:8000/health

# Get system status
curl http://localhost:8000/api/system/status

# Get basic meters
curl http://localhost:8000/api/meters/basic

# Lock machine
curl -X POST http://localhost:8000/api/machine/lock

# Enable bill acceptor
curl -X POST http://localhost:8000/api/bill-acceptor/enable

# Control bill acceptor with JSON
curl -X POST http://localhost:8000/api/bill-acceptor/control \
  -H "Content-Type: application/json" \
  -d '{"action": "enable"}'
```

## Response Format

All endpoints return JSON responses with a consistent structure:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z",
  "execution_time_ms": 150.5,
  "data": {
    // Endpoint-specific data
  }
}
```

Error responses:

```json
{
  "success": false,
  "message": "Error description",
  "timestamp": "2024-01-15T10:30:00Z",
  "error_code": "ERROR_CODE",
  "details": {
    "error_type": "SpecificErrorType",
    "error_message": "Detailed error message"
  }
}
```

## Features

### ✅ Implemented

- Thread-safe SAS communication wrapper
- Comprehensive REST API endpoints
- Request/response validation with Pydantic
- Automatic API documentation with Swagger/ReDoc
- CORS support for Next.js integration
- Global exception handling
- Health checks and system status
- Asynchronous operation with proper timeouts

### 🔄 Thread Safety

- Command queuing system prevents race conditions
- Async/await pattern for non-blocking operations
- Background SAS polling continues independently
- Safe concurrent access to SAS functions

### 📊 Monitoring

- Execution time tracking for all operations
- Comprehensive logging
- Health status indicators
- Error tracking and reporting

## Integration with Your Existing Code

The FastAPI integration wraps your existing SAS code without modifying it:

- `SlotMachineApplication` continues to run in the background
- `SASCommunicator` handles all SAS protocol communication
- `SasMoney`, `BillAcceptorFunctions`, `CardReader` remain unchanged
- API endpoints provide a clean interface to these functions

## Next Steps (Phase 3+)

For future development:

- Add AFT (Advanced Funds Transfer) endpoints
- Card reader control endpoints
- Real-time WebSocket support for events
- Database integration for logging
- Authentication and authorization
- Rate limiting and request throttling

## Troubleshooting

### Common Issues

1. **Port Access**: Ensure your user has permission to access serial ports
2. **SAS Connection**: Check that the slot machine is connected and responding
3. **CORS**: Add your Next.js domain to the allowed origins in `main.py`
4. **Dependencies**: Make sure all required packages are installed

### Logs and Debugging

The application logs detailed information about:

- SAS communication status
- API request/response cycles
- Error conditions and exceptions
- System initialization and shutdown

Check the console output for detailed logging information.

## Configuration

### CORS Settings

Update the allowed origins in `main.py` for your Next.js application:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://your-nextjs-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Port Configuration

Change the server port in `run_api.py` or when running uvicorn directly:

```python
uvicorn.run("main:app", host="0.0.0.0", port=8001)  # Custom port
```
