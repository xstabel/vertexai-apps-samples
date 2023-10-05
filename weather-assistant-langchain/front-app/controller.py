# Copyright 2020 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START cloudrun_secure_request]
import os
import urllib
import json
import google.auth.transport.requests
import google.oauth2.id_token


def new_request(data):
    """Creates a new HTTP request with IAM ID Token credential.
    This token is automatically handled by private Cloud Run and Cloud Functions.
    Args:
        data: data for the authenticated request
    Returns:
        The response from the HTTP request
    """
    url = os.environ.get("API_WEATHER_URL")
    if not url:
        raise Exception("API_WEATHER_URL missing")

    req = urllib.request.Request( url+'?cityname='+data )
    auth_req = google.auth.transport.requests.Request()
    target_audience = url

    id_token = google.oauth2.id_token.fetch_id_token(auth_req, target_audience)
    req.add_header("Authorization", f"Bearer {id_token}")
    print(f"***controller.py  1 new_request - {data} - Bearer - {id_token}!") 
    response = urllib.request.urlopen(req)
    jsonloads= json.loads(response.read())
    print(f"***controller.py  2 After calling API in new_request controller.py jsonloads - {jsonloads} !") 
    print(f"***controller.py  3 in new_request controller.py response.read - {response.read()} !") 
    jsondumps=json.dumps(jsonloads)
    print(f"***controller.py  4 in new_request controller.py response - {jsondumps} !") 
    dataweather = {}
    # default data
    dataweather['city'] = data
    dataweather['weather'] = jsondumps
    print(f"***controller.py 5 in new_request controller.py data - {dataweather} !") 
    return dataweather # response.read()

# [END cloudrun_secure_request]
