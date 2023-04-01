from flask import Flask, render_template, request,json, jsonify
import mapping
import planner
import folium
import random

app=Flask(__name__)

# def processRoutes():
#     processRoutes = planner.process_routes()
#     data_str = ', '.join([str(item) for item in processRoutes])
#     return data_str

@app.route('/')
def root():

    return render_template('index.html')

@app.route("/process-data", methods=["POST"])
def process_data():
    # Get the input data from the request
    start = request.form.get("Start")
    destination = request.form.get("Destination")
    option = request.form.get("Option")

    data = planner.process_data(start, destination, option)

    # Return the processed data as a string
    return data 

    # return render_template('index.html', path_names_coordinates=planner.path_names_coordinates)

#Updating the live map periodically
@app.route('/update_map', methods=["GET"])
def update_map():

    # Generate some random data
    data = mapping.update_markers()

    return json.dumps(data)

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


