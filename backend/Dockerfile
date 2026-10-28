FROM python:3.12-slim AS builder
WORKDIR /build
COPY pyproject.toml .
COPY app ./app
RUN pip wheel --no-cache-dir --wheel-dir /wheels .
FROM python:3.12-slim
RUN useradd --create-home --uid 10001 nexo
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY --chown=nexo:nexo . .
USER nexo
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
