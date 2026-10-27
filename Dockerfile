# ---------- Stage 1: Builder ----------
# Installs dependencies into an isolated virtualenv that the runtime stage copies.
FROM python:3.11-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# ---------- Stage 2: Test ----------
# Not part of the final image. Run it with: docker build --target test .
FROM builder AS test

COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY app.py .
COPY tests/ tests/
RUN pytest -q

# ---------- Stage 3: Runtime ----------
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Run as an unprivileged user instead of root.
RUN useradd --system --uid 10001 --no-create-home app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY app.py .

USER app

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=3)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "app:app"]
