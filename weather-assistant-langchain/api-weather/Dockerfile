# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True

# Copy application dependency manifests to the container image.
# Copying this separately prevents re-running pip install on every code change.
COPY requirements.txt ./

# Install production dependencies.
RUN pip install -r requirements.txt

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./ 
## create repo: gcloud artifacts repositories create demos-docker-repo --repository-format=docker  --location=eu-west1 --description="Docker repository"
## build dockerfile: gcloud builds submit --region=us-west2 --tag europe-west1-docker.pkg.dev/yogaproject-1508/demos-docker-repo/api-meteocris:1
## gcloud iam service-accounts create api-weather-identity
## gcloud run deploy api-weather --image europe-west1-docker.pkg.dev/yogaproject-1508/demos-docker-repo/api-meteocris:1 --service-account api-weather-identity --no-allow-unauthenticated
## https://api-weather-gzipihuhoq-ew.a.run.app
##curl -X GET -v -LS -H "Authorization: Bearer $(gcloud auth print-identity-token)" https://api-weather-gzipihuhoq-ew.a.run.app/meteocris?cityname=AREQUIPA

# Run the web service on container startup.
# Use gunicorn webserver with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app

