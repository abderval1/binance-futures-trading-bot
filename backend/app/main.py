from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from .config import settings
from . import auth, schemas, crud
from .database import engine, Base
from .routes import users, api_keys, trading
from .routers import auth as auth_router
from .trading.scanner import stop_all_scanners
from .utils.logging import setup_logging
import logging

# Setup logging
logger = setup_logging()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events"""
    logger.info("Trading Bot API starting up...")
    yield
    # Shutdown: stop all running scanners gracefully
    logger.info("Shutting down - stopping all bot scanners...")
    await stop_all_scanners()
    logger.info("All scanners stopped. Goodbye!")


app = FastAPI(
    title="Binance Futures Trading Bot",
    version="1.0.0",
    lifespan=lifespan
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, dependencies=[Depends(auth.get_current_active_user)])
app.include_router(api_keys.router, dependencies=[Depends(auth.get_current_active_user)])
app.include_router(trading.router, dependencies=[Depends(auth.get_current_active_user)])


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "trading-bot"}


@app.get("/subscription-plans")
def get_plans():
    from .schemas import SUBSCRIPTION_PLANS
    return list(SUBSCRIPTION_PLANS.values())
