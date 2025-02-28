FROM python:3.10-slim

WORKDIR /app

# تحديث النظام وتثبيت أدوات البناء وبعض المكتبات الأساسية
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
