"""
Authentication Router - Login, logout, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from pydantic import BaseModel

from auth.security import (
    authenticate_user, create_tokens_for_user, verify_token,
    User, Token, get_current_active_user
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return access/refresh tokens
    
    **Credentials:**
    - **admin/secret**: Full admin access (all scopes)
    - **operator/secret**: Read and write access  
    - **readonly/secret**: Read-only access
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    tokens = create_tokens_for_user(user)
    
    return LoginResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_in=tokens.expires_in,
        user=User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            disabled=user.disabled,
            scopes=user.scopes
        )
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_request: RefreshRequest):
    """
    Refresh access token using refresh token
    """
    try:
        # Verify refresh token
        token_data = verify_token(refresh_request.refresh_token)
        if not token_data or not token_data.username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user and create new tokens
        from auth.security import get_user
        user = get_user(token_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        tokens = create_tokens_for_user(user)
        return tokens
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout user (client should delete tokens)
    """
    return {
        "message": f"User {current_user.username} logged out successfully",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information
    """
    return current_user

@router.get("/test-permissions")
async def test_permissions(current_user: User = Depends(get_current_active_user)):
    """
    Test endpoint to check user permissions
    """
    return {
        "username": current_user.username,
        "scopes": current_user.scopes,
        "permissions": {
            "can_read": "read" in current_user.scopes or "admin" in current_user.scopes,
            "can_write": "write" in current_user.scopes or "admin" in current_user.scopes,
            "can_control": "control" in current_user.scopes or "admin" in current_user.scopes,
            "is_admin": "admin" in current_user.scopes
        },
        "message": "Authentication successful"
    } 