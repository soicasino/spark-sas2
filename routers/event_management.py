"""
Event Management Router
Endpoints for viewing event statistics and managing synchronization
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from middleware.ip_access_control import verify_ip_access
from services.event_service import event_service
from database.db_manager import db_manager

router = APIRouter(
    prefix="/api/events",
    tags=["Event Management"],
    dependencies=[Depends(verify_ip_access)]
)

@router.get("/stats")
async def get_event_stats():
    """Get event synchronization statistics"""
    try:
        stats = event_service.get_event_stats()
        
        return {
            "success": True,
            "data": stats,
            "message": "Event statistics retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "STATS_RETRIEVAL_FAILED",
                "message": f"Failed to retrieve event statistics: {str(e)}"
            }
        )

@router.get("/unsynced")
async def get_unsynced_events(event_type: str = None, limit: int = 100):
    """Get unsynced events from database"""
    try:
        if event_type and event_type not in ["game", "card"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "INVALID_EVENT_TYPE",
                    "message": "event_type must be 'game' or 'card'"
                }
            )
        
        events = db_manager.get_unsynced_events(event_type, limit)
        
        return {
            "success": True,
            "data": {
                "events": events,
                "count": len(events),
                "event_type_filter": event_type,
                "limit": limit
            },
            "message": f"Retrieved {len(events)} unsynced events"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "UNSYNCED_EVENTS_RETRIEVAL_FAILED",
                "message": f"Failed to retrieve unsynced events: {str(e)}"
            }
        )

@router.post("/force-sync")
async def force_sync():
    """Force synchronization of offline events"""
    try:
        # Trigger sync manually
        await event_service._sync_offline_events()
        
        # Get updated stats
        stats = event_service.get_event_stats()
        
        return {
            "success": True,
            "data": stats,
            "message": "Forced synchronization completed"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "FORCE_SYNC_FAILED",
                "message": f"Failed to force synchronization: {str(e)}"
            }
        )

@router.get("/sync-status")
async def get_sync_status():
    """Get detailed synchronization status"""
    try:
        sync_status = db_manager.get_sync_status()
        
        return {
            "success": True,
            "data": {
                "sync_status": sync_status,
                "is_online": event_service.is_online,
                "failed_attempts": event_service.failed_attempts,
                "nextjs_url": event_service.nextjs_base_url
            },
            "message": "Sync status retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "SYNC_STATUS_RETRIEVAL_FAILED",
                "message": f"Failed to retrieve sync status: {str(e)}"
            }
        )

@router.post("/test-nextjs-connection")
async def test_nextjs_connection():
    """Test connection to Next.js app"""
    try:
        is_connected = await event_service._test_nextjs_connection()
        
        return {
            "success": True,
            "data": {
                "is_connected": is_connected,
                "nextjs_url": event_service.nextjs_base_url,
                "timeout": event_service.timeout
            },
            "message": f"Next.js connection test {'successful' if is_connected else 'failed'}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "CONNECTION_TEST_FAILED",
                "message": f"Failed to test Next.js connection: {str(e)}"
            }
        )

@router.post("/cleanup-old-events")
async def cleanup_old_events(days_old: int = 7):
    """Clean up old synced events to prevent database bloat"""
    try:
        if days_old < 1:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "INVALID_DAYS_VALUE",
                    "message": "days_old must be at least 1"
                }
            )
        
        db_manager.cleanup_old_synced_events(days_old)
        
        return {
            "success": True,
            "data": {
                "days_old": days_old
            },
            "message": f"Cleaned up events older than {days_old} days"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "CLEANUP_FAILED",
                "message": f"Failed to cleanup old events: {str(e)}"
            }
        )

@router.post("/test-game-event")
async def test_game_event(event_type: str = "test_game_started"):
    """Create a test game event for testing purposes"""
    try:
        import uuid
        
        test_event = {
            "event_type": event_type,
            "customer_id": "test_customer_123",
            "card_number": "1234567890123456",
            "game_id": "test_game_001",
            "session_id": str(uuid.uuid4()),
            "amount": 10.50,
            "balance_before": 100.00,
            "balance_after": 89.50,
            "extra_data": {
                "test": True,
                "description": "Test event for verification"
            }
        }
        
        success = await event_service.send_game_event(test_event)
        
        return {
            "success": True,
            "data": {
                "event_sent": success,
                "event_data": test_event,
                "stored_offline": not event_service.is_online
            },
            "message": f"Test game event {'sent to Next.js' if success and event_service.is_online else 'stored offline'}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "TEST_EVENT_FAILED",
                "message": f"Failed to create test event: {str(e)}"
            }
        )

@router.post("/test-card-event")
async def test_card_event(event_type: str = "card_inserted"):
    """Create a test card event for testing purposes"""
    try:
        import uuid
        
        test_event = {
            "event_type": event_type,
            "card_number": "1234567890123456",
            "customer_id": "test_customer_123",
            "session_id": str(uuid.uuid4())
        }
        
        success = await event_service.send_card_event(test_event)
        
        return {
            "success": True,
            "data": {
                "event_sent": success,
                "event_data": test_event,
                "stored_offline": not event_service.is_online
            },
            "message": f"Test card event {'sent to Next.js' if success and event_service.is_online else 'stored offline'}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "TEST_EVENT_FAILED",
                "message": f"Failed to create test event: {str(e)}"
            }
        ) 