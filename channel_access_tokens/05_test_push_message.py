import os
import sys

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage,
)

outer_lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(outer_lib_path)
from commons.yaml_env import load_yaml_to_env

load_yaml_to_env("scripts/line_secret.yml")

configuration = Configuration(
    access_token=os.getenv("CHANNEL_ACCESS_TOKEN"),
)

# Initialize the Messaging API client once
with ApiClient(configuration) as api_client:
    line_bot_api = MessagingApi(api_client)
    line_bot_api.push_message(
        PushMessageRequest(to=os.getenv("YOUR_USER_ID"), messages=[TextMessage(text="PUSH! YAY! your token is work!")])
    )
