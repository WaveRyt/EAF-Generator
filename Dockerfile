# Use Ubuntu 22.04 as base
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system packages: Python + LibreOffice + fonts
RUN apt-get update && \
    apt-get install -y \
        python3 python3-pip python3-venv \
        libreoffice libreoffice-writer libreoffice-java-common \
        fonts-dejavu-core fonts-liberation \
        ttf-mscorefonts-installer fontconfig cabextract xfonts-utils && \
    fc-cache -fv && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
