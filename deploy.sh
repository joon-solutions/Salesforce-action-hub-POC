#!/bin/bash
# Usage: bash deploy.sh

set -a
source .env
set +a

# Set Environment Variables
ACTION_LABEL="Salesforce Campaign Creator POC"
ACTION_NAME="salesforce-campaign-creator-poc"
REGION="asia-southeast1"
PROJECT="joon-sandbox"
# todo: change this to the service account email
SERVICE_ACCOUNT_EMAIL=vertex-ai-cloud-function-demo@${PROJECT}.iam.gserviceaccount.com
CLIENT_ID=${SALESFORCE_CLIENT_ID}
CLIENT_SECRET=${SALESFORCE_CLIENT_SECRET}
USERNAME=${SALESFORCE_USERNAME}
PASSWORD=${SALESFORCE_PASSWORD}


# Create .env.yaml
printf "ACTION_LABEL: ${ACTION_LABEL}\nACTION_NAME: ${ACTION_NAME}\nREGION: ${REGION}\nPROJECT: ${PROJECT}" > .env.yaml

# Create Secret Manager for Looker Auth Token
# printf ${LOOKER_AUTH_TOKEN} | gcloud secrets create LOOKER_AUTH_TOKEN --data-file=- --replication-policy=user-managed --locations=${REGION} --project=${PROJECT}
# printf ${CLIENT_ID} | gcloud secrets create CLIENT_ID --data-file=- --replication-policy=user-managed --locations=${REGION} --project=${PROJECT}
# printf ${CLIENT_SECRET} | gcloud secrets create CLIENT_SECRET --data-file=- --replication-policy=user-managed --locations=${REGION} --project=${PROJECT}
# printf ${USERNAME} | gcloud secrets create USERNAME --data-file=- --replication-policy=user-managed --locations=${REGION} --project=${PROJECT}
# printf ${PASSWORD} | gcloud secrets create PASSWORD --data-file=- --replication-policy=user-managed --locations=${REGION} --project=${PROJECT}

# deploy cloud functions
gcloud functions deploy salesforce-campaign-creator-poc-list --entry-point salesforce_action_list --env-vars-file .env.yaml --trigger-http --runtime=python311 --allow-unauthenticated --no-gen2 --memory=1024MB --timeout=540s --region=${REGION} --project=${PROJECT} --service-account ${SERVICE_ACCOUNT_EMAIL} --set-secrets 'LOOKER_AUTH_TOKEN=LOOKER_AUTH_TOKEN:latest'
gcloud functions deploy salesforce-campaign-creator-poc-form --entry-point campaign_form --env-vars-file .env.yaml --trigger-http --runtime=python311 --allow-unauthenticated --no-gen2 --memory=1024MB --timeout=540s --region=${REGION} --project=${PROJECT} --service-account ${SERVICE_ACCOUNT_EMAIL} --set-secrets 'LOOKER_AUTH_TOKEN=LOOKER_AUTH_TOKEN:latest'
gcloud functions deploy salesforce-campaign-creator-poc-execute --entry-point campaign_execute --env-vars-file .env.yaml --trigger-http --runtime=python311 --allow-unauthenticated --no-gen2 --memory=8192MB --timeout=540s --region=${REGION} --project=${PROJECT} --service-account ${SERVICE_ACCOUNT_EMAIL} --set-secrets 'LOOKER_AUTH_TOKEN=LOOKER_AUTH_TOKEN:latest,SALESFORCE_CLIENT_ID=SALESFORCE_CLIENT_ID:latest,SALESFORCE_CLIENT_SECRET=SALESFORCE_CLIENT_SECRET:latest,SALESFORCE_USERNAME=SALESFORCE_USERNAME:latest,SALESFORCE_PASSWORD=SALESFORCE_PASSWORD:latest'
gcloud functions deploy salesforce-task-creator-poc-form --entry-point task_form --env-vars-file .env.yaml --trigger-http --runtime=python311 --allow-unauthenticated --no-gen2 --memory=1024MB --timeout=540s --region=${REGION} --project=${PROJECT} --service-account ${SERVICE_ACCOUNT_EMAIL} --set-secrets 'LOOKER_AUTH_TOKEN=LOOKER_AUTH_TOKEN:latest'
gcloud functions deploy salesforce-task-creator-poc-execute --entry-point task_execute --env-vars-file .env.yaml --trigger-http --runtime=python311 --allow-unauthenticated --no-gen2 --memory=8192MB --timeout=540s --region=${REGION} --project=${PROJECT} --service-account ${SERVICE_ACCOUNT_EMAIL} --set-secrets 'LOOKER_AUTH_TOKEN=LOOKER_AUTH_TOKEN:latest,SALESFORCE_CLIENT_ID=SALESFORCE_CLIENT_ID:latest,SALESFORCE_CLIENT_SECRET=SALESFORCE_CLIENT_SECRET:latest,SALESFORCE_USERNAME=SALESFORCE_USERNAME:latest,SALESFORCE_PASSWORD=SALESFORCE_PASSWORD:latest'
gcloud functions deploy salesforce-question-creator-poc-form --entry-point question_form --env-vars-file .env.yaml --trigger-http --runtime=python311 --allow-unauthenticated --no-gen2 --memory=1024MB --timeout=540s --region=${REGION} --project=${PROJECT} --service-account ${SERVICE_ACCOUNT_EMAIL} --set-secrets 'LOOKER_AUTH_TOKEN=LOOKER_AUTH_TOKEN:latest'
gcloud functions deploy salesforce-question-creator-poc-execute --entry-point question_execute --env-vars-file .env.yaml --trigger-http --runtime=python311 --allow-unauthenticated --no-gen2 --memory=8192MB --timeout=540s --region=${REGION} --project=${PROJECT} --service-account ${SERVICE_ACCOUNT_EMAIL} --set-secrets 'LOOKER_AUTH_TOKEN=LOOKER_AUTH_TOKEN:latest,SALESFORCE_CLIENT_ID=SALESFORCE_CLIENT_ID:latest,SALESFORCE_CLIENT_SECRET=SALESFORCE_CLIENT_SECRET:latest,SALESFORCE_USERNAME=SALESFORCE_USERNAME:latest,SALESFORCE_PASSWORD=SALESFORCE_PASSWORD:latest'
gcloud functions deploy salesforce-post-creator-poc-form --entry-point post_form --env-vars-file .env.yaml --trigger-http --runtime=python311 --allow-unauthenticated --no-gen2 --memory=1024MB --timeout=540s --region=${REGION} --project=${PROJECT} --service-account ${SERVICE_ACCOUNT_EMAIL} --set-secrets 'LOOKER_AUTH_TOKEN=LOOKER_AUTH_TOKEN:latest'
gcloud functions deploy salesforce-post-creator-poc-execute --entry-point post_execute --env-vars-file .env.yaml --trigger-http --runtime=python311 --allow-unauthenticated --no-gen2 --memory=8192MB --timeout=540s --region=${REGION} --project=${PROJECT} --service-account ${SERVICE_ACCOUNT_EMAIL} --set-secrets 'LOOKER_AUTH_TOKEN=LOOKER_AUTH_TOKEN:latest,SALESFORCE_CLIENT_ID=SALESFORCE_CLIENT_ID:latest,SALESFORCE_CLIENT_SECRET=SALESFORCE_CLIENT_SECRET:latest,SALESFORCE_USERNAME=SALESFORCE_USERNAME:latest,SALESFORCE_PASSWORD=SALESFORCE_PASSWORD:latest'
gcloud functions deploy salesforce-poll-creator-poc-form --entry-point poll_form --env-vars-file .env.yaml --trigger-http --runtime=python311 --allow-unauthenticated --no-gen2 --memory=1024MB --timeout=540s --region=${REGION} --project=${PROJECT} --service-account ${SERVICE_ACCOUNT_EMAIL} --set-secrets 'LOOKER_AUTH_TOKEN=LOOKER_AUTH_TOKEN:latest'
gcloud functions deploy salesforce-poll-creator-poc-execute --entry-point poll_execute --env-vars-file .env.yaml --trigger-http --runtime=python311 --allow-unauthenticated --no-gen2 --memory=8192MB --timeout=540s --region=${REGION} --project=${PROJECT} --service-account ${SERVICE_ACCOUNT_EMAIL} --set-secrets 'LOOKER_AUTH_TOKEN=LOOKER_AUTH_TOKEN:latest,SALESFORCE_CLIENT_ID=SALESFORCE_CLIENT_ID:latest,SALESFORCE_CLIENT_SECRET=SALESFORCE_CLIENT_SECRET:latest,SALESFORCE_USERNAME=SALESFORCE_USERNAME:latest,SALESFORCE_PASSWORD=SALESFORCE_PASSWORD:latest'