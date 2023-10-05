import os
### The Weather information is currently updated two times every 12h. Reading weather forecast for "today" from GCS
import pandas as pd
from flask import Flask
from flask import request
app = Flask(__name__)


@app.route("/meteocris", methods=['GET','POST'])
def meterocrisapi():
    city_name = request.args.get('cityname')
    print(f"Meteocris API - {city_name.upper()}!")    
    return get_city_weather(city_name.upper()) # f"Meteocris - {city_name}!"
# llamar a la funcion con los parametros de la ciudad. Tiene que haber una funcion que cargue los datos del bucket y que los guarde para consultar en datastore o BQ para leer 


### df_weatherinfo = get_file_from_gcs("","weather_14.json","weather_14.json")
def get_city_weather(city_name):
   # [START query_parameters]
    from google.cloud import bigquery
    client = bigquery.Client()
    sql = """
        SELECT  city.name,clouds,main,weather
        FROM `yogaproject-1508.data_weather.forecasting_history`
        WHERE UPPER(city.name) = @citytofind
        LIMIT 1
    """
    query_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("citytofind", "STRING", city_name) #,bigquery.ScalarQueryParameter("limit", "INTEGER", 100),
        ]
    )
    df = client.query(sql, job_config=query_config).to_dataframe()
    print(f"*** 0 $$$$ get_city_weather from API - {city_name}! and df len: {len(df)}") 
    # [END query_parameters]
    assert len(df) > 0
    json_data = df.to_json(orient='records')
    print(f"*** 1 $$$$ get_city_weather data - {json_data}!") 
    return json_data

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
