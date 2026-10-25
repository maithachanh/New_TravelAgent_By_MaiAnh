from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import engine, Base, init_db_defaults
from app.api import (
    auth,
    destinations,
    trips,
    agent,
    bookings,
    flights,
    hotels,
    places,
    activities,
    currency,
    translation,
    websocket
)
import time
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize DB Tables and default records
Base.metadata.create_all(bind=engine)
init_db_defaults()

app = FastAPI(
    title="Universal AI Travel Agent API Gateway & Platform",
    description="Enterprise-grade AI Travel Agent Platform supporting all countries, cities, and villages worldwide in real-time.",
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Request rate limiter to protect API against DDoS/spamming
REQUEST_HISTORY = defaultdict(list)
RATE_LIMIT_PER_MINUTE = 180

# Circuit breaker state
CIRCUIT_BREAKER = {
    "failures": 0,
    "last_failure_time": 0,
    "state": "closed",  # closed, open, half-open
    "threshold": 5,
    "timeout": 60  # seconds
}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    if path in ["/", "/docs", "/openapi.json", "/redoc"] or path.startswith("/static"):
        return await call_next(request)

    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()
    cutoff = now - 60.0

    timestamps = [t for t in REQUEST_HISTORY[client_ip] if t > cutoff]
    if len(timestamps) >= RATE_LIMIT_PER_MINUTE:
        return JSONResponse(
            status_code=429,
            content={"detail": "Tần suất yêu cầu quá nhanh. Vui lòng thử lại sau giây lát (Rate limit exceeded)."}
        )

    timestamps.append(now)
    REQUEST_HISTORY[client_ip] = timestamps

    # Circuit breaker check
    if CIRCUIT_BREAKER["state"] == "open":
        if now - CIRCUIT_BREAKER["last_failure_time"] > CIRCUIT_BREAKER["timeout"]:
            CIRCUIT_BREAKER["state"] = "half-open"
            logger.info("Circuit breaker moving to half-open state")
        else:
            return JSONResponse(
                status_code=503,
                content={"detail": "Service temporarily unavailable. Please try again later."}
            )

    try:
        response = await call_next(request)
        # Reset circuit breaker on success if in half-open state
        if CIRCUIT_BREAKER["state"] == "half-open":
            CIRCUIT_BREAKER["state"] = "closed"
            CIRCUIT_BREAKER["failures"] = 0
            logger.info("Circuit breaker reset to closed state")
        return response
    except Exception as e:
        CIRCUIT_BREAKER["failures"] += 1
        CIRCUIT_BREAKER["last_failure_time"] = now

        if CIRCUIT_BREAKER["failures"] >= CIRCUIT_BREAKER["threshold"]:
            CIRCUIT_BREAKER["state"] = "open"
            logger.error(f"Circuit breaker opened after {CIRCUIT_BREAKER['failures']} failures")

        logger.error(f"Request failed: {str(e)}")
        raise

# Set up CORS for Web & Mobile Frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if "*" not in settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include All Domain Routers (mounted under standard and /ai prefixes for universal compatibility)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(agent.router, prefix=settings.API_V1_STR)
app.include_router(agent.router, prefix=f"{settings.API_V1_STR}/ai")
app.include_router(trips.router, prefix=settings.API_V1_STR)
app.include_router(trips.router, prefix=f"{settings.API_V1_STR}/ai")
app.include_router(bookings.router, prefix=settings.API_V1_STR)
app.include_router(bookings.router, prefix=f"{settings.API_V1_STR}/ai")
app.include_router(flights.router, prefix=settings.API_V1_STR)
app.include_router(hotels.router, prefix=settings.API_V1_STR)
app.include_router(places.router, prefix=settings.API_V1_STR)
app.include_router(activities.router, prefix=settings.API_V1_STR)
app.include_router(destinations.router, prefix=settings.API_V1_STR)
app.include_router(currency.router, prefix=settings.API_V1_STR)
app.include_router(translation.router, prefix=settings.API_V1_STR)
app.include_router(websocket.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": "Universal AI Travel Agent Platform",
        "version": "2.0.0",
        "status": "Online",
        "coverage": "Worldwide (Any Country, City, or Village in Real-Time)",
        "docs": "/docs"
    }
