FROM python:3.13-slim

# Tizim paketlarini o‘rnatamiz
RUN apt-get update && apt-get install -y \
    libreoffice \
    fonts-dejavu-core \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Muhit o‘zgaruvchilar
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

# Kutubxonalarni o‘rnatamiz
COPY r.txt .
RUN pip install --no-cache-dir -r r.txt

# Loyiha fayllarini image ichiga nusxalaymiz
COPY . /usr/src/app

# Botni ishga tushirish
CMD ["python", "manage.py", "bot"]