from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.core.config import get_settings
from .api.core.database import connect_db, close_db, get_db
from .api.routes import auth, complaints, categories, leaderboards, files, ai, geo, classify, admin, whatsapp

settings = get_settings()


async def seed_super_admin():
    """Create super admin on first startup if not exists."""
    from .api.services.users import hash_password
    from datetime import datetime, timezone
    
    try:
        db = get_db()
        if db is None:
            return
        
        # Check if super admin exists
        existing = await db.users.find_one({"role": "super_admin"})
        if not existing:
            await db.users.insert_one({
                "name": "Super Admin",
                "phone": "9999999999",
                "password_hash": hash_password("admin123"),
                "role": "super_admin",
                "department_id": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            })
            print("[OK] Super admin created: phone=9999999999, password=admin123")
    except Exception as e:
        print(f"[WARN] Could not seed super admin: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    await connect_db()
    await seed_super_admin()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered civic grievance platform for Delhi",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "http://localhost:5173",  # Vite dev
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"  # TODO: Restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(complaints.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)
app.include_router(leaderboards.router, prefix=settings.API_V1_PREFIX)
app.include_router(files.router, prefix=settings.API_V1_PREFIX)
app.include_router(ai.router, prefix=settings.API_V1_PREFIX)
app.include_router(geo.router, prefix=settings.API_V1_PREFIX)
app.include_router(classify.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
app.include_router(whatsapp.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get(f"{settings.API_V1_PREFIX}/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
