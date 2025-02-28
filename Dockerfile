FROM python:3.10-slim

WORKDIR /app

# نسخ ملف المتطلبات وتثبيت المكتبات
COPY requirements.txt .

# تحديث pip وتثبيت المكتبات من ملف المتطلبات
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات التطبيق إلى الحاوية
COPY . .

# الأمر الافتراضي لتشغيل التطبيق
CMD ["python", "bot.py"]
