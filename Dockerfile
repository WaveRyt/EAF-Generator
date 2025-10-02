# === Base image ===
FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Copy app
COPY . /app

# Install Python, LibreOffice, fonts, and dependencies
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

# Expose port
EXPOSE 5000

# Start Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2"]
