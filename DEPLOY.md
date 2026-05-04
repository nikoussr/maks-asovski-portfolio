# Деплой на VPS

## Требования

- Ubuntu 22.04+
- Docker + Docker Compose v2
- Nginx (на хосте)
- Git

---

## Структура на сервере

```
~/
├── portfolio/          # Рабочая копия (разворачивается хуком)
│   ├── docker-compose.yml
│   ├── .env            # Секреты (не в git)
│   └── ...
├── portfolio.git/      # Bare-репозиторий
│   └── hooks/
│       └── post-receive
└── deploy.log          # Лог последнего деплоя
```

Диски:
```
/dev/vda  — основной диск (ОС, Docker, код)
/dev/vdb1 — отдельный диск → /mnt/data
              ├── uploads/   # фото и видео проектов
              └── postgres/  # данные PostgreSQL
```

---

## Первоначальная настройка

### 1. Подготовить сервер

```bash
# Установить Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Установить Nginx
sudo apt install nginx
```

### 2. Создать bare-репозиторий и хук

```bash
git init --bare ~/portfolio.git

cat > ~/portfolio.git/hooks/post-receive << 'EOF'
#!/bin/bash
GIT_WORK_TREE=~/portfolio git checkout -f master
echo "==> Деплой запущен в фоне. Логи: ~/deploy.log"
nohup bash -c "cd ~/portfolio && docker compose up --build -d >> ~/deploy.log 2>&1" &
EOF

chmod +x ~/portfolio.git/hooks/post-receive
```

### 3. Создать .env на сервере

```bash
cat > ~/portfolio/.env << 'EOF'
DATABASE_URL=postgresql://portfolio:ПАРОЛЬ@db:5432/portfolio
POSTGRES_PASSWORD=ПАРОЛЬ
SECRET_KEY=ДЛИННАЯ_СЛУЧАЙНАЯ_СТРОКА
ADMIN_USERNAME=admin
ADMIN_PASSWORD=ПАРОЛЬ
UPLOAD_DIR=/uploads
EOF
```

### 4. Подготовить диск для медиафайлов (опционально)

```bash
# Разметить и отформатировать второй диск
sudo fdisk /dev/vdb         # создать раздел
sudo mkfs.ext4 /dev/vdb1
sudo mkdir -p /mnt/data

# Добавить в /etc/fstab для автомонтирования
UUID=$(sudo blkid -s UUID -o value /dev/vdb1)
echo "UUID=$UUID /mnt/data ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo mount -a

# Создать директории для volumes
sudo mkdir -p /mnt/data/uploads /mnt/data/postgres
```

### 5. Настроить Nginx

```nginx
# /etc/nginx/sites-available/portfolio
server {
    listen 80;
    server_name ВАШ_ДОМЕН;

    client_max_body_size 1024M;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/portfolio /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 6. Добавить remote и запушить

```bash
# Локально
git remote add origin ssh://USER@IP:PORT/home/USER/portfolio.git
git push origin master
```

---

## Полезные команды

```bash
# Статус контейнеров
cd ~/portfolio && docker compose ps

# Логи приложения
docker compose logs -f web

# Лог последнего деплоя
cat ~/deploy.log

# Подключиться к БД
docker exec -it portfolio-db-1 psql -U portfolio -d portfolio

# Место на дисках
df -h

# Файлы загрузок
ls /mnt/data/uploads/
```

---

## Переменные окружения

| Переменная | Описание |
|-----------|---------|
| `DATABASE_URL` | Строка подключения PostgreSQL |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL |
| `SECRET_KEY` | Секрет для подписи cookie |
| `ADMIN_USERNAME` | Логин в админку |
| `ADMIN_PASSWORD` | Пароль в админку |
| `UPLOAD_DIR` | Путь для загрузок внутри контейнера (`/uploads`) |
