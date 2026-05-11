# Портфолио видеографа

## Ссылка - https://asovskii.com

Сайт-портфолио для видеографа и монтажёра Максима Асовского.

**Стек:** Python · FastAPI · PostgreSQL · Docker · Nginx

---

## Возможности

**Публичная часть**
- Сетка проектов с обложками
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
- CI/CD через GitHub Actions (автодеплой при пуше в main)
- Медиафайлы на отдельном диске (Docker bind mount → `/mnt/data`)
- Nginx reverse proxy: gzip-сжатие, Cache-Control, SSL/TLS (Let's Encrypt)
- FFmpeg: конвертация загружаемых видео в H.264 MP4 с `-movflags +faststart`

**Observability (SRE)**
- Prometheus + Grafana
- Node Exporter: метрики CPU, RAM, диска (`/` и `/mnt/data`)
- Просмотры каждого проекта по slug
- FastAPI instrumentation: HTTP запросы, latency p95
- Дашборд: uptime приложения, ошибки 4xx/5xx, топ просматриваемых проектов

---
## Скрины
<img width="1266" height="1018" alt="image" src="https://github.com/user-attachments/assets/cd39329c-17b5-4500-9677-5aba03c53585" />

---

<img width="1248" height="1241" alt="image" src="https://github.com/user-attachments/assets/48731557-bf77-492e-810a-a76dd09cbac5" />
<img width="1244" height="1149" alt="image" src="https://github.com/user-attachments/assets/f222ed3f-6392-4240-b3fd-b673e6b975a0" />

---

<img width="1254" height="611" alt="image" src="https://github.com/user-attachments/assets/da6d8684-704a-401b-871c-e29928f56d8c" />

---

<img width="1267" height="490" alt="image" src="https://github.com/user-attachments/assets/a9fbf4f5-97dc-4584-b6ac-a59f51757b81" />

---

<img width="1032" height="1202" alt="image" src="https://github.com/user-attachments/assets/12b4fad0-a440-4a9a-bbc3-1388b39ca29f" />
<img width="1034" height="1205" alt="image" src="https://github.com/user-attachments/assets/3f6b07f1-0692-499b-991f-dcf90ebac17e" />
<img width="1035" height="198" alt="image" src="https://github.com/user-attachments/assets/e7348500-014c-486a-bafc-097354b40b7b" />

---

<img width="963" height="1060" alt="image" src="https://github.com/user-attachments/assets/18d2f287-c431-4b67-a871-0e988b8ed5da" />

---

<img width="2243" height="1311" alt="image" src="https://github.com/user-attachments/assets/21a1443c-cf1b-4b66-8e01-cfca92d28ce9" />

---



## Стек

| Слой | Технология |
|------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy |
| Шаблоны | Jinja2 (SSR) |
| База данных | PostgreSQL 16 |
| Изображения | Pillow (resize + WebP) |
| Аутентификация | Cookie + itsdangerous |
| Медиа | FFmpeg (H.264 конвертация), Pillow (resize + WebP) |
| Инфраструктура | Docker Compose, Nginx, Let's Encrypt |
| CI/CD | GitHub Actions |
| Мониторинг | Prometheus, Grafana, Node Exporter |

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
