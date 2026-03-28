FROM python:3.12-slim

# Prevent python from writing .pyc files and enables unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \`
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app will run on
EXPOSE 8000

# - bind 0.0.0.0 so it's reachable outside the container
# - set workers; a common starting point is (2 * CPU) + 1
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app.wsgi:app", "--workers", "2", "--threads", "4", "--timeout", "60"]