# Образ Django-бекенду: gunicorn + наш код. База даних — окремий контейнер (див. docker-compose.yml).
FROM python:3.12-slim

# Не писати .pyc і не буферизувати stdout — логи одразу видно в `docker compose logs`
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Спочатку лише requirements: цей шар кешується, поки залежності не змінились
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запускаємось не від root: якщо в застосунку знайдуть вразливість,
# зловмисник не отримає root-права в контейнері
RUN chmod +x /app/entrypoint.sh \
    && adduser --disabled-password --gecos "" app \
    && mkdir -p /app/staticfiles \
    && chown -R app:app /app
USER app

EXPOSE 8000

# entrypoint.sh застосовує міграції та збирає статику, потім запускає CMD
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "potuzhno_shop.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
