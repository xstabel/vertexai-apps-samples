# This langchain tool retrieves weather forecasts data
# It's a mock function with real data from openweather. However the data is from a few years ago

import json
from typing import List
from langchain.agents import Tool 
import controller


def meteocris_data_retriever(
    location: str = None,
    period: str = None,
    specific_variables: List[str] = []
) -> str:
    '''
    This is a mockup function, returning a fixed text template. A custom python function that takes
    a list of arguments and returns a JSON (or in general any data structure).

    The function could wrap an external API returning realtime weather forecast. Given a location and a
    time period, the function returns weather forecast as a data structure in a common JSON format.

    parameters:
        location: as text. Default value is 'Madrid, Spain'
        period: time period. Default value is 'today'
        specific_variables: list of specific/required attributes, e.g ["temperature", "humidity"]

    returns:
        weather foreast description as a JSON. E.g.
        {..."main":{"temp":286.93,"pressure":1026,"humidity":47,"temp_min":285.15,"temp_max":288.15}..."weather":[{"id":800,"main":"Clear","description":"Sky is Clear","icon":"01d"}] ...}
    '''
    data = {}
    # default data
    data['forecast'] = 'sunny all day'
    data['temperature'] = '202 degrees Fahrenheit'

    # ERROR/EXCEPTION: DISAMBIGUATION REQUIRED
    # the tool can't elaborate because it doesn't has the mandatory variable 'location',
    # so the returned content is an hardcoded error sentence (not a JSON), requiring a user DISAMBIGUATION.
    if not location or ('location' in location):
        return 'The location is not specified. Where are you?'

    # Warning! If the variable period is not defined the default value is assigned
    if not period or period == 'period':
        data['period'] = 'now'

    # if required variable names are not included in the data section,
    # the attribute is added to the dictionary with value I don't know.
    for variable_name in specific_variables:
        if variable_name not in data.keys():
            data[variable_name] = 'data not available'
    try:
     ####response_as_json = get_city_weather(location)
     ### this should call the API to get weather forecast data VERSION-2-METEOCRIS
        print(f"$$$$$$$$ 0 ****** Before calling the secured API with location: {location.upper()}")  
        res = controller.new_request(location)
        print(f"$$$$$$$$ 1 ****** After calling the secured API with response: {res}")  
        '''
        response_as_json = json.loads(res)
        print(f"$$$$$$$$ 2 ****** After calling the secured API with jsonloads: {response_as_json}" )  
        json_data =json.dumps(response_as_json)        
        print(f"$$$$$$$$ 3 ****** After calling jsondumps : {json_data} ") 
        print(f"$$$$$$$$ 4 ****** After calling jsondumps : {res['weather']} ")  
        '''
        json_data = res
    except Exception as ex:
        ### if error
       print(f"!!!!!!!!  ****** ERROR loading the default data, exception : {ex}")  
       json_data = data

    return json_data

# instantiate the langchain tool.

def meteocris(json_request: str) -> str:
    '''
    This function wraps the meteocris_data_retriever function.
    Converts the input JSON in separated arguments.

    Args:
        request (str): The JSON dictionary input string.

        Takes a JSON dictionary as input in the form:
            { "period":"<period>", "location":"<location>", "specific_variables":["variable_name", ... ]}

        Example:
            { "period":"today", "location":"Madrid", "specific_variables":["humidity"]}

    Returns:
        The weather forecast data for the requested location and time.
    '''
    arguments = json.loads(json_request)
    location = arguments.get('location', None)
    period = arguments.get('period', None)
    specific_variables = arguments.get('specific_variables', [])
    return meteocris_data_retriever(location=location, period=period, specific_variables=specific_variables)


#
# instantiate the langchain tool.
# The tool description instructs the LLM to pass data using a JSON.
# Note the "{{" and "}}": this double quotation is needed
# to avoid a runt-time error triggered by the agent instatiation.
#
name = 'meteocris'
request_format = '{{"period":"period","location":"location","specific_variables":["variable_name"]}}'
description = f'''
Helps to retrieve weather forecast.
Input should be JSON in the following format: {request_format}
Supply "specific_variables" list just if you really need them.
If don't know the value to be assigned to a key, omit the key.
'''

# create an instance of the custom langchain tool
Meteocris = Tool(
    name=name,
    func=meteocris,
    description=description,
    return_direct=False
)
### Test the tool --->  print(meteocris('{ "period":"today", "location":"Arequipa" }'))


#