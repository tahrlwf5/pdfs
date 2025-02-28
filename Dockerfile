# استخدم صورة بايثون خفيفة
FROM python:3.10-slim

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# تحديث النظام وتثبيت الخطوط المطلوبة
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# نسخ الملفات إلى الحاوية
COPY requirements.txt . 
COPY bot.py . 
COPY arial.ttf /app/ 

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل البوت عند بدء التشغيل
CMD ["python", "bot.py"]
