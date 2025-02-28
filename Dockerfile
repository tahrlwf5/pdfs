# استخدم نسخة مخففة من بايثون
FROM python:3.10-slim

# تعيين دليل العمل داخل الحاوية
WORKDIR /app

# نسخ ملف المتطلبات وتثبيت المكتبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات التطبيق إلى الحاوية
COPY . .

# الأمر الافتراضي لتشغيل البوت (تأكد من أن اسم الملف هو bot.py أو قم بتعديل الأمر بما يناسبك)
CMD ["python", "bot.py"]
