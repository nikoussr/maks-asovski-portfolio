# Портфолио видеографа

## Ссылка - https://asovskii.com

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
## Скрины
<img width="1270" height="623" alt="image" src="https://github.com/user-attachments/assets/900f8952-71ef-44ce-a8c4-5cf4e8545449" />
<img width="1248" height="1019" alt="image" src="https://github.com/user-attachments/assets/3da0329b-2b90-4368-a7bb-ed1579f57fc1" />
<img width="1243" height="1138" alt="image" src="https://github.com/user-attachments/assets/8f0c84e1-5e37-4490-bc62-84364f1962c2" />
<img width="1248" height="594" alt="image" src="https://github.com/user-attachments/assets/b0485dd3-e936-445a-b8bf-d3f4a834f3f6" />
<img width="1262" height="429" alt="image" src="https://github.com/user-attachments/assets/83dfa481-4649-470f-af50-b42905a6e268" />
<img width="1248" height="1202" alt="image" src="https://github.com/user-attachments/assets/e9c25188-1a84-42c4-a7e0-fa1e41ffcff6" />
<img width="1242" height="1280" alt="image" src="https://github.com/user-attachments/assets/472918a8-f993-4cf5-8c74-23185e11d52c" />
<img width="1246" height="1278" alt="image" src="https://github.com/user-attachments/assets/17a4d46b-1305-47f2-a831-5edb33550cfe" />


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
