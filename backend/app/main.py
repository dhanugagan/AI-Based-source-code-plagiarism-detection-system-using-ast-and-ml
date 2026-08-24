"""
Application entrypoint.

Run with:
    uvicorn app.main:app --reload
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import init_db
from app.utils.rate_limit import RateLimitMiddleware
from app.routes import auth, users, submissions, comparisons, reports, dashboard, admin, batch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("plagiarism_api")

app = FastAPI(
    title="AI-Based Source Code Plagiarism Detection System",
    description="Detects source-code plagiarism via AST analysis and machine learning.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic abuse protection: fixed-window rate limiting per client IP.
app.add_middleware(RateLimitMiddleware, max_requests=180, window_seconds=60)


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("Database initialized.")


# --- Centralized error handling: never leak internal stack traces ----------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid request data.", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server error")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


# --- Routers -----------------------------------------------------------------

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(submissions.router)
app.include_router(comparisons.router)
app.include_router(batch.router)
app.include_router(reports.router)
app.include_router(dashboard.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {
        "name": "AI-Based Source Code Plagiarism Detection System",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
