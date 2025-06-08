# SAS Slot Machine Dashboard

A modern Next.js dashboard for monitoring and controlling SAS (Slot Accounting System) slot machines.

## ✨ Features

### 🎮 **Real-time Monitoring**

- **Live Events Feed**: WebSocket connection for real-time card and game events
- **Card Reader Status**: Monitor card insertion/removal with card numbers
- **Bill Acceptor Control**: Enable/disable and monitor bill acceptance
- **Meter Readings**: View current credits, balances, and game statistics
- **System Status**: Overall health and connection monitoring

### 💰 **Money Management**

- **Credit Transfer**: Add or subtract credits from the machine
- **Balance Monitoring**: Real-time balance updates
- **Transaction History**: Track money operations

### 🛠️ **Machine Control**

- **Lock/Unlock Machine**: Secure machine operations
- **Emergency Stop**: Immediate machine shutdown
- **Bill Acceptor Control**: Start, stop, stack, and return bill operations

### 📊 **Event Management**

- **Event Synchronization**: Monitor connection to backend services
- **Offline Storage**: Events stored when connection is lost
- **Force Sync**: Manual synchronization of offline events
- **Test Events**: Generate test events for debugging

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- SAS FastAPI backend running on `http://localhost:8000`

### Installation

```bash
cd test-frontend
npm install
```

### Environment Configuration

Set the API URL if different from default:

```bash
# Windows Command Prompt
set NEXT_PUBLIC_API_URL=http://localhost:8000

# Windows PowerShell
$env:NEXT_PUBLIC_API_URL="http://localhost:8000"

# Linux/Mac
export NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

### Production Build

```bash
npm run build
npm start
```

## 🎛️ Dashboard Overview

### Navigation Tabs

1. **Overview** - Quick status summary and actions
2. **Card Reader** - Detailed card reader status and controls
3. **Meters** - Credit balances and money transfer operations
4. **Bill Acceptor** - Bill acceptance control and status
5. **Live Events** - Real-time event feed and statistics

### Key Components

#### Overview Tab

- **Status Cards**: Quick view of card reader, balance, bill acceptor, and event sync
- **Quick Actions**: Lock/unlock machine, emergency stop, force sync

#### Card Reader Tab

- **Real-time Status**: Card present indicator and card number
- **Manual Controls**: Eject card, refresh status
- **Test Events**: Generate test card events

#### Meters Tab

- **Current Meters**: All machine meter readings
- **Money Transfer**: Add/subtract credits with amount input
- **Balance Display**: Formatted currency display

#### Bill Acceptor Tab

- **Toggle Control**: Enable/disable with switch
- **Manual Actions**: Start, stop, stack, return operations
- **Status Monitoring**: Current state and last bill amount

#### Live Events Tab

- **Event Feed**: Real-time scrolling list of events
- **Connection Status**: WebSocket and backend connectivity
- **Event Statistics**: Sync status and unsynced event counts

## 🔧 Configuration

### API Endpoints

The dashboard connects to these SAS API endpoints:

- **Card Reader**: `/api/card-reader/*`
- **Meters**: `/api/meters/*`
- **Bill Acceptor**: `/api/bill-acceptor/*`
- **Machine Control**: `/api/machine/*`
- **Events**: `/api/events/*`
- **WebSocket**: `/ws/live-updates`

### WebSocket Connection

Real-time updates are received via WebSocket connection with automatic reconnection on failure.

### Error Handling

- **API Errors**: Displayed in alert banners
- **Network Issues**: Graceful degradation with retry mechanisms
- **WebSocket Failures**: Automatic reconnection attempts

## 🎨 UI Components

Built with **shadcn/ui** components:

- Modern, accessible design
- Dark/light theme support
- Responsive layout
- Loading states and error handling

### Icons

Uses **Lucide React** icons for consistent visual language.

## 🔒 Security

### IP-based Access Control

The backend uses IP-based access control. Ensure your IP is whitelisted:

```bash
# Check your IP
curl http://localhost:8000/api/access/my-ip

# Add your IP (from backend)
curl -X POST http://localhost:8000/api/access/allowed-ips \
  -H "Content-Type: application/json" \
  -d '{"ip": "YOUR_IP_HERE"}'
```

## 📡 Real-time Features

### WebSocket Events

The dashboard receives these real-time events:

- `card_event`: Card insertion/removal
- `game_event`: Game start/stop/win/loss
- `meter_update`: Balance changes
- `bill_acceptor_event`: Bill acceptance events

### Auto-refresh

Data automatically refreshes on relevant events to keep displays current.

## 🐛 Testing & Debugging

### Test Events

Use the built-in test event generators:

- Test Card Events: Simulate card insertion/removal
- Test Game Events: Generate sample game events
- Connection Test: Verify backend connectivity

### Console Logging

WebSocket events and API calls are logged to browser console for debugging.

## 📦 Dependencies

### Core

- **Next.js 15**: React framework
- **React 19**: UI library
- **TypeScript**: Type safety

### UI Components

- **shadcn/ui**: Modern component library
- **Tailwind CSS**: Utility-first styling
- **Lucide React**: Icon library

### Development

- **ESLint**: Code linting
- **PostCSS**: CSS processing

## 🔄 Development Workflow

1. **Start Backend**: Ensure SAS FastAPI server is running
2. **Start Frontend**: Run `npm run dev`
3. **Access Dashboard**: Open `http://localhost:3000`
4. **Monitor Console**: Check browser console for WebSocket events
5. **Test Features**: Use test buttons to verify functionality

## 🚀 Deployment

### Production Considerations

- Set `NEXT_PUBLIC_API_URL` to production backend URL
- Configure proper IP whitelisting on backend
- Use reverse proxy for WebSocket connections if needed
- Enable HTTPS for secure connections

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 📝 Notes

- **WebSocket Auto-reconnect**: Connection automatically retries on failure
- **Responsive Design**: Works on desktop and tablet devices
- **Real-time Updates**: Data refreshes automatically on relevant events
- **Error Handling**: Graceful error display and recovery
- **Loading States**: Visual feedback during API operations

## 🆘 Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**

   - Check if backend is running
   - Verify WebSocket URL configuration
   - Check browser console for errors

2. **API Calls Failing**

   - Verify IP is whitelisted on backend
   - Check `NEXT_PUBLIC_API_URL` configuration
   - Ensure backend is accessible

3. **No Live Events**

   - Verify WebSocket connection (check badge in header)
   - Test with manual event generation
   - Check backend WebSocket implementation

4. **Styling Issues**
   - Ensure all shadcn components are installed
   - Check Tailwind CSS configuration
   - Verify component imports

For more help, check the browser console for detailed error messages.
