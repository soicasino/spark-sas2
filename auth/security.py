"""
Authentication and Security Module
Handles JWT tokens, user authentication, and API security
"""
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token security
security = HTTPBearer()

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    scope: str

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False
    scopes: list[str] = []

class UserInDB(User):
    hashed_password: str

# Mock user database - replace with real database in production
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "System Administrator",
        "email": "admin@casino.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
        "scopes": ["admin", "read", "write", "control"]
    },
    "operator": {
        "username": "operator",
        "full_name": "Casino Operator", 
        "email": "operator@casino.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
        "scopes": ["read", "write"]
    },
    "readonly": {
        "username": "readonly",
        "full_name": "Read-Only User",
        "email": "readonly@casino.com", 
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
        "scopes": ["read"]
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[UserInDB]:
    """Get user from database"""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(username: str, password: str) -> Union[UserInDB, bool]:
    """Authenticate user credentials"""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        scopes: list = payload.get("scopes", [])
        
        if username is None:
            return None
            
        token_data = TokenData(username=username, scopes=scopes)
        return token_data
        
    except JWTError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(credentials.credentials)
    if token_data is None or token_data.username is None:
        raise credentials_exception
        
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
        
    return User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=user.disabled,
        scopes=user.scopes
    )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user (not disabled)"""
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

class RequireScopes:
    """Dependency to require specific scopes"""
    
    def __init__(self, *required_scopes: str):
        self.required_scopes = required_scopes
    
    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        if not any(scope in current_user.scopes for scope in self.required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required: {', '.join(self.required_scopes)}"
            )
        return current_user

# Common permission dependencies
require_read = RequireScopes("read", "admin")
require_write = RequireScopes("write", "admin")
require_control = RequireScopes("control", "admin")
require_admin = RequireScopes("admin")

def create_tokens_for_user(user: UserInDB) -> Token:
    """Create access and refresh tokens for user"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": user.username}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope=" ".join(user.scopes)
    ) 