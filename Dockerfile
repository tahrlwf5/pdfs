# استخدم صورة بايثون الرسمية كصورة أساسية
FROM python:3.9-slim-buster

# قم بتعيين دليل العمل داخل الحاوية
WORKDIR /app

# انسخ ملفات requirements.txt و .env إلى دليل العمل
COPY requirements.txt .env ./

# قم بتثبيت المكتبات المطلوبة
RUN pip install --no-cache-dir -r requirements.txt

# انسخ باقي ملفات التطبيق إلى دليل العمل
COPY . .

# قم بتعيين متغير البيئة TELEGRAM_BOT_TOKEN
ENV TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}

# قم بتشغيل التطبيق
CMD ["python", "your_bot_script.py"]
