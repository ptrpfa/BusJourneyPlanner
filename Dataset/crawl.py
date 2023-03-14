import json
from utils import *

# Program Entrypoint
if(CRAWL_API):
    crawl_api()
if(CRAWL_WEB):
    bus_schedule = crawl_web()
    save_file(str(bus_schedule).replace("'", "\""), file_bus_schedule)

""" Excel Dataset """
dict_data = load_dataset()

""" Webpage data """
bus_schedule = json.load(open(file_bus_schedule))

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

# Start processing here