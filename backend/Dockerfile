# Dockerfile for Django backend
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . ./

# Expose Django port
EXPOSE 8000

# Run migrations and start development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
