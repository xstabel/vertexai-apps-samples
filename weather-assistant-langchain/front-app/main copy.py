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
'''
import os
from flask import Flask, render_template, request

import json

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    """Render the default template."""
    f = open("templates/markdown.md")
    return render_template("index.html", default=f.read())


# [START cloudrun_secure_request_do]
@app.route("/getcityweather", methods=["GET","POST"])
def render_handler():
    """Get City Weather Info into HTML.
    """
    multi_dict = request.args
    for key in multi_dict:
        print(f"On getcityweather - { multi_dict.get(key)}")
        print(f"On getcityweather - { multi_dict.getlist(key)}")

    cityname = request.args.get('cityname',default='Madrid',type=str).upper()
    print(f"On getcityweather - {cityname}!")    
 
    if not cityname:
        return "Error rendering cityname*******: Invalid request", 400
    try:
        city_weather = controller.new_request(cityname)
     #   return city_weather, 200
        print(f"Json city weather: {city_weather}")  
        json_data = json.loads(city_weather)        
        context = {}
        #for key, value in json_data.items():
        #    context[key] = value
        context["datos"] = json.dumps(json_data)
        context["type"] = type(json_data)
        print("json_data:", json.dumps(json_data))
        return context["datos"], 200 #render_template("index.html", **context)

    except Exception as err:
        return f"Error rendering markdown: {err}", 500

# [END cloudrun_secure_request_do]


if __name__ == "__main__":
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="127.0.0.1", port=PORT, debug=True)

########### este funciona ##############
'''