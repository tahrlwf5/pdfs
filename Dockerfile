# استخدام صورة بايثون رسمية كصورة أساسية
FROM python:3.9-slim

# تعيين دليل العمل
WORKDIR /app

# نسخ الملفات المطلوبة
COPY requirements.txt .
COPY bot.py .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملف .env (اختياري، يمكن تمرير المتغيرات البيئية من خلال Railway)
COPY .env .

# تعيين المنفذ الذي سيتم استخدامه
ENV PORT 8443

# تشغيل البوت
CMD ["python", "bot.py"]
