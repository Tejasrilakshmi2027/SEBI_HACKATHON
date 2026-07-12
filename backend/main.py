from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.session import engine, Base
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.redis import connect_to_redis, close_redis_connection
from app.api import auth, scans, dashboard, notifications, users, email_phishing, pdf_verification, deepfake_detection


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Connect to Redis
    await connect_to_redis()
    
    yield
    
    # Shutdown
    await close_mongo_connection()
    await close_redis_connection()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["authentication"])
app.include_router(scans.router, prefix=f"{settings.API_V1_PREFIX}/scans", tags=["scans"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_PREFIX}/dashboard", tags=["dashboard"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_PREFIX}/notifications", tags=["notifications"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])
app.include_router(email_phishing.router, prefix=f"{settings.API_V1_PREFIX}/email-phishing", tags=["email-phishing"])
app.include_router(pdf_verification.router, prefix=f"{settings.API_V1_PREFIX}/pdf-verification", tags=["pdf-verification"])
app.include_router(deepfake_detection.router, prefix=f"{settings.API_V1_PREFIX}/deepfake-detection", tags=["deepfake-detection"])


@app.get("/")
async def root():
    return {
        "message": "SEBI Sentinel AI - AI-Powered Multi-Modal Detection & Verification Platform",
        "version": settings.APP_VERSION,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
