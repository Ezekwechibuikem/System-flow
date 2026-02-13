FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Work in the system flow directory
WORKDIR /system-flow

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# install python dependencies
COPY requirements.txt /system-flow/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project files
COPY . /system-flow/

# Expose port 8000
EXPOSE 8000

# Run development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]