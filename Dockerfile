FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FONTCONFIG_PATH=/etc/fonts

# تثبيت التبعيات النظامية الأساسية
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    libraqm-dev \
    fonts-arabeyes \
    fonts-noto \
    fontconfig \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مستخدم غير root
RUN useradd -m botuser
WORKDIR /app
RUN chown botuser:botuser /app
USER botuser

# نسخ المتطلبات أولاً
COPY --chown=botuser:botuser requirements.txt .

# تثبيت بايثون dependencies مع إصلاح الإصدارات
RUN pip install --no-cache-dir pip==23.3.1 \
    && pip install --no-cache-dir -r requirements.txt --use-pep517

# نسخ باقي الملفات
COPY --chown=botuser:botuser . .

CMD ["python", "bot.py"]
