from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import structlog
import os
import time

logger = structlog.get_logger()

app = FastAPI(title="CrowdPark Analytics API", version="0.1.0")

# CORS — allow api to call analytics via docker network; no strict origin needed internally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID propagation + structlog context
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id", "")
    start = time.time()
    response = await call_next(request)
    if request_id:
        response.headers["x-request-id"] = request_id
    # Log with latency
    latency_ms = int((time.time() - start) * 1000)
    logger.info("request", path=request.url.path, method=request.method, request_id=request_id, latency_ms=latency_ms, status=response.status_code)
    return response

@app.get("/health")
def health_check():
    logger.info("health_check")
    return {"status": "ok", "service": "analytics", "version": "0.1.0"}

# Placeholder — estimate/spp/walk will be added in TASK-004/005/006
# from . import estimate, spp, walk
# app.include_router(estimate.router, prefix="/analyze")
