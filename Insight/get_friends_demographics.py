import sys
import os
import linebot.v3.insight
from linebot.v3.insight.models.get_friends_demographics_response import (
    GetFriendsDemographicsResponse,
)
from linebot.v3.insight.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.line.me
# See configuration.py for a list of all supported configuration parameters.
configuration = linebot.v3.insight.Configuration(host="https://api.line.me")

outer_lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(outer_lib_path)
from commons.yaml_env import load_yaml_to_env

load_yaml_to_env("scripts/line_secret.yml")

configuration = linebot.v3.insight.Configuration(
    access_token=os.environ["CHANNEL_ACCESS_TOKEN"]
)

# Enter a context with an instance of the API client
with linebot.v3.insight.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = linebot.v3.insight.Insight(api_client)

    try:
        api_response = api_instance.get_friends_demographics()
        print("The response of Insight->get_friends_demographics:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling Insight->get_friends_demographics: %s\n" % e)
