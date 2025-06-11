"""
WebSocket Manager for Real-time SAS Updates
Handles live streaming of meter data, machine status, and events
"""
import asyncio
import json
import logging
from typing import Dict, Set, Any, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Active WebSocket connections
        self.active_connections: Set[WebSocket] = set()
        
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Event subscriptions per connection
        self.subscriptions: Dict[WebSocket, Set[str]] = {}
        
        # Last known data for immediate updates to new connections
        self.last_meter_data: Optional[Dict[str, Any]] = None
        self.last_system_status: Optional[Dict[str, Any]] = None
        self.last_machine_status: Optional[Dict[str, Any]] = None
        
        # Update counters for metrics
        self.update_counters = {
            "meters": 0,
            "system_status": 0,
            "machine_events": 0,
            "bill_events": 0,
            "card_events": 0,
            "money_events": 0
        }

    async def connect(self, websocket: WebSocket, client_info: Dict[str, Any] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        # Store connection metadata
        self.connection_metadata[websocket] = {
            "connected_at": datetime.now(),
            "client_info": client_info or {},
            "last_ping": datetime.now()
        }
        
        # Default subscriptions (all events)
        self.subscriptions[websocket] = {
            "meters", "system_status", "machine_events", "bill_events", "card_events", "money_events", "heartbeat"
        }
        
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")
        
        # Send initial data to new connection
        await self._send_initial_data(websocket)

    async def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
            
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
            
        logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")

    async def _send_initial_data(self, websocket: WebSocket):
        """Send last known data to newly connected client"""
        try:
            # Send last meter data
            if self.last_meter_data:
                await self._send_to_connection(websocket, {
                    "type": "meters",
                    "data": self.last_meter_data,
                    "timestamp": datetime.now().isoformat(),
                    "is_initial": True
                })
            
            # Send last system status
            if self.last_system_status:
                await self._send_to_connection(websocket, {
                    "type": "system_status",
                    "data": self.last_system_status,
                    "timestamp": datetime.now().isoformat(),
                    "is_initial": True
                })
                
            # Send connection stats
            await self._send_to_connection(websocket, {
                "type": "connection_info",
                "data": {
                    "connected_clients": len(self.active_connections),
                    "update_counters": self.update_counters.copy(),
                    "connection_established": datetime.now().isoformat()
                },
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error sending initial data: {e}")

    async def _send_to_connection(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to a specific connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending to WebSocket connection: {e}")
            await self.disconnect(websocket)

    async def broadcast_to_subscribed(self, event_type: str, data: Dict[str, Any]):
        """Broadcast data to all connections subscribed to event type"""
        if not self.active_connections:
            return
            
        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store last known data
        if event_type == "meters":
            self.last_meter_data = data
            self.update_counters["meters"] += 1
        elif event_type == "system_status":
            self.last_system_status = data
            self.update_counters["system_status"] += 1
        elif event_type == "machine_events":
            self.update_counters["machine_events"] += 1
        elif event_type == "bill_events":
            self.update_counters["bill_events"] += 1
        elif event_type == "card_events":
            self.update_counters["card_events"] += 1
        elif event_type == "money_events":
            self.update_counters["money_events"] += 1

        # Send to subscribed connections
        disconnected_connections = []
        
        for websocket in self.active_connections.copy():
            if event_type in self.subscriptions.get(websocket, set()):
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to WebSocket: {e}")
                    disconnected_connections.append(websocket)
        
        # Clean up disconnected connections
        for websocket in disconnected_connections:
            await self.disconnect(websocket)

    async def update_subscription(self, websocket: WebSocket, event_types: Set[str]):
        """Update event subscriptions for a connection"""
        valid_events = {"meters", "system_status", "machine_events", "bill_events", "card_events", "money_events", "heartbeat"}
        
        # Filter to valid event types
        filtered_events = event_types.intersection(valid_events)
        self.subscriptions[websocket] = filtered_events
        
        await self._send_to_connection(websocket, {
            "type": "subscription_updated",
            "data": {
                "subscribed_events": list(filtered_events),
                "available_events": list(valid_events)
            },
            "timestamp": datetime.now().isoformat()
        })

    async def send_heartbeat(self):
        """Send heartbeat to all connections"""
        if not self.active_connections:
            return
            
        heartbeat_data = {
            "server_time": datetime.now().isoformat(),
            "active_connections": len(self.active_connections),
            "uptime_seconds": 0  # Could track actual uptime
        }
        
        await self.broadcast_to_subscribed("heartbeat", heartbeat_data)

    async def handle_client_message(self, websocket: WebSocket, message: str):
        """Handle incoming messages from clients"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "ping":
                # Update last ping time
                if websocket in self.connection_metadata:
                    self.connection_metadata[websocket]["last_ping"] = datetime.now()
                
                # Send pong response
                await self._send_to_connection(websocket, {
                    "type": "pong",
                    "data": {"timestamp": datetime.now().isoformat()},
                    "timestamp": datetime.now().isoformat()
                })
                
            elif message_type == "subscribe":
                # Update subscriptions
                events = set(data.get("events", []))
                await self.update_subscription(websocket, events)
                
            elif message_type == "request_current_data":
                # Send current data immediately
                await self._send_initial_data(websocket)
                
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from WebSocket client")
        except Exception as e:
            logger.error(f"Error handling client message: {e}")

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get current connection statistics"""
        now = datetime.now()
        
        connection_details = []
        for websocket, metadata in self.connection_metadata.items():
            connection_details.append({
                "connected_duration_seconds": (now - metadata["connected_at"]).total_seconds(),
                "last_ping_seconds_ago": (now - metadata["last_ping"]).total_seconds(),
                "subscriptions": list(self.subscriptions.get(websocket, set())),
                "client_info": metadata.get("client_info", {})
            })
        
        return {
            "total_connections": len(self.active_connections),
            "update_counters": self.update_counters.copy(),
            "connections": connection_details
        }

# Global connection manager instance
connection_manager = ConnectionManager()

@asynccontextmanager
async def websocket_lifespan():
    """Async context manager for WebSocket lifecycle"""
    logger.info("WebSocket manager starting...")
    
    # Start background tasks
    heartbeat_task = asyncio.create_task(heartbeat_loop())
    
    try:
        yield connection_manager
    finally:
        logger.info("WebSocket manager shutting down...")
        heartbeat_task.cancel()
        
        # Close all connections
        for websocket in connection_manager.active_connections.copy():
            try:
                await websocket.close()
            except:
                pass

async def heartbeat_loop():
    """Background task to send periodic heartbeats"""
    while True:
        try:
            await connection_manager.send_heartbeat()
            await asyncio.sleep(30)  # Send heartbeat every 30 seconds
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in heartbeat loop: {e}")
            await asyncio.sleep(5)  # Wait before retrying 