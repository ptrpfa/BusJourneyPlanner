import requests
import folium
import time

def live_map():
	# API endpoint and key
	api_endpoint = 'https://dataapi.paj.com.my/api/v1'
	api_key = 'a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a'
	headers = {'api-key': api_key}

	# Initialize map
	m = folium.Map(location=[1.4964559999542668, 103.74374661113058], zoom_start=12)

	# Define the routes to display
	routes_to_display = ["P101", "P102", "P106"]

	# Define the feature group for bus markers
	bus_group = folium.FeatureGroup(name='Buses')

	# Add the feature group to the map
	m.add_child(bus_group)

	# Add a layer control to the map to enable clearing of bus markers
	folium.LayerControl().add_to(m)

	# Make API request to get bus data
	bus_live = requests.get(api_endpoint + '/bus-live', headers=headers, verify=True)
	bus_data_json = bus_live.json()
	print("Grabbed Data")

	# Clear the bus feature group of previous markers
	bus_group._children.clear()

	# Add markers for buses on specified routes
	for bus_data in bus_data_json['data']:
		if any(route in bus_data['route'] for route in routes_to_display):
			#Get the information
			latitude = bus_data['latitude']
			longitude = bus_data['longitude']
			bus_plate = bus_data['bus']
			speed = bus_data['speed']

			# Create marker with popup
			popup_html = f"<b>Bus Plate:</b> {bus_plate}<br><b>Speed:</b> {speed} km/h"
			marker = folium.Marker(location=[latitude, longitude], icon=folium.Icon(icon='bus', prefix='fa', color="green"), popup=folium.Popup(html=popup_html))
			bus_group.add_child(marker)

	# Save updated map as HTML file
	return m._repr_html_()