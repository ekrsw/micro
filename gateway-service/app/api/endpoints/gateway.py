from typing import Any, Optional
from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse, StreamingResponse

from app.core.config import settings
from app.services.proxy import forward_request, verify_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    return await verify_token(token)

@router.get("/auth/{path:path}")
async def auth_proxy(request: Request, path: str):
    """
    Proxy requests to the auth service
    """
    response_data = await forward_request(
        request=request,
        path=f"{settings.API_V1_STR}/auth/{path}",
        service_url=settings.AUTH_SERVICE_URL,
    )
    
    return Response(
        content=response_data["content"],
        status_code=response_data["status_code"],
        headers=response_data["headers"],
    )

@router.post("/auth/{path:path}")
async def auth_proxy_post(request: Request, path: str):
    """
    Proxy POST requests to the auth service
    """
    response_data = await forward_request(
        request=request,
        path=f"{settings.API_V1_STR}/auth/{path}",
        service_url=settings.AUTH_SERVICE_URL,
    )
    
    return Response(
        content=response_data["content"],
        status_code=response_data["status_code"],
        headers=response_data["headers"],
    )

@router.get("/protected-resource")
async def protected_resource(current_user: Any = Depends(get_current_user)):
    """
    Example of a protected resource that requires authentication
    """
    return {
        "message": "This is a protected resource",
        "user": current_user,
    }

@router.get("/public-resource")
async def public_resource():
    """
    Example of a public resource that doesn't require authentication
    """
    return {
        "message": "This is a public resource",
    }
