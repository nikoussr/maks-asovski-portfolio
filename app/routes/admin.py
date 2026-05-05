import io
import re
import uuid
from pathlib import Path
from typing import List, Optional

from PIL import Image

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..auth import create_session_token, is_authenticated
from ..config import settings
from ..database import get_db
from ..models import Project, ProjectImage, SiteSettings
from ..templates_config import templates

router = APIRouter(prefix="/admin")


def slugify(text: str) -> str:
    translit = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
        "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }
    text = text.lower()
    result = ""
    for char in text:
        result += translit.get(char, char)
    result = re.sub(r"[^a-z0-9]+", "-", result)
    return result.strip("-")


_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif"}
_VIDEO_EXTS = {".mp4", ".webm", ".mov", ".avi", ".mkv", ".m4v"}


async def save_upload(file: UploadFile, max_width: int = 1920, quality: int = 85) -> str:
    content = await file.read()
    ext = Path(file.filename).suffix.lower()

    if ext in _IMAGE_EXTS:
        try:
            from PIL import ImageOps
            img = Image.open(io.BytesIO(content))
            img = ImageOps.exif_transpose(img)  # apply EXIF rotation before anything else
            if img.width > max_width:
                new_height = int(img.height * max_width / img.width)
                img = img.resize((max_width, new_height), Image.LANCZOS)
            img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="WEBP", quality=quality, method=4)
            content = buf.getvalue()
            ext = ".webp"
        except Exception:
            pass  # if Pillow fails, save original

    filename = f"{uuid.uuid4()}{ext}"
    upload_path = Path(settings.upload_dir) / filename
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    with open(upload_path, "wb") as f:
        f.write(content)
    return f"/uploads/{filename}"


async def save_video(file: UploadFile) -> str:
    import asyncio
    content = await file.read()
    ext = Path(file.filename).suffix.lower()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    uid = uuid.uuid4()
    # Save original to temp file
    tmp_path = upload_dir / f"tmp_{uid}{ext if ext in _VIDEO_EXTS else '.mp4'}"
    with open(tmp_path, "wb") as f:
        f.write(content)

    # Convert to H.264 MP4: universal browser support + compression + faststart
    out_filename = f"{uid}.mp4"
    out_path = upload_dir / out_filename
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-y", "-i", str(tmp_path),
        "-c:v", "libx264", "-crf", "23", "-preset", "medium",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(out_path),
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.communicate()

    tmp_path.unlink(missing_ok=True)

    # Fall back to original if ffmpeg failed
    if not out_path.exists():
        orig_filename = f"{uid}{ext if ext in _VIDEO_EXTS else '.mp4'}"
        tmp_path.rename(upload_dir / orig_filename)
        return f"/uploads/{orig_filename}"

    return f"/uploads/{out_filename}"


# ─── Auth ────────────────────────────────────────────────────────────────────

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/admin", status_code=302)
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if username == settings.admin_username and password == settings.admin_password:
        token = create_session_token(username)
        response = RedirectResponse(url="/admin", status_code=302)
        response.set_cookie("admin_session", token, httponly=True, samesite="lax")
        return response
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request, "error": "Неверный логин или пароль"},
        status_code=400,
    )


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("admin_session")
    return response


# ─── Dashboard ───────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    projects = (
        db.query(Project)
        .order_by(Project.display_order, Project.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        "admin/dashboard.html", {"request": request, "projects": projects}
    )


# ─── Projects ────────────────────────────────────────────────────────────────

@router.get("/projects/new", response_class=HTMLResponse)
async def new_project_form(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    return templates.TemplateResponse(
        "admin/project_form.html",
        {"request": request, "project": None, "action": "create"},
    )


@router.post("/projects/new")
async def create_project(
    request: Request,
    title: str = Form(...),
    slug: str = Form(""),
    description: str = Form(""),
    role_checks: List[str] = Form(default=[]),
    role_custom: str = Form(""),
    cat_checks: List[str] = Form(default=[]),
    client: str = Form(""),
    year: Optional[str] = Form(None),
    video_embed: str = Form(""),
    is_published: Optional[str] = Form(None),
    is_featured: Optional[str] = Form(None),
    featured_order: Optional[str] = Form(None),
    display_order: Optional[str] = Form(None),
    order_ai_video: Optional[str] = Form(None),
    order_motion_design: Optional[str] = Form(None),
    order_commercial: Optional[str] = Form(None),
    cover_image: UploadFile = File(None),
    video_file: UploadFile = File(None),
    process_images: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    def to_int(v): return int(v) if v and v.strip().isdigit() else 0

    year_int = int(year) if year and year.strip().isdigit() else None
    order_int = to_int(display_order)
    featured_order_int = to_int(featured_order)
    published = is_published is not None
    featured = is_featured is not None
    custom_parts = [r.strip() for r in role_custom.split(",") if r.strip()]
    role = ", ".join(role_checks + [r for r in custom_parts if r not in role_checks])
    categories = ", ".join(cat_checks)

    if video_file and video_file.filename:
        video_embed = await save_video(video_file)

    if not slug:
        slug = slugify(title)

    base_slug = slug
    counter = 1
    while db.query(Project).filter(Project.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    cover_path = ""
    if cover_image and cover_image.filename:
        cover_path = await save_upload(cover_image)

    project = Project(
        title=title,
        slug=slug,
        description=description,
        role=role,
        client=client,
        year=year_int,
        video_embed=video_embed,
        cover_image=cover_path,
        is_published=published,
        is_featured=featured,
        featured_order=featured_order_int,
        display_order=order_int,
        order_ai_video=to_int(order_ai_video),
        order_motion_design=to_int(order_motion_design),
        order_commercial=to_int(order_commercial),
        categories=categories,
    )
    db.add(project)
    db.flush()

    for i, img in enumerate(process_images):
        if img and img.filename:
            img_path = await save_upload(img, max_width=1280, quality=80)
            db.add(ProjectImage(project_id=project.id, file_path=img_path, order=i))

    db.commit()
    return RedirectResponse(url="/admin", status_code=302)


@router.get("/projects/{project_id}/edit", response_class=HTMLResponse)
async def edit_project_form(
    project_id: int, request: Request, db: Session = Depends(get_db)
):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return RedirectResponse(url="/admin", status_code=302)
    return templates.TemplateResponse(
        "admin/project_form.html",
        {"request": request, "project": project, "action": "edit"},
    )


@router.post("/projects/{project_id}/edit")
async def update_project(
    project_id: int,
    request: Request,
    title: str = Form(...),
    slug: str = Form(""),
    description: str = Form(""),
    role_checks: List[str] = Form(default=[]),
    role_custom: str = Form(""),
    cat_checks: List[str] = Form(default=[]),
    client: str = Form(""),
    year: Optional[str] = Form(None),
    video_embed: str = Form(""),
    is_published: Optional[str] = Form(None),
    is_featured: Optional[str] = Form(None),
    featured_order: Optional[str] = Form(None),
    display_order: Optional[str] = Form(None),
    order_ai_video: Optional[str] = Form(None),
    order_motion_design: Optional[str] = Form(None),
    order_commercial: Optional[str] = Form(None),
    cover_image: UploadFile = File(None),
    video_file: UploadFile = File(None),
    process_images: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return RedirectResponse(url="/admin", status_code=302)

    def to_int(v): return int(v) if v and v.strip().isdigit() else 0

    year_int = int(year) if year and year.strip().isdigit() else None
    order_int = to_int(display_order)
    featured_order_int = to_int(featured_order)
    published = is_published is not None
    featured = is_featured is not None
    custom_parts = [r.strip() for r in role_custom.split(",") if r.strip()]
    role = ", ".join(role_checks + [r for r in custom_parts if r not in role_checks])
    categories = ", ".join(cat_checks)

    if video_file and video_file.filename:
        video_embed = await save_video(video_file)

    if not slug:
        slug = slugify(title)

    base_slug = slug
    counter = 1
    while (
        db.query(Project)
        .filter(Project.slug == slug, Project.id != project_id)
        .first()
    ):
        slug = f"{base_slug}-{counter}"
        counter += 1

    project.title = title
    project.slug = slug
    project.description = description
    project.role = role
    project.client = client
    project.year = year_int
    project.video_embed = video_embed
    project.is_published = published
    project.is_featured = featured
    project.featured_order = featured_order_int
    project.display_order = order_int
    project.order_ai_video = to_int(order_ai_video)
    project.order_motion_design = to_int(order_motion_design)
    project.order_commercial = to_int(order_commercial)
    project.categories = categories

    if cover_image and cover_image.filename:
        project.cover_image = await save_upload(cover_image)

    for i, img in enumerate(process_images):
        if img and img.filename:
            img_path = await save_upload(img)
            max_order = len(project.images)
            db.add(
                ProjectImage(project_id=project.id, file_path=img_path, order=max_order + i)
            )

    db.commit()
    return RedirectResponse(url=f"/admin/projects/{project_id}/edit", status_code=302)


@router.post("/projects/{project_id}/delete")
async def delete_project(
    project_id: int, request: Request, db: Session = Depends(get_db)
):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        db.delete(project)
        db.commit()
    return RedirectResponse(url="/admin", status_code=302)


@router.post("/images/{image_id}/delete")
async def delete_image(
    image_id: int, request: Request, db: Session = Depends(get_db)
):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    image = db.query(ProjectImage).filter(ProjectImage.id == image_id).first()
    if image:
        project_id = image.project_id
        db.delete(image)
        db.commit()
        return RedirectResponse(
            url=f"/admin/projects/{project_id}/edit", status_code=302
        )
    return RedirectResponse(url="/admin", status_code=302)


# ─── Site Settings ───────────────────────────────────────────────────────────

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    site_settings = db.query(SiteSettings).first()
    if not site_settings:
        site_settings = SiteSettings()
        db.add(site_settings)
        db.commit()
        db.refresh(site_settings)
    return templates.TemplateResponse(
        "admin/settings.html", {"request": request, "settings": site_settings}
    )


@router.post("/settings")
async def update_settings(
    request: Request,
    bio: str = Form(""),
    telegram: str = Form(""),
    instagram: str = Form(""),
    vk: str = Form(""),
    email: str = Form(""),
    youtube: str = Form(""),
    photo: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    site_settings = db.query(SiteSettings).first()
    if not site_settings:
        site_settings = SiteSettings()
        db.add(site_settings)

    site_settings.bio = bio
    site_settings.telegram = telegram
    site_settings.instagram = instagram
    site_settings.vk = vk
    site_settings.email = email
    site_settings.youtube = youtube

    if photo and photo.filename:
        site_settings.photo_path = await save_upload(photo)

    db.commit()
    return RedirectResponse(url="/admin/settings", status_code=302)
