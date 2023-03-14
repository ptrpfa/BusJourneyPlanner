import requests
import json
import re
from config import *
from bs4 import BeautifulSoup as bs_4

# Function to write to a file
def save_file(text, file_name):
    with open(file_name, 'w') as f:
        f.write(text)

# Function to crawl PAJ's API (limited to 6 API calls per minute)
def crawl_api():
    # Set HTTP header
    headers = {'api-key': api_key}

    # Get bus route data
    routes = requests.get(api_endpoint + '/route', headers=headers, verify=False).text
    save_file(routes, file_routes)

    # Get route coordinates
    geo_routes = requests.get(api_endpoint + '/route-geojson', headers=headers, verify=False).text
    save_file(geo_routes, file_geo_routes)

    # Get route schedule
    route_schedule = requests.get(api_endpoint + '/route-schedule', headers=headers, verify=False).text
    save_file(route_schedule, file_route_schedule)

    # Get bus operators
    operators = requests.get(api_endpoint + '/operators', headers=headers, verify=False).text
    save_file(operators, file_operators)

    # Get live bus data
    bus_live = requests.get(api_endpoint + '/bus-live', headers=headers, verify=False).text
    save_file(bus_live, file_bus_live)

    # Get bus stop data
    bus_stops = requests.get(api_endpoint + '/bus-stop', headers=headers, verify=False).text
    save_file(bus_stops, file_bus_stop)

    # Get bus list data (bus license plates)
    bus_list = requests.get(api_endpoint + '/bus-list', headers=headers, verify=False).text
    save_file(bus_list, file_bus_list)

# Function to crawl webpages for bus schedule information
def crawl_web():
    # Initialise bus schedule
    bus_schedule = {}

    # Loop through each bus (loop)
    for bus in loop_buses:
        list_timings = []
        response = requests.get(schedule_link + bus)
        response = bs_4(response.text, "lxml")
        response = response.find_all('table', attrs={'border':'1'})[1] # Get table
        response = response.find_all('div') # Get rows
        # Loop through each row to get the bus timings
        for row in response:
            list_timings.append(re.search("^<div.*>(\d*)<\/div>$", str(row)).group(1))
        bus_schedule[bus] = list_timings

    # Loop through each one way bus
    for bus in one_way_buses:
        list_timings = []
        response = requests.get(schedule_link + bus)
        response = bs_4(response.text, "lxml")
        response = response.find_all('table', attrs={'border':'1'})[1] # Get table
        
        # Get first direction
        first = response.find_all('tr')[4]
        first = first.find_all('div') # Get rows
        # Loop through each row to get the bus timings
        for row in first:
            list_timings.append(re.search("^<div.*>(\d*)<\/div>$", str(row)).group(1))
        bus_schedule[bus + '-01'] = list_timings
        
        # Get second direction
        list_timings = []
        second = response.find_all('tr')[7]
        second = second.find_all('div') # Get rows
        # Loop through each row to get the bus timings
        for row in second:
            list_timings.append(re.search("^<div.*>(\d*)<\/div>$", str(row)).group(1))
        bus_schedule[bus + '-02'] = list_timings

    # Return bus schedule obtained
    return bus_schedule

# Program Entrypoint
if(CRAWL_API):
    crawl_api()

""" Initialise API data """
routes = json.load(open(file_routes))                   # Bus Route data (used to get overall distance)
routes = routes['data']
geo_routes = json.load(open(file_geo_routes))           # Route Coordinates data (used for displaying of routes)
geo_routes = geo_routes['data']

""" Dynamic API data """
# bus_live = json.load(open(file_bus_live))               # Live Bus data (used for live bus tracking; to call API)
# bus_live = bus_live['data']

""" Unused API data """
# route_schedule = json.load(open(file_route_schedule))   # Route Schedule data (Unused, will be using website data)
# route_schedule = route_schedule['data']
# bus_stop = json.load(open(file_bus_stop))               # Bus Stop data (Unused, will be using dataset given)
# bus_stop = bus_stop['data']
# bus_list = json.load(open(file_bus_list))               # Bus license plates (Unused)
# bus_list = bus_list['data']
# operators = json.load(open(file_operators))             # Bus Operators (Unused)
# operators = operators['data']

if(CRAWL_WEB):
    bus_schedule = crawl_web()
    print(bus_schedule)