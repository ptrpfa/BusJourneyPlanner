import openpyxl
import re
import folium
import requests
import polyline

from geopy.geocoders import Nominatim
import webbrowser


from flask import Flask, request, render_template


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


def get_lat_long_from_address(address):         # converts address name into coordinates
   locator = Nominatim(user_agent='myGeocoder')
   location = locator.geocode(address)
   return location.latitude, location.longitude


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

# add new tile layers
folium.TileLayer('OpenStreetMap').add_to(m)
folium.TileLayer('Stamen Terrain', attr="Stamen Terrain").add_to(m)
folium.TileLayer('Stamen Water Color', attr="Stamen Water Color").add_to(m)

# add layers control over the map
folium.LayerControl().add_to(m)


for key,stops in Directory.items():
    color = color_dict.get(key)

    # Generate the OSRM API request for the route between stops
    coordinates = ';'.join([f'{stop[1]},{stop[0]}' for stop in stops])
    url = f'http://router.project-osrm.org/route/v1/driving/{coordinates}'
    response = requests.get(url)
    route = response.json()['routes'][0]['geometry']
    decoded_route = polyline.decode(route) #One whole bus route in driving mode

    # Add markers for each stop in stops list
    for i, stop in enumerate(stops):   
        folium.Marker(stop, tooltip=f'Stop {i+1}', icon=folium.Icon(color=color)).add_to(m)

    # Add a polyline for the bus path
    folium.PolyLine(decoded_route, color=color).add_to(m)


# save the setting on html 
m.save("try.html")

# webbrowser.open("try.html")    <--- can use to automatically open map 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('try.html')

@app.route('/plan-route', methods=['POST'])
def plan_route():
    starting_point = request.form['starting-point']     # Do something with the starting point and destination, such as calculating the route
    destination = request.form['destination']           # Do something with the starting point and destination, such as calculating the route
    Start_coor = get_lat_long_from_address(starting_point)      # changed into coordinates from address name 
    Destin_coor = get_lat_long_from_address(destination)        # changed into coordinates from address name 
    return render_template('try.html')

if __name__ == '__main__':
    app.run()