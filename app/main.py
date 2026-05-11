from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator

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


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    from .templates_config import templates
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


app.include_router(public_router)
app.include_router(admin_router)

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
