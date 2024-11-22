import time
import os
import sys

import linebot
import lineibot.v3.oauth
from pprint import pprint

# Defining the host is optional and defaults to https://api.line.me
configuration = linebot.v3.oauth.Configuration(
    host = "https://api.line.me"
)

outer_lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(outer_lib_path)
from commons.yaml_env import load_yaml_to_env
load_yaml_to_env("scripts/line_secret.yml")


# Enter a context with an instance of the API client
with linebot.v3.oauth.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = linebot.v3.oauth.ChannelAccessToken(api_client)
    access_token = os.getenv("CHANNEL_ACCESS_TOKEN"), # str | A short-lived or long-lived channel access token.

    try:
        api_response = api_instance.verify_channel_token(access_token)
        print("The response of ChannelAccessToken->verify_channel_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChannelAccessToken->verify_channel_token: %s\n" % e)