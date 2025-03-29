from typing import Generator, Optional
import uuid

from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.db.session import get_db


async def validate_token(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Validate the authorization token with the auth service
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    # Make request to auth service to validate token
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_BASE_URL}/api/v1/users/me",
                headers={"Authorization": authorization}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )
            
            return response.json()
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )