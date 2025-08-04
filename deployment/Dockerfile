FROM python:3.12.3-slim
# Set work directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    nano \
    build-essential \
    libffi-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --no-cache-dir pipenv
# Copy Pipenv files
COPY ["Pipfile", "Pipfile.lock", "./"]
# Install Python dependencies
RUN pipenv install --deploy --ignore-pipfile
# Copy source code
COPY ["predict.py", "app.py", "./"]
# Expose the port the app runs on
EXPOSE 8000
# Run the app (fix module name if needed)
CMD ["pipenv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]