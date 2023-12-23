import uvicorn
from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse
from dependencies import async_session

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from routers import (
    device_route,
    data_route,
    task_route,
    auth_route,
    default_route,
)

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)

app.include_router(device_route.router)
app.include_router(default_route.router)
app.include_router(data_route.router)
app.include_router(task_route.router)
app.include_router(auth_route.router)


async def rate_limit_handler(request, exc):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = async_session()
        response = await call_next(request)
    except Exception as e:
        return Response(f"Internal server error: {e}", status_code=500)
    finally:
        await request.state.db.close()
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port="8000", log_level="info")
