# Beauty Platform API

## Установка и запуск

> Требуется **Python ≥ 3.10** (на 3.9 не устанавливаются security-фиксы starlette/fastapi).

1. Создание и активация виртуального окружения:
```bash
python3.11 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
```

2. Установка зависимостей:
```bash
pip install -r requirements.txt
```

3. Секреты и ключи (НЕ коммитятся, см. .gitignore):
```bash
cp .env.example .env              # заполнить SECRET_KEY и POSTGRES_PASSWORD
python -m app.scripts.gen_keys    # сгенерировать пару RS256-ключей в keys/
```
Сгенерировать SECRET_KEY: `python -c "import secrets; print(secrets.token_urlsafe(48))"`

4. Инфраструктура и запуск:
```bash
docker compose up -d db redis     # PostgreSQL + Redis
alembic upgrade head              # миграции
python main.py
```

Dev-данные (`python -m app.scripts.seed_data`) создаются с паролем `Seedpass1`.

## Безопасность

Что сделано по итогам аудита ИБ (см. конспект «Комментарии по ИБ»):

- **Секреты** — `SECRET_KEY`, креды БД и URL alembic вынесены в `.env`; ключи RS256 — в `keys/` (gitignore). Скомпрометированный публикацией ключ при деплое **обязательно ротировать**.
- **JWT** — RS256 (асимметрично) на `PyJWT` вместо `python-jose`; короткий access-токен (60 мин).
- **Пароли** — единый модуль `app/core/security.py`, Argon2id (passlib); старые bcrypt/pbkdf2 переподписываются при логине; сырой sha256 больше не принимается; политика сложности.
- **Доступ (A01)** — роль при регистрации назначает сервер (нет privilege escalation); отзыв только при завершённой записи (`ReviewService`); уникальный пароль создаваемому мастеру.
- **Rate limiting** — slowapi (Redis-backend) на login + блокировка по телефону; пример Nginx ниже.
- **CSRF / заголовки / CORS** — проверка Origin/Referer для cookie-мутаций, security-заголовки, явный CORS-список; cookie `Secure` в проде.
- **SCA** — `requirements.txt` обновлён, `pip-audit` чист. Драйвер БД — `asyncpg` (psycopg2 убран).

### Nginx — грубый лимит флуда по IP (уровень до приложения)
```nginx
limit_req_zone $binary_remote_addr zone=login_zone:10m rate=10r/s;

location ~ ^/api/v1/auth/(login|login-web)$ {
    limit_req zone=login_zone burst=5 nodelay;
    limit_req_status 429;
    proxy_pass http://app;
}
```

### SCA в CI (Shift Left)
Добавить в пайплайн, чтобы новые CVE ловились автоматически:
```bash
pip install pip-audit && pip-audit
```
 
## API Endpoints 
- GET /api/v1/users/ - список пользователей 
- GET /api/v1/services/ - список услуг 
- GET /api/v1/appointments/ - список записей 
## надо будет сделать Конвертации времени сейчас у нас строка