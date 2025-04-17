source ./scripts/init.sh
'/Users/varin/Downloads/google-cloud-sdk/bin/gcloud' config set project $PROJECT_ID

echo "GCP Project ID: $PROJECT_ID"
echo "Function Name: $FUNCTION_NAME"

'/Users/varin/Downloads/google-cloud-sdk/bin/gcloud' functions deploy $FUNCTION_NAME \
    --gen2 \
    --trigger-http \
    --region=asia-southeast1 \
    --runtime=python312 \
    --source=. \
    --entry-point=$ENTRY_POINT \
    --allow-unauthenticated \
    --env-vars-file=scripts/line_secret.yml