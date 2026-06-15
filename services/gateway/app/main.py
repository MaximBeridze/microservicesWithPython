import httpx
from fastapi import FastAPI, Request, Response
from jose import JWTError, jwt

from app.config import settings

app = FastAPI(title="gateway", version="1.0.0")

# Routing table — maps the resource name in the URL path to the target service base URL.
# Path structure: /{version}/{resource}/...
#   e.g. GET /v1/users/123  →  resource = "users"  →  forward to user_service_url
#
# Add new entries here as each module introduces a new service.
# Module 4 will add: "notifications"
# Module 5 will add: "consent", "logs"
# Module 6 will add: "auth"
ROUTES: dict[str, str] = {
    "users":      settings.user_service_url,
    "games":      settings.game_service_url,
    "activities": settings.activity_service_url,
    # Added in Module 4
    "notifications": settings.notification_service_url,
    # Added in Module 5
    "consent": settings.logging_service_url,
    "logs": settings.logging_service_url,
    # Added in Module 6
    "auth": settings.auth_service_url,
}


@app.get("/health")
async def health():
    """
    Gateway liveness check. Handled here — never forwarded to a service.
    In Module 10 this endpoint will be upgraded to fan out to all services
    and return their individual status.
    """
    return {"status": "ok", "service": "gateway"}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(request: Request, path: str):

    """
    Verify your implementation:
        curl http://localhost:8000/health
        curl http://localhost:8000/v1/users
        curl http://localhost:8000/v1/games
        curl http://localhost:8000/v1/activities
        curl http://localhost:8000/v1/unknown   # should return 404
    """
    segments = path.split("/")
    if len(segments) < 2:
        return Response(status_code=404, content="Not found")

    resource = segments[1]
    target_base = ROUTES.get(resource)

    if target_base is None:
        return Response(status_code=404, content=f"Unknown resource: {resource}")

    is_public_token_request = path == "v1/auth/token"
    if not is_public_token_request:
        authorization = request.headers.get("authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return Response(status_code=401, content="Missing or invalid token")

        token = authorization.removeprefix("Bearer ").strip()
        try:
            jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        except JWTError:
            return Response(status_code=401, content="Missing or invalid token")

    target_url = f"{target_base}/{path}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=request.headers.raw,
                content=await request.body(),
                params=request.query_params,
            )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type"),
        )

    except httpx.RequestError:
        return Response(status_code=503, content="Service unavailable")
