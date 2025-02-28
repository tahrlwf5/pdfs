# Base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FONTCONFIG_PATH=/etc/fonts

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libfreetype6-dev \
    fonts-arabeyes \
    fonts-noto \
    fontconfig \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m botuser
WORKDIR /app
RUN chown botuser:botuser /app
USER botuser

# Copy requirements first for caching
COPY --chown=botuser:botuser requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=botuser:botuser . .

# Set entrypoint
CMD ["python", "bot.py"]
