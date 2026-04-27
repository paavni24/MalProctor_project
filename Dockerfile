# syntax=docker/dockerfile:1

# ── Stage 1: Python + Java + apktool base ──
FROM python:3.10-slim

# Install Java (required by apktool)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        default-jre-headless \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Download apktool jar
RUN mkdir -p /opt/apktool && \
    curl -L https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar \
         -o /opt/apktool/apktool.jar

# Create apktool wrapper on PATH
RUN printf '#!/bin/sh\nexec java -jar /opt/apktool/apktool.jar "$@"\n' \
         > /usr/local/bin/apktool && \
    chmod +x /usr/local/bin/apktool

# ── Stage 2: Python dependencies ──
WORKDIR /app

# Copy and install requirements first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 3: App code ──
COPY apk_scanner.py app.py ./
COPY templates/ templates/
COPY data/best_model.pkl data/best_model.pkl
COPY data/scaler.pkl     data/scaler.pkl

# Ensure temp dirs exist
RUN mkdir -p temp_uploads temp_decompiled

# ── Run ──
ENV PORT=8080
EXPOSE 8080

CMD ["python", "app.py"]
