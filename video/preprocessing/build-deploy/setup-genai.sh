export PROJECT_ID=$(gcloud config get-value project)
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
export PROJECT_NAME=$(gcloud projects describe $PROJECT_ID --format='value(name)')
export REGION=europe-west1
export IMAGE_NAME=video-demogenai-job
export REPO_NAME=demos-docker-repo
export PASS_DB=P4w0rd@@
export DBINSTANCE=postgresdemovideoai
export DBNAME=dbvideogenai
export JOBNAME=videoai-job
export PIPELINE_NAME=videogenai-pipeline
export VIDEO_GCS_URI="gsc_video_demogenai"  

echo 'PROJECT_ID="'${PROJECT_ID}'"
REGION="'${REGION}'"
FPS_GCS_URI="gsc_fps_gcs_video_demogenai"
VIDEO_TRANSCRIPT_ANNOTATIONS_GCS="gsc_video_transcript_annotationsvideo_demogenai"
SNIPPETS_GCS_URI="gsc_snippets_video_demogenai"
VIDEO_GCS_URI="gsc_video_demogenai"  
PICKLE_FILE_NAME="emb2.pkl"  
LINUX=False
INSTANCE_NAME="postgresdemovideoai"
DATABASE_USER="emb-admin"
DATABASE_NAME="dbvideogenai"' > ../preprocessing/utils/variables.py 

echo DATABASE_PASSWORD="'${PASS_DB}'" > ../preprocessing/utils/credentials.py

gcloud config set project $PROJECT_ID
gsutil mb -l ${REGION}  gs://gsc_video_demogenai
gsutil mb -l ${REGION}  gs://gsc_video_transcript_annotationsvideo_demogenai
gsutil mb -l ${REGION}  gs://gsc_fps_gcs_video_demogenai
gsutil mb -l ${REGION}  gs://gsc_snippets_video_demogenai

# Database 

gcloud sql instances create ${DBINSTANCE} --database-version=POSTGRES_15 --region=${REGION} --cpu=1 --memory=4GB --root-password=${PASS_DB}
gcloud sql databases create ${DBNAME} --instance=${DBINSTANCE}

# Create and Deploy preprocessing job.

sed -e "s/_PROJECT_ID/$PROJECT_ID/g" cloud-deploy.yaml > cloud-deploy-temp1.yaml
sed -e "s/_PIPELINE_NAME/$PIPELINE_NAME/g" cloud-deploy-temp1.yaml > cloud-deploy-temp.yaml
rm cloud-deploy-temp1.yaml
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


#cd ../preprocessing


#gcloud builds submit --pack ^--^image=gcr.io/{vtxdemos}/preprocess--env=GOOGLE_PYTHON_VERSION="3.10.0"
#gcloud run deploy ${JOBNAME} --cpu 8 --memory 32Gi --timeout 900 --image  {gcr.io/vtxdemos/preprocess} --allow-unauthenticated

export RELEASE_TIMESTAMP=$(date '+%Y%m%d-%H%M%S')

# gcloud builds submit ../preprocessing \
#  --config cloudbuild.yaml \
#  --substitutions=_REGION=${REGION},_IMAGE_NAME=${IMAGE_NAME},_REPO_NAME=${REPO_NAME}

export SKAFFOLD_DIR="./build-deploy"
gcloud builds submit .. \
  --config cloudbuild2.yaml \
  --substitutions=_REGION=${REGION},_RELEASE_TIMESTAMP=${RELEASE_TIMESTAMP},_IMAGE_NAME=${IMAGE_NAME},_REPO_NAME=${REPO_NAME},_PIPELINE_NAME=${PIPELINE_NAME},_SKAFFOLD_DIR=${SKAFFOLD_DIR}
  
  ,_SKAFFOLD_FILE=${SKAFFOLD_FILE}


export SKAFFOLD_FILE="./skaffold.yaml"
gcloud builds submit ../preprocessing \
  --config cloudbuild.yaml \
  --substitutions=_REGION=${REGION},_RELEASE_TIMESTAMP=${RELEASE_TIMESTAMP},_IMAGE_NAME=${IMAGE_NAME},_REPO_NAME=${REPO_NAME},_PIPELINE_NAME=${PIPELINE_NAME},_SKAFFOLD_FILE=${SKAFFOLD_FILE}


#######################################
##########  To promote to  PRE and PROD
gcloud beta deploy releases promote \
    --release="release-${RELEASE_TIMESTAMP}" \
    --delivery-pipeline=cloud-run-pipeline \
    --region=${REGION} \
    --to-target=pre-env \
    --quiet


#### Create a Trigger Function and Workflow
export CLOUDRUN_VIDEOPREP=${IMAGE_NAME}-dev

gcloud eventarc triggers create triggerforvideopreprocess --destination-run-service=${CLOUDRUN_VIDEOPREP} \
 --destination-run-region=${REGION} --event-filters="type=google.cloud.storage.object.v1.finalized"  --event-filters="bucket=${VIDEO_GCS_URI}"  \
 --service-account=93433691361-compute@developer.gserviceaccount.com --location=${REGION} 

 gcloud workflows deploy workflowforvideopreprocess --source=../event_workflow.yaml --location=${REGION} 


## Component 2: Front End

cd ../front-end
gcloud builds submit --pack ^--^image=gcr.io/{vtxdemos}/frontend--env=GOOGLE_PYTHON_VERSION="3.10.0"

gcloud run deploy {video-front} --image  {gcr.io/vtxdemos/frontend} --allow-unauthenticated