import requests
import json

# Configurations
CRAWL = False # Boolean to configure the crawling of data from PAJ's API
api_endpoint = 'https://dataapi.paj.com.my/api/v1'
api_key = 'a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a'
headers = {'api-key': api_key}

# Files
data_folder = "json/"
file_routes = data_folder + "routes.json"
file_geo_routes = data_folder + "geo_routes.json"
file_route_schedule = data_folder + "routes_schedule.json"
file_operators = data_folder + "operators.json"
file_bus_live = data_folder + "bus_live.json"
file_bus_stop = data_folder + "bus_stops.json"
file_bus_list = data_folder + "bus_list.json"

# Function to write to a file
def save_file(text, file_name):
    with open(file_name, 'w') as f:
        f.write(text)

# Function to crawl PAJ's API (limited to 6 API calls per minute)
def crawl_api():
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

# Program Entrypoint
if(CRAWL):
    crawl_api()

# Initialise data
bus_stop = json.load(open(file_bus_stop))               # Bus Stop data
bus_stop = bus_stop['data']
routes = json.load(open(file_routes))                   # Bus Route data
routes = routes['data']
geo_routes = json.load(open(file_geo_routes))           # Route Coordinates data
geo_routes = geo_routes['data']
route_schedule = json.load(open(file_route_schedule))   # Route Schedule data
route_schedule = route_schedule['data']
bus_live = json.load(open(file_bus_live))               # Live Bus data
bus_live = bus_live['data']
# bus_list = json.load(open(file_bus_list))               # Bus license plates (Unused)
# bus_list = bus_list['data']
# operators = json.load(open(file_operators))             # Bus Operators (Unused)
# operators = operators['data']
