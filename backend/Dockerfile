FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --prefix=/install --no-warn-script-location -r requirements.txt

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/install/lib/python3.12/site-packages" \
    PATH="/install/bin:/usr/local/bin:/usr/bin:/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /install

RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --create-home --shell /bin/bash app

WORKDIR /app

COPY --chown=app:app . .

RUN mkdir -p /app/uploads /app/static \
    && chown -R app:app /app/uploads /app/static

COPY --chown=app:app docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

USER app

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]