from flask import Flask, render_template, request,json, jsonify
import mapping
import planner
import folium

app=Flask(__name__)

live_map_obj = mapping.Live_Map()

@app.route('/')
def root():
    #Get Live traffic data
    map_html = live_map_obj.getMap()
        
    return render_template('index.html', map=map_html)

@app.route("/process-data", methods=["POST"])
def process_data():
    # Get the input data from the request
    start = request.form.get("Start")
    destination = request.form.get("Destination")
    option = request.form.get("Option")

    planner.process_data(start, destination, option)    
    #print(map_html)
    # Return the processed data as a string
    return "good"

#Updating the live map periodically
@app.route('/update_markers')
def update_markers():
    live_map_obj.update_markers()
    
    # map_fg = live_map_obj.getFeatureGroup()

    return live_map_obj.getMap()

if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)                                                                         


# Process the data
"""
    1) Call the 'utils.get_coordinates' -> This is the starting coordinate
    2) Call the 'utils.get_nearest_bus_stop' -> This is the "Starting" stopID, name, coord, distance
    3) Call the 'utils.get_coordinates' -> This is the ending coordinate
    4) Call the 'utils.get_nearest_bus_stop' -> This is the "Ending" stopID, name, coord, distance
    5) Send to either of the if below to get the path (startId, endID), returns [bustopID1, bustop2]
    6) Get the coordinates all the busstopID, create a function
    6) Plot into folium, coordinates, bus stop name, with marker and route
    7) Get the 'util.getDirection' for populating the Route in html
    
    1) -> 4) see main.py in util folder for example
"""
# if option == 1: #Shortest path

# elif option == 2: #Shortest Time


# # filter out any markers or shapes with missing geometry
# valid_children = []
# for child in map_fg._children.values():
#     print(child.location)
#     try:
#         if child.feature.geometry is not None:
#             valid_children.append(child)
#     except AttributeError:
#         pass

# # create a GeoJSON object from the valid markers and shapes
# if valid_children:
#     geojson = folium.features.GeoJson(valid_children).data
# else:
#     geojson = {"type": "FeatureCollection", "features": []}
#     print("Empty features")

# # convert the GeoJSON object to a JSON string
# json_data = json.dumps(geojson)

# return the JSON string as a JSON response