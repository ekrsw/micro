import httpx
from fastapi import HTTPException, status, Request
from jose import jwt, JWTError

from app.core.config import settings

async def forward_request(request: Request, path: str, service_url: str, token: str = None):
    """
    Forward the request to the appropriate service
    """
    # Get the request method
    method = request.method.lower()
    
    # Get the request body
    body = await request.body()
    
    # Get the request headers
    headers = dict(request.headers)
    
    # Remove host header to avoid conflicts
    if "host" in headers:
        del headers["host"]
    
    # Add authorization header if token is provided
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Construct the target URL
    url = f"{service_url}{path}"
    
    # Create an httpx client
    async with httpx.AsyncClient() as client:
        try:
            # Forward the request
            response = await getattr(client, method)(
                url,
                headers=headers,
                content=body,
                params=request.query_params,
                follow_redirects=True,
            )
            
            # Return the response
            return {
                "status_code": response.status_code,
                "content": response.content,
                "headers": dict(response.headers),
            }
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service unavailable: {str(exc)}",
            )

async def verify_token(token: str):
    """
    Verify the JWT token with the auth service
    """
    try:
        # Decode the token to get the user ID
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify the token with the auth service
    auth_url = f"{settings.AUTH_SERVICE_URL}{settings.API_V1_STR}/auth/verify-token"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                auth_url,
                params={"user_id": user_id},
            )
            
            if response.status_code != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return response.json()
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable",
            )
