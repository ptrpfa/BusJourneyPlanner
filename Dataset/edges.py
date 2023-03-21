# Program for creation of route edges and calculation of weights
from utils import *

# Program entrypoint
create_route_edges()
# gmaps = googlemaps.Client(key=gmap_api_key) # Initialise Google Map client



# distances = []
# for i in range(len(coords)):
#     loc1 = tuple(coords[i])
#     if(i == (len(coords)-1)):
#             loc2 = tuple(coords[0])
#     else:
#             loc2 = tuple(coords[i + 1])
#     current_dist = gmaps.distance_matrix(loc1, loc2, mode='driving')
#     current_dist = current_dist['rows'][0]['elements'][0]['distance']['value'] / 1000
#     distances.append(current_dist)