FROM python:3.12-slim

# Set environment variable to avoid buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install necessary system dependencies including Netcat
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /django

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project files
COPY . .

# Collect static files for WhiteNoise to serve in production
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Run the Django production server, binding to all interfaces for Docker
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "hanapbuhai.wsgi:application"]