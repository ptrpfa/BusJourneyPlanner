import googlemaps
import os

# Program Flags
LOCAL_DB = False            # Boolean to configure the use of a local database
LOAD_BUS_FROM_DB = False    # Boolean to configure the loading of bus schedule from the database (otherwise, will load using pickled file)
INTEGRATE_LIVE_BUS = False  # Boolean to configure the integration of live bus data into the calculations of the fastest path

# Telegram Bot API Key
TELEGRAM_KEY = ''

# Google Map API
gmap_api_key = ''

# PAJ API
paj_api_endpoint = 'https://dataapi.paj.com.my/api/v1'
paj_api_live_bus = '%s/bus-live' % paj_api_endpoint
paj_api_key = ''
loop_buses = ["P101", "P106", "P202", "P403"]       # Buses that run in a loop
one_way_buses = ["P102", "P211", "P411"]            # Buses that only run one way
bearing_threshhold = 45                             # Bearing threshold (if bearing between a live bus and a bus stop is within this threshold, assume that the bus is headed towards the bus stop)
bus_speed = 70                                      # Assumed speed of a bus (in km/h)

# Database
db_host = ""
db_user = ""
db_password = ""
db_schema = ""
if(LOCAL_DB):
    from local_config import *

# Email
outgoing_email = ''    # Outgoing email address
outgoing_email_password = ''    # Outgoing email password
outgoing_email_name = ""             # Outgoing email name
email_footer = ""

# File paths 
cwd = os.getcwd()
folder_static = "%s/static/" % cwd
folder_templates = "%s/template/" % cwd
folder_files = "%s/files/" % cwd
folder_utils = "%s/utils/" % cwd
folder_live = "%s/live/" % cwd

# Files
file_pkl_graph = "%sgraph.pkl" % folder_files
file_live_bus = "%sbus_data.json" % folder_live
file_map_html = "%smap.html" % folder_live

# Initialise Google Map client
gmaps = googlemaps.Client(key=gmap_api_key)