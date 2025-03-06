# https://hub.docker.com/_/python
FROM python:3.11-slim-bookworm

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
# Copy application dependency manifests to the container image.
# Copying this separately prevents re-running pip install on every code change.
COPY requirements.txt ./

# Install production dependencies.
RUN pip install -r requirements.txt

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./ 

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app

