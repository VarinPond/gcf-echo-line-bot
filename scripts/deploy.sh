source ./deploy_script/init.sh
gcloud config set project $PROJECT_ID

echo "GCP Project ID: $PROJECT_ID"
echo "Function Name: $FUNCTION_NAME"

gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --trigger-http \
    --runtime=python312 \
    --source=. \
    --entry-point=callback \
    --allow-unauthenticated \
    --env-vars-file=deploy_script/line_secret.yml