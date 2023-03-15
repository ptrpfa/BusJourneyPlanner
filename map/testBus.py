import openpyxl
import re
import folium
import requests
import polyline

def bus_stops():
    # Load the workbook
    workbook = openpyxl.load_workbook('bus_stops.xlsx')

    #Define dict of stops
    Directory = {}

    # Define a regular expression pattern to match latitude and longitude in the format "number, number"
    pattern = r'^-?\d+\.\d+,\s?-?\d+\.\d+$'
    regex = re.compile(pattern)

    # Loop through all sheets in the workbook
    for sheet in workbook.worksheets:

        #Store the stops
        stops=[]

        # Loop through the rows starting from the second row and print the value of the third column
        for row in sheet.iter_rows(min_row=2, values_only=True):

            if not regex.match(row[2]):
                continue  # skip if third column does not match regex  

            lat, lng = map(float, row[2].split(", "))
            stops.append((lat, lng)) 

        #Store the stops
        Directory[sheet.title] = stops

    return Directory

def find_bus_route(destination):
    for bus_route, stops in Directory.items():
        coordinates = f'{stops[0][1]},{stops[0][0]};{destination[1]},{destination[0]}'
        url = f'http://router.project-osrm.org/route/v1/driving/{coordinates}'
        response = requests.get(url)
        route = response.json()['routes'][0]['geometry']
        decoded_route = polyline.decode(route)

        # Check if the destination is on the bus route
        if destination in stops:
            # Return the bus route and the path from the first stop to the destination
            return bus_route, decoded_route

    # If no bus route goes to the destination, return None
    return None

def find_route_coordinates(destination):
    # Get the bus stops dictionary
    Directory = bus_stops()

    # Loop through all bus routes
    for bus_route, stops in Directory.items():

        # Check if the destination is one of the bus stops on this route
        if destination in stops:
            # If it is, generate the OSRM API request for the route between stops
            coordinates = ';'.join([f'{stop[1]},{stop[0]}' for stop in stops])
            url = f'http://router.project-osrm.org/route/v1/driving/{coordinates}'
            response = requests.get(url)
            route = response.json()['routes'][0]['geometry']
            decoded_route = polyline.decode(route) #One whole bus route in driving mode
            return decoded_route, bus_route

    # If the destination is not a bus stop on any route, return None
    return None, None

Directory = bus_stops()

color_dict = {
    'P101-loop': 'darkred',
    'P102-01': 'orange',
    'P102-02': 'beige',
    'P106-loop': 'darkgreen',
    'P202-loop': 'cadetblue',
    'P211-01': 'black',
    'P211-02': 'darkpurple',
    'P403-loop': 'pink',
    'P411-01': 'white',
    'P411-02': 'gray',
}

# Create a map centered at the first stop
m = folium.Map(location=(1.4964559999542668, 103.74374661113058), zoom_start=15) #Larkin Terminal

# Commented out plot for all routes
# for key,stops in Directory.items():
#     color = color_dict.get(key)

#     # Generate the OSRM API request for the route between stops
#     coordinates = ';'.join([f'{stop[1]},{stop[0]}' for stop in stops])
#     url = f'http://router.project-osrm.org/route/v1/driving/{coordinates}'
#     response = requests.get(url)
#     route = response.json()['routes'][0]['geometry']
#     decoded_route = polyline.decode(route) #One whole bus route in driving mode

#     # Add markers for each stop in stops list
#     for i, stop in enumerate(stops):   
#         folium.Marker(stop, tooltip=f'Stop {i+1}', icon=folium.Icon(color=color)).add_to(m)

#     # Add a polyline for the bus path
#     folium.PolyLine(decoded_route, color=color).add_to(m)

# Get the destination from the user
destination = (1.4689940555974177, 103.7368740086021)

# Find the bus route
result = find_bus_route(destination)

# Print the bus route and path to the destination if found, else print a message indicating that no bus route goes to the destination
if result:
    bus_route, path = result
    print(f'Take bus route {bus_route} and follow this path to your destination:')
    for point in path:
        print(point)

    color = color_dict.get(bus_route)

    # Add markers for each stop in stops list
    for i, stop in enumerate(Directory[bus_route]):   
        folium.Marker(stop, tooltip=f'Stop {i+1}', icon=folium.Icon(color=color)).add_to(m)

    # Add a polyline for the bus path
    folium.PolyLine(path, color='red').add_to(m)
else:
    print('No bus route goes to the destination.')


# Display the map
m.save("mapTestingUhSiol.html")