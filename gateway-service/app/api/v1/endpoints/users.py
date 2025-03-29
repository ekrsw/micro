from fastapi import APIRouter, HTTPException, Request, Response, status

from app.core.config import settings
from app.services.proxy import proxy_request

router = APIRouter()


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    tags=["users"],
)
async def users_proxy(path: str, request: Request):
    """
    Proxy all user service requests
    """
    try:
        result = await proxy_request(
            service_url=settings.USER_SERVICE_URL,
            path=f"/api/v1/{path}",
            request=request,
        )
        
        return Response(
            content=result["content"] if isinstance(result["content"], str) else result["content"],
            status_code=result["status_code"],
            headers=result["headers"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"User service unavailable: {str(e)}",
        )