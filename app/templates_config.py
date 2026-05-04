import re
from datetime import datetime
from fastapi.templating import Jinja2Templates

_ROLE_LEGACY = {
    "montage": "Монтаж",
    "shooting_montage": "Съёмка & Монтаж",
}

CATEGORIES = [
    {"slug": "ai-video",      "label": "AI Video"},
    {"slug": "motion-design", "label": "Motion Design"},
    {"slug": "commercial",    "label": "Commercial videos"},
]


def category_list(cats: str) -> list:
    if not cats:
        return []
    return [c.strip() for c in cats.split(",") if c.strip()]


ROLE_PRESETS = [
    "Video Editor",
    "Motion Designer",
    "Music & Sound Design",
    "AI Artist",
    "Edit",
]


def display_role(role: str) -> str:
    """Map legacy slug roles; pass display values and multi-role strings through."""
    if not role:
        return ""
    parts = [_ROLE_LEGACY.get(r.strip(), r.strip()) for r in role.split(",")]
    return ", ".join(p for p in parts if p)


def role_list(role: str) -> list:
    """Return role as a list of individual role strings."""
    if not role:
        return []
    return [r.strip() for r in display_role(role).split(",") if r.strip()]


def resolve_video_embed(value: str) -> dict:
    if not value:
        return None
    v = value.strip()
    if v.lower().startswith("<"):
        return {"type": "raw", "html": v}
    yt = re.search(r"(?:youtube\.com/(?:watch\?v=|shorts/)|youtu\.be/)([a-zA-Z0-9_-]{11})", v)
    if yt:
        return {"type": "iframe", "url": f"https://www.youtube.com/embed/{yt.group(1)}?rel=0&modestbranding=1"}
    vm = re.search(r"vimeo\.com/(\d+)", v)
    if vm:
        return {"type": "iframe", "url": f"https://player.vimeo.com/video/{vm.group(1)}"}
    if v.startswith("/uploads/"):
        return {"type": "video", "url": v}
    return {"type": "iframe", "url": v}


templates = Jinja2Templates(directory="app/templates")
templates.env.globals["now_year"] = datetime.now().year
templates.env.globals["resolve_video"] = resolve_video_embed
templates.env.globals["display_role"] = display_role
templates.env.globals["role_list"] = role_list
templates.env.globals["ROLE_PRESETS"] = ROLE_PRESETS
templates.env.globals["CATEGORIES"] = CATEGORIES
templates.env.globals["category_list"] = category_list
