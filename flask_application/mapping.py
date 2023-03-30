from cloud_config import *

import folium
import polyline
import requests 
from flask import json, jsonify

def generateUserMap(path_names_coordinates, start_coordinates, end_coordinates,start_bus_stop,end_bus_stop):
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
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=walking&key={gmap_api_key}'
    response = requests.get(url)
    route = response.json()['routes'][0]['overview_polyline']['points']

    # Decode the polyline into a list of latitude and longitude coordinates
    decoded_route = polyline.decode(route)

    # Add polyline to map
    folium.PolyLine(locations=decoded_route, color='red').add_to(map)

    # Generate the Google Maps API request for the walking path from the last stop to the destination
    origin = f'{end_bus_stop["Latitude"]},{end_bus_stop["Longitude"]}'
    destination = f'{end_coordinates[0]},{end_coordinates[1]}'
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=walking&key={gmap_api_key}'
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
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&waypoints={waypoints}&mode=driving&key={gmap_api_key}'
    response = requests.get(url)
    route = response.json()['routes'][0]['overview_polyline']['points']

    # Decode the polyline into a list of latitude and longitude coordinates
    decoded_route = polyline.decode(route)

    # Add polyline to map
    folium.PolyLine(locations=decoded_route, color='blue').add_to(map)

    # Save map to HTML file
    map.save('C:/Users/Jeffr/Downloads/CSC1108-JourneyPlanner-main (3)/CSC1108-JourneyPlanner-main/flask_application/utils/map.html')

    return map._repr_html_()


class Live_Map:

    def __init__(self):
        # Initialize map => Larking Terminal
        self.m = folium.Map(location=[1.4964559999542668, 103.74374661113058], zoom_start=12)

        # Define the feature group for bus markers
        self.bus_group = folium.FeatureGroup(name='Buses', overlay=True, control=True)

        # Add the feature group to the map
        self.m.add_child(self.bus_group)

        # Add a layer control to the map to enable clearing of bus markers
        folium.LayerControl().add_to(self.m)

        # Update markers initially
        self.update_markers()


    def update_markers(self):
        # Clear the bus feature group of previous markers
        self.bus_group._children.clear()

        # API endpoint and key
        api_endpoint = 'https://dataapi.paj.com.my/api/v1'
        gmap_api_key = 'a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a'
        headers = {'api-key': gmap_api_key}

        # Make API request to get bus data
        bus_live = requests.get(api_endpoint + '/bus-live', headers=headers, verify=True)
        bus_data_json = bus_live.json()

        if 'data' not in bus_data_json:
            # handle missing 'data' key in the API response
            print("Error: 'data' key is missing in API response")
            return

        print("Grabbed Data")

        # Write the contents of bus_data_json to a file
        with open(file_live_bus, 'w') as f:
            json.dump(bus_data_json, f)

        # Define the routes to display
        routes_to_display = ["P101", "P102", "P106"]

        # Create a new feature collection
        self.feature_collection = {
            "type": "FeatureCollection",
            "features": []
        }

        # Add markers for buses on specified routes
        for bus_data in bus_data_json['data']:
            if any(route in bus_data['route'] for route in routes_to_display):
                #Get the information
                latitude = bus_data['latitude']
                longitude = bus_data['longitude']
                bus_plate = bus_data['bus']
                speed = bus_data['speed']
                print(bus_plate, speed)

                # Create marker with popup
                popup_html = f"<b>Bus Plate:</b> {bus_plate}<br><b>Speed:</b> {speed} km/h"
                icon = folium.Icon(icon='bus', prefix='fa', color="green")
                marker = folium.Marker(location=[latitude, longitude], icon=icon, popup=folium.Popup(html=popup_html))
                
                # Create a feature for the marker and add it to the feature collection
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            longitude,
                            latitude
                        ]
                    },
                    "properties": {
                        "popup": popup_html,
                        "icon": {
                            "iconUrl": None,
                            "iconSize": [0, 0],
                            "iconAnchor": [0, 0],
                            "popupAnchor": [0, 0],
                            "className": "fa-bus marker-icon"
                        }
                    }
                }
                self.feature_collection['features'].append(feature)

                #Add the new feature group
                self.bus_group.add_child(marker)

                

    def getFeatureGroup(self):

        # convert the GeoJSON object to a JSON string
        json_data = json.dumps(self.feature_collection)

        # return the JSON string as a JSON response
        return jsonify(json_data)

    def getMap(self):


        # js_string = '''
        #     window.onload = function() {
        #         var bus_group = L.featureGroup();
        #         console.log(bus_group.getLayers());
        #     }
        # '''

        # self.m.get_root().script.add_child(folium.Element(js_string))
    


        map_html = self.m._repr_html_()

        return map_html