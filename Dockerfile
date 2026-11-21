FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DATA_DIR=/data
LABEL org.opencontainers.image.source="https://github.com/jbkunama1/hAI.FlexPowerInfo" org.opencontainers.image.licenses="MIT"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd -u 10001 app && mkdir /data && chown app /data
COPY app.py core.py gateway.py telegram_service.py bot_visuals.py market_alerts.py alert_gateway.py ./
COPY static ./static
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=2)" || exit 1
CMD ["uvicorn","alert_gateway:app","--host","0.0.0.0","--port","8080","--workers","1","--no-access-log"]
