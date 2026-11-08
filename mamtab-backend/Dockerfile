FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app/src

RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --home /app app

COPY src/requirements.txt .
RUN pip install -r requirements.txt

# Stessa struttura del repo: src/ accanto a PostgreSQL.sql e gtfs_data/
COPY --chown=app:app PostgreSQL.sql /app/PostgreSQL.sql
COPY --chown=app:app gtfs_data /app/gtfs_data
COPY --chown=app:app src/ /app/src/
COPY --chown=app:app entrypoint.sh /app/entrypoint.sh

RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

USER app

EXPOSE 8000

# start-period lungo: al primo avvio importa ~12 MB di GTFS
HEALTHCHECK --interval=15s --timeout=5s --start-period=300s --retries=5 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4).status == 200 else 1)"

CMD ["/app/entrypoint.sh"]
