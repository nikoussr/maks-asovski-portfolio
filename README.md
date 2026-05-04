# Портфолио видеографа

Сайт-портфолио для видеографа и монтажёра Максима Асовского.
Минималистичный дизайн, кастомная CMS, автодеплой через git.

**Стек:** Python · FastAPI · PostgreSQL · Docker · Nginx

---

## Возможности

**Публичная часть**
- Сетка проектов с обложками (shimmer-скелетон при загрузке)
- Страница проекта: видео-плеер, описание, фото процесса с lightbox
- Страница «О себе» с контактами
- Поддержка видео: прямая загрузка MP4/WebM/MOV, YouTube, Vimeo, iframe-embed

**Административная панель**
- Создание и редактирование проектов
- Загрузка видеофайлов до 1 ГБ с прогресс-баром
- Автоматическое сжатие изображений в WebP (Pillow)
- Несколько ролей на проект (Video Editor, Motion Designer и др.)
- Настройки сайта: фото, bio, контакты

**Инфраструктура**
- Docker Compose (web + PostgreSQL)
- Автодеплой через git bare repo + post-receive hook
- Медиафайлы на отдельном диске (Docker bind mount)
- Cache-Control заголовки для статики и загрузок

---

## Стек

| Слой | Технология |
|------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy |
| Шаблоны | Jinja2 (SSR) |
| База данных | PostgreSQL 16 |
| Изображения | Pillow (resize + WebP) |
| Аутентификация | Cookie + itsdangerous |
| Инфраструктура | Docker Compose, Nginx |
| Деплой | Git bare repo + post-receive hook |

---

## Структура проекта

```
app/
├── main.py              # FastAPI app, cache middleware
├── models.py            # Project, ProjectImage, SiteSettings
├── auth.py              # Cookie-based auth
├── config.py            # Pydantic settings
├── database.py          # SQLAlchemy session
├── templates_config.py  # Jinja2 globals (resolve_video, role_list...)
├── routes/
│   ├── public.py        # Публичные страницы
│   └── admin.py         # Админка, загрузка файлов
├── templates/           # Jinja2 HTML шаблоны
└── static/              # CSS, JS, favicon
docker-compose.yml
Dockerfile
```

---

## Локальный запуск

**Требования:** Docker, Docker Compose

```bash
git clone https://github.com/nikoussr/maks-asovski-portfolio
cd maks-asovski-portfolio

# Создать .env
cp .env.example .env
# Заполнить DATABASE_URL, SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD

docker compose up --build
```

Сайт: `http://localhost:8001`
Админка: `http://localhost:8001/admin`

---

## Деплой на VPS

Подробная инструкция: [DEPLOY.md](DEPLOY.md)

Краткая схема:
1. На сервере создаётся bare git-репозиторий с `post-receive` хуком
2. `git push origin master` → хук запускает `docker compose up --build -d`
3. Медиафайлы хранятся на отдельном диске через Docker bind mount — не теряются при пересборке
