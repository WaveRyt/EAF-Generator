# Use Ubuntu 22.04 full image
FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and LibreOffice
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv libreoffice libreoffice-writer && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Expose port for Render
EXPOSE 5000

# Start Gunicorn using the port Render provides
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT", "--workers", "2"]
