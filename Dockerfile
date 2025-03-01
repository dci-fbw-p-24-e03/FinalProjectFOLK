# Add "whitenoise.middleware.WhiteNoiseMiddleware" to middleware[] in settings.py - whitenoise is used for
# running gunicorn and using static files in particular CSS files!
# Add STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles") to settings.py  # Create staticfiles for deployment
# Add '0.0.0.0' to allowed hosts in settings.py

# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Update installed apps:

RUN apt update && apt install -y libpq-dev

# Copy the Django project
COPY . .

# Run migrations and collect static files; static files need to be collected for running gunicorn
# RUN python manage.py makemigrations
# RUN python manage.py migrate
RUN python manage.py collectstatic --noinput


# Expose the port Gunicorn will run on
EXPOSE 8000

# Command to start Gunicorn server running AI_quiz
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "AI_quiz.wsgi:application"]
