# ==============================
#       STAGE 1 : BUILDER
# ==============================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    libjpeg-dev zlib1g-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only dependency files
COPY requirements.txt .

# Build wheels (faster next builds)
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ==============================
#       STAGE 2 : RUNTIME
# ==============================
FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install runtime deps (without compiler)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    libjpeg62-turbo \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels + install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Copy actual project
COPY . .

EXPOSE 8000

# Gunicorn command
CMD ["gunicorn", "EscapeSaintonge.wsgi:application", "--bind", "0.0.0.0:8000"]
