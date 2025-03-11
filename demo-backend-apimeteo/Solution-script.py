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