FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings_container

WORKDIR /app

COPY requirements.txt requirements-container.txt ./
RUN pip install --no-cache-dir -r requirements-container.txt

RUN groupadd --system app && useradd --system --gid app --home-dir /app app
COPY . .

# Collect assets without a live database or deployment credentials.
RUN DJANGO_SECRET_KEY=build-only-not-a-runtime-secret \
    DATABASE_URL=sqlite:///:memory: \
    DJANGO_ALLOWED_HOSTS=localhost \
    python manage.py collectstatic --noinput

USER app
EXPOSE 8000

CMD ["gunicorn", "--config", "gunicorn.conf.py", "config.wsgi:application"]
