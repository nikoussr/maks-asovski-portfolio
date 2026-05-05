from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, default="")
    role = Column(String(200), default="")
    client = Column(String(200), default="")
    year = Column(Integer, nullable=True)
    video_embed = Column(Text, default="")
    cover_image = Column(String(500), default="")
    is_published = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    categories = Column(String(200), default="")
    is_featured = Column(Boolean, default=False)
    featured_order = Column(Integer, default=0)
    order_ai_video = Column(Integer, default=0)
    order_motion_design = Column(Integer, default=0)
    order_commercial = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    images = relationship(
        "ProjectImage",
        back_populates="project",
        order_by="ProjectImage.order",
        cascade="all, delete-orphan",
    )


class ProjectImage(Base):
    __tablename__ = "project_images"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    file_path = Column(String(500))
    caption = Column(String(500), default="")
    order = Column(Integer, default=0)

    project = relationship("Project", back_populates="images")


class SiteSettings(Base):
    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, index=True)
    bio = Column(Text, default="")
    photo_path = Column(String(500), default="")
    telegram = Column(String(200), default="")
    instagram = Column(String(200), default="")
    vk = Column(String(200), default="")
    email = Column(String(200), default="")
    youtube = Column(String(200), default="")
