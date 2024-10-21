source ./scripts/init.sh
gcloud config set project $PROJECT_ID

echo "Local Deploy for Testing"
echo "GCP Project ID: $PROJECT_ID"
echo "Function Name: $FUNCTION_NAME"

 gcloud alpha functions local deploy $FUNCTION_NAME \
    --entry-point=$ENTRY_POINT \
    --runtime=python312\
    --gen2 \
    --trigger-http \
    --source=. \
    --env-vars-file=scripts/line_secret.yml