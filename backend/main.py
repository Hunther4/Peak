import logging
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.staticfiles import StaticFiles

from api.routes import assessments, books, cognitive, dashboard, health, mental, models, profile, sessions, skills
from api.routes.iq_practice import router as iq_practice_router
from api.routes.math_thinking import router as math_thinking_router
from api.routes.memory_game import router as memory_game_router
from api.routes.paes import router as paes_router
from core.auth import api_key_manager, auth_middleware
from core.database import create_db_and_tables
from core.limiter import limiter
from core.tasks import shutdown_executor

logger = logging.getLogger(__name__)



ALLOWED_UPLOAD_MIMES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/gif",
    "image/webp",
    "text/plain",
    "application/pdf",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers to every HTTP response with per-request nonce."""

    async def dispatch(self, request: Request, call_next):
        nonce = secrets.token_hex(16)  # 32-character hex string
        csp = (
            f"default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}'; "
            f"style-src 'self' 'nonce-{nonce}'; "
            f"img-src 'self' data: blob:; "
            f"font-src 'self' data:; "
            f"connect-src 'self'; "
            f"frame-ancestors 'none'"
        )
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = csp
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response


class UploadsMimeMiddleware(BaseHTTPMiddleware):
    """Ensures upload requests to /uploads/ only use whitelisted Content-Types."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/uploads"):
            if request.method in ("POST", "PUT", "PATCH"):
                content_type = request.headers.get("Content-Type", "").split(";")[0].strip().lower()
                if content_type and content_type not in ALLOWED_UPLOAD_MIMES and not content_type.startswith("image/"):
                    return Response(
                        content="Unsupported Media Type",
                        status_code=415,
                        media_type="text/plain",
                    )
        return await call_next(request)


def _check_cors_production_guard():
    origin = os.getenv("CORS_ORIGIN", "")
    is_prod = os.getenv("PRODUCTION") == "1"
    if origin == "*":
        if is_prod:
            raise RuntimeError("CORS_ORIGIN cannot be '*' in production")
        logger.warning("CORS_ORIGIN is '*' — do not use in production")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    _check_cors_production_guard()
    if os.getenv("DISABLE_AUTH") == "1":
        logger.warning("Authentication DISABLED — API is open")
    create_db_and_tables()
    raw_key = api_key_manager.initialize()
    if raw_key:
        logger.info(
            "API Key generated: %s**** — copy this key and store it securely. "
            "Set PEAK_API_KEY in .env to use your own key.",
            raw_key[:4],
        )
    yield
    shutdown_executor()


app = FastAPI(title="Peak Practice API", version="1.0.0", lifespan=lifespan)

_BASE = Path(__file__).resolve().parent
app.mount("/uploads", StaticFiles(directory=str(_BASE / "uploads")), name="uploads")

app.middleware("http")(auth_middleware)

# Security and MIME middlewares
app.add_middleware(UploadsMimeMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware — outermost so ALL responses, including auth errors and exceptions, get CORS headers
cors_env = os.getenv("CORS_ORIGIN", "http://localhost:5173,http://localhost:8081")
allowed_origins = [o.strip() for o in cors_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting — slowapi
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(assessments.router, prefix="/api/assessments", tags=["Assessments"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(books.router, prefix="/api/books", tags=["Books"])
app.include_router(mental.router, prefix="/api/mental", tags=["Mental"])
app.include_router(models.router, prefix="/api/models", tags=["Models"])
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(profile.router, prefix="/api", tags=["Profile"])
app.include_router(memory_game_router, prefix="/api/memory-game", tags=["memory-game"])
app.include_router(math_thinking_router, prefix="/api/math-thinking", tags=["math-thinking"])
app.include_router(cognitive.router, prefix="/api/cognitive", tags=["Cognitive"])
app.include_router(iq_practice_router, prefix="/api/iq-practice", tags=["IQ Practice"])
app.include_router(paes_router)


@app.get("/")
def root():
    return {"status": "Peak Practice API corriendo"}
