import os
import uvicorn
from fastapi import FastAPI, Response, Request
from dependencies import async_session

from routers import (
    device_route,
    data_route,
    task_route,
    auth_route,
    default_route,
)

app = FastAPI()

app.include_router(device_route.router)
app.include_router(default_route.router)
app.include_router(data_route.router)
app.include_router(task_route.router)
app.include_router(auth_route.router)


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
    try:
        port = os.environ.get("PORT", "8000")
        port = int(port)
    except ValueError:
        port = 5000
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
