import os
### The Weather information is currently updated two times every 12h. Reading weather forecast for "today" from BQ
import pandas as pd
from flask import Flask
from flask import request
app = Flask(__name__)


@app.route("/meteocris", methods=['GET','POST'])
def meterocrisapi():
    city_name = request.args.get('cityname')
    print(f"Meteo API - {city_name.upper()}!")    
    return get_city_weather(city_name.upper()) 

def get_city_weather(city_name):
   # [START query_parameters]
    from google.cloud import bigquery
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
            bigquery.ScalarQueryParameter("citytofind", "STRING", city_name) #,bigquery.ScalarQueryParameter("limit", "INTEGER", 100),
        ]
    )
    df = client.query(sql, job_config=query_config).to_dataframe()
    print(f"*** 0 function get_city_weather from API - {city_name}! and df len: {len(df)}") 
    # [END query_parameters]
    assert len(df) > 0
    json_data = df.to_json(orient='records')
    print(f"*** 1 function get_city_weather data - {json_data}!") 
    return json_data


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
