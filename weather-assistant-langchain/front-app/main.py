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

import os
from flask import Flask, render_template, request
import json
# Using a zero-shot react agent to reply questions using custom tools created above
# - Meteo
# - Datetime
# - Location
#
# The agent gets the question as an argument (a quoted sentence).

import sys
from langchain.agents import initialize_agent
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import VertexAI 
from meteo_retriever import  Meteocris
from datetimetool import Datetime
from locationtool import Location

app = Flask(__name__)
llm = VertexAI(
            model_name='gemini-1.5-flash-002',
            max_output_tokens=256,
            temperature=0.1,
            top_p=0.8,
            top_k=40,
            verbose=True,
        )

template = '''\
        Please respond to the questions accurately and succinctly. \
        If you are unable to obtain the necessary data after seeking help, \
        indicate that you do not know.
        '''

prompt = PromptTemplate(input_variables=[], template=template)

        # debug
        # print(prompt.format())
        # Load the tool configs that are needed.
llm_weather_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=True
        )

tools = [
            Meteocris, 
            Datetime,  
            Location
        ]

        # Construct the react agent type.
agent = initialize_agent(
            tools,
            llm,
            agent="zero-shot-react-description",
            verbose=True
        )

        # DEBUG
        # https://github.com/hwchase17/langchain/issues/912#issuecomment-1426646112
        # agent.agent.llm_chain.verbose=True



@app.route("/", methods=["GET"])
def index():
    """Render the default template."""
    f = open("templates/markdown.md")
    return render_template("index.html", default=f.read())


@app.route("/weatherassitant", methods=["GET","POST"])
def render_handler():
    """Langchain agent to get City Weather Info into HTML.
    """
    if request.method == 'POST':
        body = request.get_json(silent=True)
        if not body:
            return "Error!!! Invalid JSON in chat", 400
        querytoagent = body["data"]

    if request.method == 'GET':
        querytoagent = request.args.get('message',default='weather in Madrid',type=str).upper()
        if not querytoagent: 
            return "Error rendering query to agent *******: Invalid request", 400
    try:
       
        answer = agent.run(querytoagent)
        context = {}
        context["datos"] = answer
        context["type"] = type(answer)
        print("***** data:", context["datos"])
        return context["datos"], 200 #render_template("index.html", **context)
    except Exception as err:
        return f"Error rendering page: {err}", 500

# [START cloudrun_secure_request_do]
@app.route("/getcityweather", methods=["GET","POST"])
def render_handler_original():
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

########### de uno por defecto ##############
