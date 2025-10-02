FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app
COPY . /app


# Install Python, LibreOffice, and fonts
RUN apt-get update && \
    apt-get install -y python3 python3-pip libreoffice-core libreoffice-writer fonts-dejavu-core ttf-mscorefonts-installer && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2"]
