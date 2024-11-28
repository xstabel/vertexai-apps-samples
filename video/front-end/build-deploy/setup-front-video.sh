export PROJECT_ID=$(gcloud config get-value project)
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
export PROJECT_NAME=$(gcloud projects describe $PROJECT_ID --format='value(name)')
export REGION=europe-west1
export IMAGE_NAME=video-demogenai-front
export REPO_NAME=demos-docker-repo
export PASS_DB=P4w0rd@@
export DBINSTANCE=postgresdemovideoai
export DBNAME=dbvideogenai
export PIPELINE_NAME=videogenai-pipeline-front-end
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
DATABASE_NAME="dbvideogenai"' > ../front-end/utils/variables.py 

echo DATABASE_PASSWORD="'${PASS_DB}'" > ../front-end/utils/credentials.py

# Create and Deploy front-end service.

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


export RELEASE_TIMESTAMP=$(date '+%Y%m%d-%H%M%S')

export SKAFFOLD_DIR="./build-deploy"
gcloud builds submit .. \
  --config cloudbuild.yaml \
  --substitutions=_REGION=${REGION},_RELEASE_TIMESTAMP=${RELEASE_TIMESTAMP},_IMAGE_NAME=${IMAGE_NAME},_REPO_NAME=${REPO_NAME},_PIPELINE_NAME=${PIPELINE_NAME},_SKAFFOLD_DIR=${SKAFFOLD_DIR}


#######################################
##########  To promote to  PRE and PROD
gcloud beta deploy releases promote \
    --release="release-${RELEASE_TIMESTAMP}" \
    --delivery-pipeline=cloud-run-pipeline \
    --region=${REGION} \
    --to-target=pre-env \
    --quiet


## Component 2: Front End

cd ../front-end
gcloud builds submit --pack ^--^image=gcr.io/{vtxdemos}/frontend--env=GOOGLE_PYTHON_VERSION="3.10.0"

gcloud run deploy {video-front} --image  {gcr.io/vtxdemos/frontend} --allow-unauthenticated