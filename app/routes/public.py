from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Project, SiteSettings
from ..templates_config import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, category: str = None, db: Session = Depends(get_db)):
    if category:
        projects = (
            db.query(Project)
            .filter(Project.is_published == True, Project.categories.contains(category))
            .order_by(Project.display_order, Project.created_at.desc())
            .all()
        )
    else:
        projects = (
            db.query(Project)
            .filter(Project.is_published == True, Project.is_featured == True)
            .order_by(Project.display_order, Project.created_at.desc())
            .all()
        )
    return templates.TemplateResponse("index.html", {
        "request": request,
        "projects": projects,
        "active_category": category or "",
    })


@router.get("/projects/{slug}", response_class=HTMLResponse)
async def project_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    project = (
        db.query(Project)
        .filter(Project.slug == slug, Project.is_published == True)
        .first()
    )
    if not project:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse("project.html", {"request": request, "project": project})


@router.get("/about", response_class=HTMLResponse)
async def about(request: Request, db: Session = Depends(get_db)):
    site_settings = db.query(SiteSettings).first()
    return templates.TemplateResponse(
        "about.html", {"request": request, "settings": site_settings}
    )
