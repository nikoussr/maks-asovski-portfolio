from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import Base, engine
from .routes.admin import router as admin_router
from .routes.public import router as public_router

Base.metadata.create_all(bind=engine)
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Максим Асовский — Портфолио", docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.middleware("http")
async def cache_static(request: Request, call_next) -> Response:
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/uploads/"):
        response.headers["Cache-Control"] = "public, max-age=2592000, immutable"  # 30 days
    elif path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=86400"  # 1 day
    return response


app.include_router(public_router)
app.include_router(admin_router)
