import googlemaps

# Program Flags
LOCAL_DB = False     # Boolean to configure the use of a local database

# Google Map API
gmap_api_key = 'AIzaSyBV9jbLm29r5xYKHjJrv0UtZk5qMe-KPt4'

# Database
db_host = "34.143.210.189"
db_user = "root"
db_password = "LKP_OOP_STRONG"
db_schema = "DSA_JP"
if(LOCAL_DB):
    from local_config import *

# Initialise Google Map client
gmaps = googlemaps.Client(key=gmap_api_key)