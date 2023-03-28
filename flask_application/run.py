from flask import Flask, render_template, request
from utils import planner

app=Flask(__name__)

@app.route('/')
def root():
    #Get Live traffic data
    # map_html = plotBus.generate_map()
    
    return render_template('index.html')

@app.route("/process-data", methods=["POST"])
def process_data():
    # Get the input data from the request
    start = request.form.get("Start")
    destination = request.form.get("Destination")
    option = request.form.get("Option")

    map_html = planner.process_data(start, destination, option)    

    # Return the processed data as a string
    return map_html 

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
