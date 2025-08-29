FROM python:3.13-slim

# Tizim paketlarini o‘rnatamiz
RUN apt-get update && apt-get install -y \
libreoffice \
fonts-dejavu-core \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/* \

# Muhit o‘zgaruvchilar
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

# Kutubxonalarni alohida qatorda o‘rnatish (cache saqlash uchun)
COPY r.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r r.txt

# Loyiha fayllarini nusxalash
COPY . .

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
