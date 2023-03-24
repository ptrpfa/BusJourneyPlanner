# Temporary program to explore data collected from PAJ's API
import json
# Files
data_folder = "json/"
file_routes = data_folder + "routes.json"
file_geo_routes = data_folder + "geo_routes.json"
file_route_schedule = data_folder + "routes_schedule.json"
file_operators = data_folder + "operators.json"
file_bus_live = data_folder + "bus_live.json"
file_bus_stop = data_folder + "bus_stops.json"
file_bus_list = data_folder + "bus_list.json"

# Initialise data
routes = json.load(open(file_routes))                   # Bus Route data
routes = routes['data']
geo_routes = json.load(open(file_geo_routes))           # Route Coordinates data
geo_routes = geo_routes['data']
route_schedule = json.load(open(file_route_schedule))   # Route Schedule data
route_schedule = route_schedule['data']
bus_live = json.load(open(file_bus_live))               # Live Bus data
bus_live = bus_live['data']
bus_stop = json.load(open(file_bus_stop))               # Bus Stop data (unused, will be using dataset given)
bus_stop = bus_stop['data']
bus_list = json.load(open(file_bus_list))               # Bus license plates (Unused)
bus_list = bus_list['data']
operators = json.load(open(file_operators))             # Bus Operators (Unused)
operators = operators['data']

# Get buses that do not operate on the same schedule every day
""" 
Buses found:
{'route': 'LB001', 'trip': [{'dayofweek': 'sunday', 'schedule': ['06:15', '10:00', '12:00', '14:30', '18:30']}, {'dayofweek': 'monday', 'schedule': ['06:15', '10:00', '12:00', '14:30', '18:30']}, {'dayofweek': 'tuesday', 'schedule': ['06:15', '10:00', '12:00', '14:30', '18:30']}, {'dayofweek': 'wednesday', 'schedule': ['06:15', '10:00', '12:00', '14:30', '18:30']}, {'dayofweek': 'thursday', 'schedule': []}, {'dayofweek': 'friday', 'schedule': []}, {'dayofweek': 'saturday', 'schedule': ['06:15', '10:00', '12:00', '14:30', '18:30']}]}
{'route': 'LB001A', 'trip': [{'dayofweek': 'sunday', 'schedule': []}, {'dayofweek': 'monday', 'schedule': []}, {'dayofweek': 'tuesday', 'schedule': []}, {'dayofweek': 'wednesday', 'schedule': []}, {'dayofweek': 'thursday', 'schedule': ['06:15', '10:00', '12:00', '14:00', '18:00']}, {'dayofweek': 'friday', 'schedule': ['06:15', '10:00', '12:00', '14:00', '18:00']}, {'dayofweek': 'saturday', 'schedule': []}]}
{'route': 'TK001', 'trip': [{'dayofweek': 'sunday', 'schedule': ['06:15', '10:00', '12:00', '14:00', '16:00', '18:00']}, {'dayofweek': 'monday', 'schedule': ['06:15', '10:00', '12:00', '14:00', '16:00', '18:00']}, {'dayofweek': 'tuesday', 'schedule': ['06:15', '10:00', '12:00', '14:00', '16:00', '18:00']}, {'dayofweek': 'wednesday', 'schedule': ['06:15', '10:00', '12:00', '14:00', '16:00', '18:00']}, {'dayofweek': 'thursday', 'schedule': ['07:30', '13:30', '14:30', '18:30']}, {'dayofweek': 'friday', 'schedule': ['07:30', '13:30', '14:30', '18:30']}, {'dayofweek': 'saturday', 'schedule': ['06:15', '10:00', '12:00', '14:00', '16:00', '18:00']}]}
{'route': 'TK001A', 'trip': [{'dayofweek': 'sunday', 'schedule': ['07:30', '17:00']}, {'dayofweek': 'monday', 'schedule': ['07:30', '17:00']}, {'dayofweek': 'tuesday', 'schedule': ['07:30', '17:00']}, {'dayofweek': 'wednesday', 'schedule': ['07:30', '17:00']}, {'dayofweek': 'thursday', 'schedule': ['09:30', '11:30', '16:00', '17:00']}, {'dayofweek': 'friday', 'schedule': ['09:30', '11:30', '16:00', '17:00']}, {'dayofweek': 'saturday', 'schedule': ['07:30', '17:00']}]} 
"""
for i in range(len(route_schedule)):
    wrong = False
    baseline = route_schedule[i]['trip'][0]
    for j in range(len(route_schedule[i]['trip'])):
            if(route_schedule[i]['trip'][j]['schedule'] != baseline['schedule']):
                    wrong = True
                    break
    if(wrong):
            print(route_schedule[i])
