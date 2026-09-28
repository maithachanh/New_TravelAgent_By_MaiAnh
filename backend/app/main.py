from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
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
    translation
)

# Initialize DB Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Universal AI Travel Agent API Gateway & Platform",
    description="Enterprise-grade AI Travel Agent Platform supporting all countries, cities, and villages worldwide in real-time.",
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS for Web & Mobile Frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include All Domain Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(agent.router, prefix=settings.API_V1_STR)
app.include_router(agent.router, prefix=f"{settings.API_V1_STR}/ai")
app.include_router(trips.router, prefix=settings.API_V1_STR)
app.include_router(bookings.router, prefix=settings.API_V1_STR)
app.include_router(flights.router, prefix=settings.API_V1_STR)
app.include_router(hotels.router, prefix=settings.API_V1_STR)
app.include_router(places.router, prefix=settings.API_V1_STR)
app.include_router(activities.router, prefix=settings.API_V1_STR)
app.include_router(destinations.router, prefix=settings.API_V1_STR)
app.include_router(currency.router, prefix=settings.API_V1_STR)
app.include_router(translation.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": "Universal AI Travel Agent Platform",
        "version": "2.0.0",
        "status": "Online",
        "coverage": "Worldwide (Any Country, City, or Village in Real-Time)",
        "docs": "/docs"
    }
