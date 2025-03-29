from typing import Dict, Any, Optional
import httpx
from fastapi import Request

from app.core.config import settings


async def proxy_request(
    service_url: str,
    path: str,
    request: Request,
    timeout: int = 60,
) -> Dict[str, Any]:
    """
    Proxy a request to a microservice
    """
    # Get request body if any
    request_body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        request_body = await request.json()
    
    # Get query parameters
    query_params = {}
    for key, value in request.query_params.items():
        if key in query_params:
            if isinstance(query_params[key], list):
                query_params[key].append(value)
            else:
                query_params[key] = [query_params[key], value]
        else:
            query_params[key] = value
    
    # Get headers
    headers = {}
    for key, value in request.headers.items():
        if key.lower() not in ["host", "content-length"]:
            headers[key] = value
    
    # Make request to the service
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=f"{service_url}{path}",
            params=query_params,
            json=request_body,
            headers=headers,
            timeout=timeout,
        )
        
        return {
            "status_code": response.status_code,
            "content": response.json() if response.headers.get("content-type") == "application/json" else response.text,
            "headers": dict(response.headers),
        }