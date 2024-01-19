# Program Flags
LOCAL_DB = True        # Boolean to configure the use of local database
CRAWL_API = True       # Boolean to configure the crawling of data from PAJ's API
CRAWL_WEB = True       # Boolean to configure the crawling of data from the bus webpages
UPDATE_DB = True       # Boolean to configure the insertion of crawled data into the database
UPDATE_EDGES = True    # Boolean to configure the updating of edges
UPDATE_WEIGHTS = True  # Boolean to configure the updating of weights

# PAJ API
api_endpoint = 'https://dataapi.paj.com.my/api/v1'
api_key = ''

# Google Map API
gmap_api_key = ''

# Bus Links
schedule_link = "https://businterchange.net/johorbus/routes/routeinfo.php?service="
route_link = "https://businterchange.net/johorbus/routes/276-routes-BMJ.html"
loop_char = '⊃'
one_way_char = '⇔'
loop_buses = ["P101", "P106", "P202", "P403"]       # Buses that run in a loop
one_way_buses = ["P102", "P211", "P411"]            # Buses that only run one way
bus_speed = 70                                      # Assumed bus speed (km/h)

# Database
db_host = ""
db_user = ""
db_password = ""
db_schema = ""
if(LOCAL_DB):
    from local_config import *

# Files and folders
data_folder = "data/"
file_routes = data_folder + "routes.json"
file_geo_routes = data_folder + "geo_routes.json"
file_route_schedule = data_folder + "routes_schedule.json"
file_operators = data_folder + "operators.json"
file_bus_live = data_folder + "bus_live.json"
file_bus_stop = data_folder + "bus_stops.json"
file_bus_list = data_folder + "bus_list.json"
file_bus_schedule = data_folder + "bus_schedule.json"
file_excel_bus = data_folder + "bus_stops.xlsx"