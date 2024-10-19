# gcf-echo-line-bot

<img src="assets/title.png"><img>

---
*Author*: Punsiri Boonyakiat </br>
*Medium*: -

---

### STEP :  

Simple Line Chatbot Demo with Python SDK and Google Cloud Run Function

1. Log-in to your GCP Project using gcloud CLI
```
gcloud auth login
```

2. Set up the init.sh by copy from `init.sh.example` and replace with you GCP Project ID
```
export PROJECT_ID=XXXXX
export FUNCTION_NAME=line_webhook_handler
export ENTRY_POINT=callback
```

3. Set up your Chatbot Credential file `line_secret.yml.example` by copy to line_secret.yml and replace with you LINE Chatbot credentails
```
YOUR_CHANNEL_SECRET: XXXXX
YOUR_CHANNEL_ACCESS_TOKEN: XXXXX
```

4. Install Python Libraly for local run 
``` 
pip install -r requirements.txt 
```

To test in local with functions-framework
```
./scripts/local_run.sh
```

5. To Deploy run the deploy.sh

```
./scripts/deploy.sh
```