"""
SQLite Database Manager
Handles IP access control and game events storage for offline scenarios
"""
import sqlite3
import json
import threading
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

class DatabaseManager:
    """SQLite database manager for IP access and game events"""
    
    def __init__(self, db_path: str = "sas_data.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        
        # Ensure database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database and tables
        self.init_database()
        
        print(f"📦 Database Manager initialized: {db_path}")
    
    def get_connection(self):
        """Get database connection with proper settings"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        with self.lock:
            conn = self.get_connection()
            try:
                # Create IP access control table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS ip_access_control (
                        id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                        ip_or_network TEXT UNIQUE NOT NULL,
                        description TEXT DEFAULT '',
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create game events table for offline storage
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS game_events (
                        id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                        event_id TEXT UNIQUE NOT NULL DEFAULT (lower(hex(randomblob(16)))),
                        customer_id TEXT,
                        card_number TEXT,
                        event_type TEXT NOT NULL,
                        game_id TEXT,
                        session_id TEXT,
                        event_data TEXT,  -- JSON data
                        amount DECIMAL(10,2),
                        balance_before DECIMAL(10,2),
                        balance_after DECIMAL(10,2),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_synced BOOLEAN DEFAULT 0,
                        sync_attempts INTEGER DEFAULT 0,
                        last_sync_attempt TIMESTAMP NULL
                    )
                """)
                
                # Create card events table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS card_events (
                        id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                        event_id TEXT UNIQUE NOT NULL DEFAULT (lower(hex(randomblob(16)))),
                        card_number TEXT NOT NULL,
                        event_type TEXT NOT NULL,  -- 'inserted', 'removed', 'ejected'
                        customer_id TEXT,
                        session_id TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_synced BOOLEAN DEFAULT 0,
                        sync_attempts INTEGER DEFAULT 0,
                        last_sync_attempt TIMESTAMP NULL
                    )
                """)
                
                # Create sync status table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sync_status (
                        id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                        service_name TEXT UNIQUE NOT NULL,
                        last_successful_sync TIMESTAMP,
                        last_attempt TIMESTAMP,
                        is_online BOOLEAN DEFAULT 1,
                        total_failed_attempts INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Add indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_game_events_synced ON game_events(is_synced)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_game_events_timestamp ON game_events(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_card_events_synced ON card_events(is_synced)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_card_events_timestamp ON card_events(timestamp)")
                
                conn.commit()
                print("✅ Database tables initialized successfully")
                
                # Load default IPs if table is empty
                self._load_default_ips(conn)
                
            except Exception as e:
                print(f"❌ Database initialization error: {e}")
                conn.rollback()
            finally:
                conn.close()
    
    def _load_default_ips(self, conn):
        """Load default IP ranges if table is empty"""
        cursor = conn.execute("SELECT COUNT(*) FROM ip_access_control")
        count = cursor.fetchone()[0]
        
        if count == 0:
            default_ips = [
                ("127.0.0.1", "localhost"),
                ("::1", "localhost IPv6"),
                ("192.168.1.0/24", "Common local network"),
                ("10.0.0.0/8", "Private network range"),
                ("172.16.0.0/12", "Private network range")
            ]
            
            for ip, desc in default_ips:
                conn.execute(
                    "INSERT INTO ip_access_control (ip_or_network, description) VALUES (?, ?)",
                    (ip, desc)
                )
            
            conn.commit()
            print(f"📋 Loaded {len(default_ips)} default IP ranges")
    
    # IP Access Control Methods
    def get_allowed_ips(self) -> List[str]:
        """Get list of allowed IPs/networks"""
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.execute(
                    "SELECT ip_or_network FROM ip_access_control WHERE is_active = 1"
                )
                return [row[0] for row in cursor.fetchall()]
            finally:
                conn.close()
    
    def add_allowed_ip(self, ip_or_network: str, description: str = "") -> bool:
        """Add IP to allowed list"""
        with self.lock:
            conn = self.get_connection()
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO ip_access_control (ip_or_network, description, updated_at) VALUES (?, ?, ?)",
                    (ip_or_network, description, datetime.now())
                )
                conn.commit()
                return True
            except Exception as e:
                print(f"Error adding IP {ip_or_network}: {e}")
                return False
            finally:
                conn.close()
    
    def remove_allowed_ip(self, ip_or_network: str) -> bool:
        """Remove IP from allowed list"""
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.execute(
                    "UPDATE ip_access_control SET is_active = 0, updated_at = ? WHERE ip_or_network = ?",
                    (datetime.now(), ip_or_network)
                )
                success = cursor.rowcount > 0
                conn.commit()
                return success
            except Exception as e:
                print(f"Error removing IP {ip_or_network}: {e}")
                return False
            finally:
                conn.close()
    
    def get_ip_details(self) -> List[Dict[str, Any]]:
        """Get detailed IP information"""
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.execute("""
                    SELECT ip_or_network, description, is_active, created_at, updated_at 
                    FROM ip_access_control 
                    ORDER BY created_at DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
            finally:
                conn.close()
    
    # Game Events Methods
    def store_game_event(self, event_data: Dict[str, Any]) -> bool:
        """Store game event when Next.js app is unreachable"""
        with self.lock:
            conn = self.get_connection()
            try:
                # Generate UUID if not provided
                event_id = event_data.get('event_id') or str(uuid.uuid4())
                
                conn.execute("""
                    INSERT INTO game_events (
                        event_id, customer_id, card_number, event_type, game_id, 
                        session_id, event_data, amount, balance_before, balance_after, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event_id,
                    event_data.get('customer_id'),
                    event_data.get('card_number'),
                    event_data.get('event_type'),
                    event_data.get('game_id'),
                    event_data.get('session_id'),
                    json.dumps(event_data.get('extra_data', {})),
                    event_data.get('amount'),
                    event_data.get('balance_before'),
                    event_data.get('balance_after'),
                    event_data.get('timestamp', datetime.now())
                ))
                conn.commit()
                print(f"💾 Stored game event offline: {event_data.get('event_type')} (ID: {event_id})")
                return True
            except Exception as e:
                print(f"❌ Error storing game event: {e}")
                return False
            finally:
                conn.close()
    
    def store_card_event(self, event_data: Dict[str, Any]) -> bool:
        """Store card event when Next.js app is unreachable"""
        with self.lock:
            conn = self.get_connection()
            try:
                # Generate UUID if not provided
                event_id = event_data.get('event_id') or str(uuid.uuid4())
                
                conn.execute("""
                    INSERT INTO card_events (
                        event_id, card_number, event_type, customer_id, session_id, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    event_id,
                    event_data.get('card_number'),
                    event_data.get('event_type'),
                    event_data.get('customer_id'),
                    event_data.get('session_id'),
                    event_data.get('timestamp', datetime.now())
                ))
                conn.commit()
                print(f"💾 Stored card event offline: {event_data.get('event_type')} (ID: {event_id})")
                return True
            except Exception as e:
                print(f"❌ Error storing card event: {e}")
                return False
            finally:
                conn.close()
    
    def get_unsynced_events(self, event_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get unsynced events for synchronization"""
        with self.lock:
            conn = self.get_connection()
            try:
                if event_type == "game":
                    cursor = conn.execute("""
                        SELECT * FROM game_events 
                        WHERE is_synced = 0 
                        ORDER BY timestamp ASC 
                        LIMIT ?
                    """, (limit,))
                elif event_type == "card":
                    cursor = conn.execute("""
                        SELECT * FROM card_events 
                        WHERE is_synced = 0 
                        ORDER BY timestamp ASC 
                        LIMIT ?
                    """, (limit,))
                else:
                    # Return both types
                    game_cursor = conn.execute("""
                        SELECT 'game' as table_type, * FROM game_events 
                        WHERE is_synced = 0 
                        ORDER BY timestamp ASC 
                        LIMIT ?
                    """, (limit//2,))
                    card_cursor = conn.execute("""
                        SELECT 'card' as table_type, * FROM card_events 
                        WHERE is_synced = 0 
                        ORDER BY timestamp ASC 
                        LIMIT ?
                    """, (limit//2,))
                    return [dict(row) for row in game_cursor.fetchall()] + [dict(row) for row in card_cursor.fetchall()]
                
                return [dict(row) for row in cursor.fetchall()]
            finally:
                conn.close()
    
    def mark_events_synced(self, event_ids: List[str], event_type: str) -> bool:
        """Mark events as synced"""
        with self.lock:
            conn = self.get_connection()
            try:
                table = "game_events" if event_type == "game" else "card_events"
                placeholders = ','.join(['?' for _ in event_ids])
                conn.execute(f"""
                    UPDATE {table} 
                    SET is_synced = 1, last_sync_attempt = ? 
                    WHERE event_id IN ({placeholders})
                """, [datetime.now()] + event_ids)
                conn.commit()
                return True
            except Exception as e:
                print(f"❌ Error marking events as synced: {e}")
                return False
            finally:
                conn.close()
    
    def increment_sync_attempts(self, event_ids: List[str], event_type: str) -> bool:
        """Increment sync attempt counter for failed syncs"""
        with self.lock:
            conn = self.get_connection()
            try:
                table = "game_events" if event_type == "game" else "card_events"
                placeholders = ','.join(['?' for _ in event_ids])
                conn.execute(f"""
                    UPDATE {table} 
                    SET sync_attempts = sync_attempts + 1, last_sync_attempt = ? 
                    WHERE event_id IN ({placeholders})
                """, [datetime.now()] + event_ids)
                conn.commit()
                return True
            except Exception as e:
                print(f"❌ Error incrementing sync attempts: {e}")
                return False
            finally:
                conn.close()
    
    def update_sync_status(self, service_name: str, is_online: bool, success: bool = True):
        """Update service sync status"""
        with self.lock:
            conn = self.get_connection()
            try:
                now = datetime.now()
                if success:
                    conn.execute("""
                        INSERT OR REPLACE INTO sync_status 
                        (service_name, last_successful_sync, last_attempt, is_online, total_failed_attempts)
                        VALUES (?, ?, ?, ?, 0)
                    """, (service_name, now, now, is_online))
                else:
                    conn.execute("""
                        INSERT OR REPLACE INTO sync_status 
                        (service_name, last_attempt, is_online, total_failed_attempts)
                        VALUES (?, ?, ?, COALESCE((SELECT total_failed_attempts FROM sync_status WHERE service_name = ?), 0) + 1)
                    """, (service_name, now, is_online, service_name))
                conn.commit()
            except Exception as e:
                print(f"❌ Error updating sync status: {e}")
            finally:
                conn.close()
    
    def get_sync_status(self) -> List[Dict[str, Any]]:
        """Get sync status for all services"""
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.execute("SELECT * FROM sync_status ORDER BY last_attempt DESC")
                return [dict(row) for row in cursor.fetchall()]
            finally:
                conn.close()
    
    def cleanup_old_synced_events(self, days_old: int = 7):
        """Clean up old synced events to prevent database bloat"""
        with self.lock:
            conn = self.get_connection()
            try:
                cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
                
                # Delete old synced game events
                cursor = conn.execute("""
                    DELETE FROM game_events 
                    WHERE is_synced = 1 AND created_at < datetime(?, 'unixepoch')
                """, (cutoff_date,))
                game_deleted = cursor.rowcount
                
                # Delete old synced card events
                cursor = conn.execute("""
                    DELETE FROM card_events 
                    WHERE is_synced = 1 AND created_at < datetime(?, 'unixepoch')
                """, (cutoff_date,))
                card_deleted = cursor.rowcount
                
                conn.commit()
                
                if game_deleted > 0 or card_deleted > 0:
                    print(f"🧹 Cleaned up {game_deleted} game events and {card_deleted} card events older than {days_old} days")
                
            except Exception as e:
                print(f"❌ Error cleaning up old events: {e}")
            finally:
                conn.close()

# Global database manager instance
db_manager = DatabaseManager() 