import os
### The Weather information is currently updated two times every 12h. Reading weather forecast for "today" from BQ
#import pandas as pd
from flask import Flask
from flask import request
from google.cloud import bigquery
import re
app = Flask(__name__)


@app.route("/meteocris", methods=['GET','POST'])
def meterocrisapi():
    city_name = request.args.get('cityname')
    if city_name:
        city_name = re.sub(r'[^a-zA-Z\s]', '', city_name)
        # Or use a more specific validation if needed
    
    print(f"Meteo API - {city_name.upper()}!")    
    return get_city_weather(city_name.upper())


def get_city_weather(city_name):
   # [START query_parameters]
    client = bigquery.Client()
    #crea la sql con variables que indiquen el proyecto y dataset 
    project_id = os.environ.get("PROJECT_ID")
    dataset_id = os.environ.get("DATASET_ID")
    if project_id and dataset_id:
        sql = f"""
        SELECT  city.name,clouds,main,weather
        FROM `{project_id}.{dataset_id}.forecasting_history`
        WHERE UPPER(city.name) = @citytofind
        LIMIT 1
    """
    else:
        print("PROJECT_ID or DATASET_ID environment variables are not set. Using default values.")

    query_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("citytofind", "STRING", city_name) #,bigquery.ScalarQueryParameter("limit", "INTEGER", 100),
        ]
    )
    try:
        df = client.query(sql, job_config=query_config).to_dataframe()
        assert len(df) > 0
        json_data = df.to_json(orient='records')
        print(f"*** 1 function get_city_weather data - {json_data}!")
        return json_data
    except AssertionError:
        return "City not found", 404
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An internal error occurred =O", 500


### DEMO START
# crea una función que devuelva la temperatura de la ciudad indicada desde BigQuery
@app.route("/temperature", methods=['GET'])
def get_temperature():
    city_name = request.args.get('cityname')
    if not city_name:
        return "City name is required", 400
    city_name = re.sub(r'[^a-zA-Z\s]', '', city_name)
    client = bigquery.Client()
    project_id = os.environ.get("PROJECT_ID")
    dataset_id = os.environ.get("DATASET_ID")
    if project_id and dataset_id:
        sql = f"""
        SELECT main.temp
        FROM `{project_id}.{dataset_id}.forecasting_history`
        WHERE UPPER(city.name) = @citytofind
        LIMIT 1
    """
    else:
        print("PROJECT_ID or DATASET_ID environment variables are not set. Using default values.")
        return "Internal error", 500

    query_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("citytofind", "STRING", city_name.upper())
        ]
    )
    try:
        df = client.query(sql, job_config=query_config).to_dataframe()
        if df.empty:
            return "City not found", 404
        temperature = df['temp'].iloc[0]
        return str(temperature)
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An internal error occurred", 500



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
