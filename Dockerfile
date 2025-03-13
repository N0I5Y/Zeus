FROM python:3.9-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend project
COPY . .

# Set the correct Django settings module
ENV DJANGO_SETTINGS_MODULE=resume_project.settings

# Ensure logs directory exists
RUN mkdir -p /app/logs

# Run the application with auto-reload
CMD ["watchfiles", "python manage.py runserver 0.0.0.0:8000"]
