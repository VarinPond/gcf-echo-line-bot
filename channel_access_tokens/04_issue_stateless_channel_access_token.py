import sys
import os
import linebot.v3.oauth
from pprint import pprint

# Defining the host is optional and defaults to https://api.line.me
# See configuration.py for a list of all supported configuration parameters.
configuration = linebot.v3.oauth.Configuration(host="https://api.line.me")

outer_lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(outer_lib_path)
from commons.yaml_env import load_yaml_to_env
load_yaml_to_env("scripts/line_secret.yml")

# Enter a context with an instance of the API client
with linebot.v3.oauth.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = linebot.v3.oauth.ChannelAccessToken(api_client)
    grant_type = "client_credentials"  # str | `client_credentials`
    client_assertion_type = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"  # str | URL-encoded value of `urn:ietf:params:oauth:client-assertion-type:jwt-bearer`
    client_assertion = os.getenv("JWT")  # str | A JSON Web Token ที่เราเก็บเอาไว้
    client_id = os.getenv("CHANNEL_ID")  # str | Channel ID.
    client_secret = os.getenv("CHANNEL_SECRET")  # str | Channel secret.

    try:
        api_response = api_instance.issue_stateless_channel_token(
            grant_type,
            client_assertion_type,
            client_assertion,
            client_id,
            client_secret,
        )
        print("The response of ChannelAccessToken->issue_stateless_channel_token:\n")
        pprint(api_response)
    except Exception as e:
        print(
            "Exception when calling ChannelAccessToken->issue_stateless_channel_token: %s\n"
            % e
        )
