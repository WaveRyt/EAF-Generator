# === Base image ===
FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install Python, LibreOffice, fonts, and utilities
RUN apt-get update && \
    apt-get install -y \
        python3 python3-pip \
        libreoffice-core libreoffice-writer libreoffice-java-common \
        fonts-dejavu-core ttf-mscorefonts-installer fontconfig cabextract xfonts-utils && \
    fc-cache -fv && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Set environment variables for Flask (optional defaults)
ENV FLASK_ENV=production
ENV FLASK_APP=app.py

# Expose port 5000
EXPOSE 5000

# Start Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2"]
