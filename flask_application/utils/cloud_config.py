import googlemaps
import os

# Program Flags
LOCAL_DB = False            # Boolean to configure the use of a local database
LOAD_BUS_FROM_DB = False    # Boolean to configure the loading of bus schedule from the database (otherwise, will load using pickled file)

# Google Map API
gmap_api_key = 'AIzaSyBV9jbLm29r5xYKHjJrv0UtZk5qMe-KPt4'

# Database
db_host = "34.143.210.189"
db_user = "root"
db_password = "LKP_OOP_STRONG"
db_schema = "DSA_JP"
if(LOCAL_DB):
    from local_config import *

# Email
outgoing_email = '2023.dsa.group7@gmail.com'    # Outgoing email address
outgoing_email_password = 'wmnhjzitsbsepjow'    # Outgoing email password
outgoing_email_name = "DSA Group 7"             # Outgoing email name

# File paths 
cwd = os.getcwd()
folder_static = "%s/static/" % cwd
folder_templates = "%s/template/" % cwd
folder_pickles = "%s/pickles/" % cwd
folder_utils = "%s/utils/" % cwd

# Files
file_pickle_bus_schedule = "%sbus_schedule.pkl" % folder_pickles

# Initialise Google Map client
gmaps = googlemaps.Client(key=gmap_api_key)