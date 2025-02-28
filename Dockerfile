FROM python:3.10-slim

WORKDIR /app

# تثبيت الأدوات اللازمة
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    ttf-mscorefonts-installer \
    && rm -rf /var/lib/apt/lists/*

# نسخ الملفات إلى الحاوية
COPY requirements.txt .
COPY arial.ttf /app/  # نسخ الخط العربي إلى الحاوية
COPY bot.py /app/

# تثبيت المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل البوت
CMD ["python", "bot.py"]
