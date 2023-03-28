import folium
import polyline

def generateUserMap(path_names_coordinates, start_coordinates, end_coordinates):
    map = folium.Map(location=start_coordinates, zoom_start=13)

    # Add markers for starting and ending locations
    folium.Marker(start_coordinates, popup='Starting Location').add_to(map)
    folium.Marker(end_coordinates, popup='Ending Location').add_to(map)

    # Add markers for all bus stop on the path and pop with name
    for location in path_names_coordinates:
        name = location[0]
        coordinates = location[1:]
        if coordinates is not None:
            folium.Marker(coordinates, popup=name).add_to(map)

    # Generate the Google Maps API request for the walking path from the starting location to the first stop
    origin = f'{start_coordinates[0]},{start_coordinates[1]}'
    destination = f'{start_bus_stop["Latitude"]},{start_bus_stop["Longitude"]}'
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=walking&key={API_KEY}'
    response = requests.get(url)
    route = response.json()['routes'][0]['overview_polyline']['points']

    # Decode the polyline into a list of latitude and longitude coordinates
    decoded_route = polyline.decode(route)

    # Add polyline to map
    folium.PolyLine(locations=decoded_route, color='red').add_to(map)

    # Generate the Google Maps API request for the walking path from the last stop to the destination
    origin = f'{end_bus_stop["Latitude"]},{end_bus_stop["Longitude"]}'
    destination = f'{end_coordinates[0]},{end_coordinates[1]}'
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=walking&key={API_KEY}'
    response = requests.get(url)
    route = response.json()['routes'][0]['overview_polyline']['points']

    # Decode the polyline into a list of latitude and longitude coordinates
    decoded_route = polyline.decode(route)

    # Add polyline to map
    folium.PolyLine(locations=decoded_route, color='red').add_to(map)

    # Generate the Google Maps API request for the route between stops
    stops = [location[1:] for location in path_names_coordinates if location[1:] is not None]
    origin = f'{stops[0][0]},{stops[0][1]}'
    destination = f'{stops[-1][0]},{stops[-1][1]}'
    waypoints = '|'.join([f'{stop[0]},{stop[1]}' for stop in stops[1:]])
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&waypoints={waypoints}&mode=driving&key={API_KEY}'
    response = requests.get(url)
    route = response.json()['routes'][0]['overview_polyline']['points']

    # Decode the polyline into a list of latitude and longitude coordinates
    decoded_route = polyline.decode(route)

    # Add polyline to map
    folium.PolyLine(locations=decoded_route, color='blue').add_to(map)

    # Save map to HTML file
    # map.save('C:/Users/Jeffr/Desktop/123/flask_application/utils/map.html')

    return map._repr_html_()