#!/usr/bin/env bash

# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

export PROJECT_ID=$(gcloud config get-value project)
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
export PROJECT_NAME=$(gcloud projects describe $PROJECT_ID --format='value(name)')
export REGION=europe-west1
export IMAGE_NAME=api-meteo-demo
export REPO_NAME=demos-docker-repo
export DATASET_ID=data_weather

gcloud config set project $PROJECT_ID

gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  clouddeploy.googleapis.com \
  artifactregistry.googleapis.com

#gcloud artifacts repositories create containers-repo \
  --repository-format=docker \
  --location=${REGION} \
  --description="Containers repository"

sed -e "s/_PROJECT_ID/$PROJECT_ID/g" cloud-deploy.yaml > cloud-deploy-temp.yaml
sed -e "s/_IMAGE_NAME/${IMAGE_NAME}/g" deploy-dev.yaml > deploy-dev-temp.yaml
sed -e "s/_IMAGE_NAME/${IMAGE_NAME}/g" deploy-pre.yaml > deploy-pre-temp.yaml
sed -e "s/_IMAGE_NAME/${IMAGE_NAME}/g" deploy-pro.yaml > deploy-pro-temp.yaml

# create deploy first time
gcloud deploy apply \
  --file=cloud-deploy-temp.yaml \
  --region=${REGION} \
  --project=${PROJECT_ID}

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
    --role=roles/clouddeploy.operator

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
    --role=roles/iam.serviceAccountUser

# cd ..

export RELEASE_TIMESTAMP=$(date '+%Y%m%d-%H%M%S')

gcloud builds submit \
  --config ./cloudbuild.yaml \
  --substitutions=_REGION=${REGION},_RELEASE_TIMESTAMP=${RELEASE_TIMESTAMP},_IMAGE_NAME=${IMAGE_NAME},_REPO_NAME=${REPO_NAME},_DATASET_ID=${DATASET_ID}

gcloud beta deploy releases promote \
    --release="release-${RELEASE_TIMESTAMP}" \
    --delivery-pipeline=cloud-run-pipeline \
    --region=${REGION} \
    --to-target=pre-env \
    --quiet