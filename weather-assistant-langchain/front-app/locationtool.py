# A langchain tool that retrieves current location data

import json
from langchain.agents import Tool


def location(json_request: str = None) -> str:
    '''
    Returns:
        The current location data in JSON format.
    '''
    data = {}

    # this function is a mockup, returns fake/hardcoded location forecast data
    data['city'] = 'Madrid'
    data['country'] = 'Spain'
    data['latitude'] = 40.4167
    data['longitude'] = -3.703
    data['timezone'] = 'Europe/Madrid'
    return json.dumps(data)


# instantiate the langchain tool.
# The tool description instructs the LLM to pass data using a JSON.
# Note the "{{" and "}}": this double quotation is needed
# to avoid a runt-time error triggered by the agent instantiation.
#
name = 'current_location'
description = 'Helps to retrieve current location data (where I\'m now). Returns a JSON with relevant variables'

# create an instance of the custom langchain tool
Location = Tool(
    name=name,
    func=location,
    description=description,
    return_direct=False
)