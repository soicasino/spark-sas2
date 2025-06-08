"""
Event Service
Handles game and card events with Next.js app communication and offline fallback
"""
import asyncio
import httpx
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from database.db_manager import db_manager
import json
import threading
from config import settings

class EventService:
    """Service for handling game and card events with offline fallback"""
    
    def __init__(self):
        self.nextjs_base_url = getattr(settings, 'NEXTJS_BASE_URL', 'http://localhost:3000')
        self.timeout = getattr(settings, 'NEXTJS_TIMEOUT', 5.0)
        self.is_online = True
        self.failed_attempts = 0
        self.max_retry_attempts = 3
        
        # Start background sync task
        self._start_sync_task()
        
        print(f"🎮 Event Service initialized")
        print(f"   Next.js URL: {self.nextjs_base_url}")
        print(f"   Timeout: {self.timeout}s")
    
    def _start_sync_task(self):
        """Start background task to sync offline events"""
        def sync_worker():
            import time
            while True:
                try:
                    if self.is_online:
                        asyncio.run(self._sync_offline_events())
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    print(f"❌ Sync worker error: {e}")
                    time.sleep(60)  # Wait longer on error
        
        sync_thread = threading.Thread(target=sync_worker, daemon=True)
        sync_thread.start()
        print("🔄 Background event sync started")
    
    async def _test_nextjs_connection(self) -> bool:
        """Test connection to Next.js app"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.nextjs_base_url}/api/health")
                success = response.status_code == 200
                
                if success and not self.is_online:
                    print("✅ Next.js app connection restored")
                    self.is_online = True
                    self.failed_attempts = 0
                    db_manager.update_sync_status("nextjs_app", True, True)
                
                return success
                
        except Exception as e:
            if self.is_online:
                print(f"🔌 Next.js app connection lost: {e}")
                self.is_online = False
            
            self.failed_attempts += 1
            db_manager.update_sync_status("nextjs_app", False, False)
            return False
    
    async def send_game_event(self, event_data: Dict[str, Any]) -> bool:
        """Send game event to Next.js app or store offline"""
        # Ensure event has UUID
        if not event_data.get('event_id'):
            event_data['event_id'] = str(uuid.uuid4())
        
        # Add timestamp if not present
        if not event_data.get('timestamp'):
            event_data['timestamp'] = datetime.now().isoformat()
        
        print(f"🎮 Processing game event: {event_data.get('event_type')} (ID: {event_data.get('event_id')})")
        
        # Try to send to Next.js app
        if await self._send_to_nextjs('/api/events/game', event_data):
            return True
        
        # Fallback to database storage
        success = db_manager.store_game_event(event_data)
        if success:
            print(f"💾 Game event stored offline for later sync")
        
        return success
    
    async def send_card_event(self, event_data: Dict[str, Any]) -> bool:
        """Send card event to Next.js app or store offline"""
        # Ensure event has UUID
        if not event_data.get('event_id'):
            event_data['event_id'] = str(uuid.uuid4())
        
        # Add timestamp if not present
        if not event_data.get('timestamp'):
            event_data['timestamp'] = datetime.now().isoformat()
        
        print(f"🎴 Processing card event: {event_data.get('event_type')} (ID: {event_data.get('event_id')})")
        
        # Try to send to Next.js app
        if await self._send_to_nextjs('/api/events/card', event_data):
            return True
        
        # Fallback to database storage
        success = db_manager.store_card_event(event_data)
        if success:
            print(f"💾 Card event stored offline for later sync")
        
        return success
    
    async def _send_to_nextjs(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """Send data to Next.js app endpoint"""
        try:
            if not await self._test_nextjs_connection():
                return False
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.nextjs_base_url}{endpoint}",
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in [200, 201]:
                    print(f"✅ Event sent to Next.js: {data.get('event_type')}")
                    return True
                else:
                    print(f"❌ Next.js returned error {response.status_code}: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Failed to send to Next.js: {e}")
            return False
    
    async def _sync_offline_events(self):
        """Sync offline events to Next.js app"""
        if not await self._test_nextjs_connection():
            return
        
        # Sync game events
        game_events = db_manager.get_unsynced_events("game", limit=50)
        if game_events:
            print(f"🔄 Syncing {len(game_events)} game events...")
            synced_ids = []
            
            for event in game_events:
                event_dict = dict(event)
                # Parse JSON event_data back to dict
                if event_dict.get('event_data'):
                    try:
                        event_dict['extra_data'] = json.loads(event_dict['event_data'])
                    except:
                        pass
                
                if await self._send_to_nextjs('/api/events/game', event_dict):
                    synced_ids.append(event_dict['event_id'])
                else:
                    # Stop syncing on first failure to maintain order
                    break
            
            if synced_ids:
                db_manager.mark_events_synced(synced_ids, "game")
                print(f"✅ Synced {len(synced_ids)} game events")
            
            if len(synced_ids) < len(game_events):
                failed_ids = [e['event_id'] for e in game_events[len(synced_ids):]]
                db_manager.increment_sync_attempts(failed_ids, "game")
        
        # Sync card events
        card_events = db_manager.get_unsynced_events("card", limit=50)
        if card_events:
            print(f"🔄 Syncing {len(card_events)} card events...")
            synced_ids = []
            
            for event in card_events:
                event_dict = dict(event)
                
                if await self._send_to_nextjs('/api/events/card', event_dict):
                    synced_ids.append(event_dict['event_id'])
                else:
                    # Stop syncing on first failure to maintain order
                    break
            
            if synced_ids:
                db_manager.mark_events_synced(synced_ids, "card")
                print(f"✅ Synced {len(synced_ids)} card events")
            
            if len(synced_ids) < len(card_events):
                failed_ids = [e['event_id'] for e in card_events[len(synced_ids):]]
                db_manager.increment_sync_attempts(failed_ids, "card")
    
    def get_event_stats(self) -> Dict[str, Any]:
        """Get event synchronization statistics"""
        sync_status = db_manager.get_sync_status()
        
        # Count unsynced events
        unsynced_game = len(db_manager.get_unsynced_events("game", limit=1000))
        unsynced_card = len(db_manager.get_unsynced_events("card", limit=1000))
        
        return {
            "is_online": self.is_online,
            "nextjs_url": self.nextjs_base_url,
            "failed_attempts": self.failed_attempts,
            "unsynced_events": {
                "game": unsynced_game,
                "card": unsynced_card,
                "total": unsynced_game + unsynced_card
            },
            "sync_status": sync_status
        }
    
    # Convenience methods for common game events
    async def game_started(self, customer_id: str, card_number: str, game_id: str, session_id: str, **kwargs):
        """Log game start event"""
        return await self.send_game_event({
            "event_type": "game_started",
            "customer_id": customer_id,
            "card_number": card_number,
            "game_id": game_id,
            "session_id": session_id,
            "extra_data": kwargs
        })
    
    async def game_ended(self, customer_id: str, card_number: str, game_id: str, session_id: str, 
                        result: str, amount: float = None, balance_before: float = None, 
                        balance_after: float = None, **kwargs):
        """Log game end event"""
        return await self.send_game_event({
            "event_type": "game_ended",
            "customer_id": customer_id,
            "card_number": card_number,
            "game_id": game_id,
            "session_id": session_id,
            "amount": amount,
            "balance_before": balance_before,
            "balance_after": balance_after,
            "extra_data": {
                "result": result,
                **kwargs
            }
        })
    
    async def game_win(self, customer_id: str, card_number: str, game_id: str, session_id: str,
                      win_amount: float, balance_before: float = None, balance_after: float = None, **kwargs):
        """Log game win event"""
        return await self.send_game_event({
            "event_type": "game_win",
            "customer_id": customer_id,
            "card_number": card_number,
            "game_id": game_id,
            "session_id": session_id,
            "amount": win_amount,
            "balance_before": balance_before,
            "balance_after": balance_after,
            "extra_data": kwargs
        })
    
    async def game_loss(self, customer_id: str, card_number: str, game_id: str, session_id: str,
                       loss_amount: float, balance_before: float = None, balance_after: float = None, **kwargs):
        """Log game loss event"""
        return await self.send_game_event({
            "event_type": "game_loss",
            "customer_id": customer_id,
            "card_number": card_number,
            "game_id": game_id,
            "session_id": session_id,
            "amount": loss_amount,
            "balance_before": balance_before,
            "balance_after": balance_after,
            "extra_data": kwargs
        })
    
    async def jackpot_win(self, customer_id: str, card_number: str, game_id: str, session_id: str,
                         jackpot_amount: float, jackpot_type: str = "regular", **kwargs):
        """Log jackpot win event"""
        return await self.send_game_event({
            "event_type": "jackpot_win",
            "customer_id": customer_id,
            "card_number": card_number,
            "game_id": game_id,
            "session_id": session_id,
            "amount": jackpot_amount,
            "extra_data": {
                "jackpot_type": jackpot_type,
                **kwargs
            }
        })
    
    async def card_inserted(self, card_number: str, customer_id: str = None, session_id: str = None):
        """Log card insertion event"""
        return await self.send_card_event({
            "event_type": "card_inserted",
            "card_number": card_number,
            "customer_id": customer_id,
            "session_id": session_id
        })
    
    async def card_removed(self, card_number: str, customer_id: str = None, session_id: str = None):
        """Log card removal event"""
        return await self.send_card_event({
            "event_type": "card_removed",
            "card_number": card_number,
            "customer_id": customer_id,
            "session_id": session_id
        })
    
    async def card_ejected(self, card_number: str, customer_id: str = None, session_id: str = None, reason: str = "manual"):
        """Log card ejection event"""
        return await self.send_card_event({
            "event_type": "card_ejected",
            "card_number": card_number,
            "customer_id": customer_id,
            "session_id": session_id,
            "extra_data": {"reason": reason}
        })

# Global event service instance
event_service = EventService() 