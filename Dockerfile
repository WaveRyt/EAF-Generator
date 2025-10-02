# === Base image ===
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# === System packages: Python + LibreOffice + fonts ===
RUN apt-get update && \
    apt-get install -y \
        python3 python3-pip python3-venv \
        libreoffice libreoffice-writer libreoffice-java-common libreoffice-common \
        fonts-dejavu-core fonts-liberation \
        ttf-mscorefonts-installer fontconfig cabextract xfonts-utils && \
    fc-cache -fv && \
    rm -rf /var/lib/apt/lists/*

# === Working directory ===
WORKDIR /app
COPY . /app

# === Python deps ===
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# === Port for Render ===
EXPOSE 5000

# === Start Gunicorn ===
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT", "--workers", "2"]
