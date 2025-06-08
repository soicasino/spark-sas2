"""
IP-based Access Control
SQLite-backed IP whitelist for SAS API access with persistent storage
"""
from fastapi import HTTPException, Request, Depends
from datetime import datetime
from typing import List, Set
import ipaddress
from database.db_manager import db_manager

class IPAccessControl:
    """Manages IP-based access control with database persistence"""
    
    def __init__(self):
        print("🌐 IP Access Control Initialized with Database Storage")
        
        # Load IPs from database on startup
        self._refresh_allowed_ips()
        
        print(f"   Loaded {len(self.allowed_ips_cache)} IPs/Networks from database")
        print("   ⚠️  Configure IP whitelist via API endpoints!")
    
    def _refresh_allowed_ips(self):
        """Refresh allowed IPs cache from database"""
        try:
            self.allowed_ips_cache = set(db_manager.get_allowed_ips())
        except Exception as e:
            print(f"❌ Error loading IPs from database: {e}")
            self.allowed_ips_cache = set()
    
    def is_ip_allowed(self, client_ip: str) -> bool:
        """Check if an IP address is allowed"""
        try:
            client_addr = ipaddress.ip_address(client_ip)
            
            # Refresh cache if needed
            if not hasattr(self, 'allowed_ips_cache'):
                self._refresh_allowed_ips()
            
            for allowed in self.allowed_ips_cache:
                try:
                    # Try as network (CIDR)
                    if '/' in allowed:
                        network = ipaddress.ip_network(allowed, strict=False)
                        if client_addr in network:
                            return True
                    # Try as single IP
                    else:
                        if client_addr == ipaddress.ip_address(allowed):
                            return True
                except ValueError:
                    continue
            
            return False
            
        except ValueError:
            # Invalid IP format
            return False
    
    def add_allowed_ip(self, ip_or_network: str, description: str = ""):
        """Add an IP or network to the allowed list (persistent)"""
        try:
            # Validate format
            if '/' in ip_or_network:
                ipaddress.ip_network(ip_or_network, strict=False)
            else:
                ipaddress.ip_address(ip_or_network)
            
            success = db_manager.add_allowed_ip(ip_or_network, description)
            if success:
                self._refresh_allowed_ips()  # Update cache
                print(f"✅ Added to IP whitelist: {ip_or_network}")
                return True
            else:
                print(f"❌ Failed to add IP to database: {ip_or_network}")
                return False
            
        except ValueError:
            print(f"❌ Invalid IP format: {ip_or_network}")
            return False
    
    def remove_allowed_ip(self, ip_or_network: str):
        """Remove an IP or network from the allowed list (persistent)"""
        success = db_manager.remove_allowed_ip(ip_or_network)
        if success:
            self._refresh_allowed_ips()  # Update cache
            print(f"✅ Removed from IP whitelist: {ip_or_network}")
            return True
        else:
            print(f"❌ IP not found in whitelist: {ip_or_network}")
            return False
    
    def get_allowed_ips(self) -> List[str]:
        """Get list of allowed IPs/networks"""
        self._refresh_allowed_ips()
        return list(self.allowed_ips_cache)
    
    def get_ip_details(self):
        """Get detailed IP information from database"""
        return db_manager.get_ip_details()

# Global IP access control instance
ip_access_control = IPAccessControl()

def get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies"""
    # Check for forwarded headers (proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP (client)
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct connection
    return request.client.host

async def verify_ip_access(request: Request):
    """Dependency to verify IP access"""
    client_ip = get_client_ip(request)
    
    if not ip_access_control.is_ip_allowed(client_ip):
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error_code": "ACCESS_DENIED",
                "message": f"Access denied for IP: {client_ip}",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    # Log successful access (optional)
    print(f"✅ API Access granted to IP: {client_ip}")
    
    return client_ip

# Optional: Dependency that doesn't enforce restrictions (for public endpoints)
async def get_client_ip_optional(request: Request) -> str:
    """Get client IP without enforcing restrictions"""
    return get_client_ip(request) 