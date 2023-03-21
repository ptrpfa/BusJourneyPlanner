import requests
import re
import pickle
import pandas as pd
import mysql.connector
import googlemaps
from bs4 import BeautifulSoup as bs_4
from config import *

# Function to write to a file
def save_file(text, file_name):
    with open(file_name, 'w') as f:
        f.write(text)

# Function to pickle object (accepts object to pickle and its filename to save as)
def pickle_object (pickle_object, filepath):
    # Create file object to store object to pickle
    file_pickle = open (filepath, 'wb') # w = write, b = bytes (overwrite pre-existing files if any)

    # Pickle (serialise) object [store object as a file]
    pickle.dump (pickle_object, file_pickle)

    # Close file object
    file_pickle.close ()

# Function to load pickle object (accepts filename of pickle to load and returns the de-pickled object)
def load_pickle (filepath):
    # Create file object accessing the pickle file
    file_pickle = open (filepath, 'rb') # r = read, b = bytes

    # Get pickled object
    pickled_object = pickle.load (file_pickle)

    # Close file object
    file_pickle.close ()

    # Return pickle object
    return pickled_object

# Function to crawl PAJ's API (limited to 6 API calls per minute)
def crawl_api():
    # Set HTTP header
    headers = {'api-key': api_key}

    # Get bus route data
    routes = requests.get(api_endpoint + '/route', headers=headers, verify=False).text
    save_file(routes, file_routes)

    # Get route coordinates
    geo_routes = requests.get(api_endpoint + '/route-geojson', headers=headers, verify=False).text
    save_file(geo_routes, file_geo_routes)

    # Get route schedule
    route_schedule = requests.get(api_endpoint + '/route-schedule', headers=headers, verify=False).text
    save_file(route_schedule, file_route_schedule)

    # Get bus operators
    operators = requests.get(api_endpoint + '/operators', headers=headers, verify=False).text
    save_file(operators, file_operators)

    # Get live bus data
    bus_live = requests.get(api_endpoint + '/bus-live', headers=headers, verify=False).text
    save_file(bus_live, file_bus_live)

    # Get bus stop data
    bus_stops = requests.get(api_endpoint + '/bus-stop', headers=headers, verify=False).text
    save_file(bus_stops, file_bus_stop)

    # Get bus list data (bus license plates)
    bus_list = requests.get(api_endpoint + '/bus-list', headers=headers, verify=False).text
    save_file(bus_list, file_bus_list)

# Function to crawl webpages for bus schedule information
def crawl_web():
    # Initialise bus schedule
    bus_schedule = {}

    # Loop through each bus (loop)
    for bus in loop_buses:
        list_timings = []
        response = requests.get(schedule_link + bus)
        response = bs_4(response.text, "lxml")
        response = response.find_all('table', attrs={'border':'1'})[1] # Get table
        response = response.find_all('div') # Get rows
        # Loop through each row to get the bus timings
        for row in response:
            list_timings.append(re.search("^<div.*>(\d*)<\/div>$", str(row)).group(1))
        bus_schedule[bus] = list_timings

    # Loop through each one way bus
    for bus in one_way_buses:
        list_timings = []
        response = requests.get(schedule_link + bus)
        response = bs_4(response.text, "lxml")
        response = response.find_all('table', attrs={'border':'1'})[1] # Get table
        
        # Get first direction
        first = response.find_all('tr')[4]
        first = first.find_all('div') # Get rows
        # Loop through each row to get the bus timings
        for row in first:
            list_timings.append(re.search("^<div.*>(\d*)<\/div>$", str(row)).group(1))
        bus_schedule[bus + '-01'] = list_timings
        
        # Get second direction
        list_timings = []
        second = response.find_all('tr')[7]
        second = second.find_all('div') # Get rows
        # Loop through each row to get the bus timings
        for row in second:
            list_timings.append(re.search("^<div.*>(\d*)<\/div>$", str(row)).group(1))
        bus_schedule[bus + '-02'] = list_timings

    # Return bus schedule obtained
    return bus_schedule

# Function to crawl webpage for a list of all buses
def crawl_web_list():
    global loop_buses, one_way_buses
    loop_buses = []
    one_way_buses = []
    response = requests.get(route_link)
    response = bs_4(response.text, "lxml")
    response = response.find_all('table')[1]    # Get table
    response = response.find_all('tr')[1:]      # Get rows
    # Loop through each row to get the buses
    for row in response:
        bus, route = re.search("<a.*>(.*)<\/a>.*<b>(.*)<\/b>", str(row)).group(1), re.search("<a.*>(.*)<\/a>.*<b>(.*)<\/b>", str(row)).group(2)
        if(loop_char in route):
            loop_buses.append(bus)
        elif(one_way_char in route):
            one_way_buses.append(bus)
    # return loop_buses, one_way_buses

# Function to load bus dataset
def load_dataset():
    # Load excel file
    excel = pd.ExcelFile(file_excel_bus)
    # Initialise empty dictionary
    data = {}
    # Loop through each sheet
    for sheet in excel.sheet_names:
        # Get dataframe
        df = excel.parse(sheet)
        # Create empty longitude column
        df['Longitude'] = 0
        # Rename column
        df.rename(columns = {'Stop ID': 'StopOrder', 'Bus stop': 'Bus Stop', 'GPS Location': 'Latitude'}, inplace = True)
        # Loop through each row of the current dataframe
        for index in df.index:
            # Get coordinates
            coordinates = df.loc[index]['Latitude']
            df.at[index, 'Latitude'], df.at[index, 'Longitude'] = [i.strip() for i in coordinates.split(",")]
        # Set dataframe to be value of key in dictionary
        data[sheet] = df
    # Return data dictionary
    return data

# Function to create route edges
def create_route_edges():
    # Initialise database connection
    mysql_db = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_schema)
    db_cursor = mysql_db.cursor(buffered=True)

    # Get bus information
    loop_buses = []
    one_way_buses = []
    sql = "SELECT BusID, Type FROM Bus;"
    db_cursor.execute(sql)
    for i in db_cursor:
        if(i[1] == 1):
            one_way_buses.append(i[0])
        elif(i[1] == 2):
            loop_buses.append(i[0])

    # Get bus route information
    for i in loop_buses:
        # Get current route
        sql = "SELECT BusRoute.*, BusStop.Latitude, BusStop.Longitude FROM BusRoute INNER JOIN BusStop ON BusRoute.BusStopID = BusStop.BusStopID WHERE BusID = %s ORDER BY StopOrder ASC;" % i
        routes = []
        db_cursor.execute(sql)
        for j in db_cursor:
            current_route = {'RouteID': j[0], 'BusID': j[1], 'BusStopID': j[2], 'StopOrder': j[3], 'Latitude': j[4], 'Longitude': j[5]}
            routes.append(current_route)
        # Create edges
        for j in range(len(routes)):
            insert_sql = "INSERT INTO Edge (FromBusStopID, ToBusStopID, RouteID) VALUES (%s, %s, %s)"
            if(j == (len(routes) - 1)):
                insert_sql = insert_sql % (routes[j]['BusStopID'], routes[0]['BusStopID'], routes[j]['RouteID'])        # Last bus stop in route is linked to the first bus stop
            else:
                insert_sql = insert_sql % (routes[j]['BusStopID'], routes[j + 1]['BusStopID'], routes[j]['RouteID'])    # Each bus stop is connected to the following bus stop in the route
            db_cursor.execute(insert_sql)

    for i in one_way_buses:
        # Get current route
        sql = "SELECT BusRoute.*, BusStop.Latitude, BusStop.Longitude FROM BusRoute INNER JOIN BusStop ON BusRoute.BusStopID = BusStop.BusStopID WHERE BusID = %s ORDER BY StopOrder ASC;" % i
        routes = []
        db_cursor.execute(sql)
        for j in db_cursor:
            current_route = {'RouteID': j[0], 'BusID': j[1], 'BusStopID': j[2], 'StopOrder': j[3], 'Latitude': j[4], 'Longitude': j[5]}
            routes.append(current_route)
        # Create edges
        for j in range(len(routes) - 1):
            insert_sql = "INSERT INTO Edge (FromBusStopID, ToBusStopID, RouteID) VALUES (%s, %s, %s)"
            insert_sql = insert_sql % (routes[j]['BusStopID'], routes[j + 1]['BusStopID'], routes[j]['RouteID'])    # Each bus stop is connected to the following bus stop in the route
            db_cursor.execute(insert_sql)

    # Effect changes
    mysql_db.commit()

    # Close connections
    db_cursor.close()
    mysql_db.close()

# Function to populate weights
def create_weights(weight_type):
    # Weight types:
    # 1: Distance (km)
    # 2: Duration (minutes)

    # Initialise database connection
    mysql_db = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_schema)
    db_cursor = mysql_db.cursor(buffered=True)

    # Get edges from the database
    edges = []
    sql = "SELECT Edge.*, bsfrom.Latitude AS \"FromLat\", bsfrom.Longitude AS \"FromLong\", bsto.Latitude AS \"ToLat\", bsto.Longitude AS \"ToLong\" FROM Edge INNER JOIN BusStop AS bsfrom ON Edge.FromBusStopID = bsfrom.BusStopID INNER JOIN BusStop AS bsto ON Edge.ToBusStopID = bsto.BusStopID;"
    db_cursor.execute(sql)
    for i in db_cursor:
        current_edge = {'EdgeID': i[0], 'From':i[1], 'To': i[2], 'RouteID': i[3], 'FromLatitude':i[4], 'FromLongitude': i[5], 'ToLatitude': i[6], 'ToLongitude': i[7]}
        edges.append(current_edge)

    # Distance
    if(weight_type == 1):
        # Initialise Google Map client
        gmaps = googlemaps.Client(key=gmap_api_key)
        
        # Calculate distance between starting point and destination
        for i in range(len(edges)):
            # Get starting and ending coordinates
            from_bus_stop = (edges[i]['FromLatitude'], edges[i]['FromLongitude'])
            to_bus_stop = (edges[i]['ToLatitude'], edges[i]['ToLongitude'])

            # Get distance between points (in km)
            current_dist = gmaps.distance_matrix(from_bus_stop, to_bus_stop, mode='driving')
            current_dist = current_dist['rows'][0]['elements'][0]['distance']['value'] / 1000
            edges[i]['Distance'] = current_dist

        # Loop through each edge
        for i in edges:
            insert_sql = "INSERT INTO Weight (EdgeID, Weight, Type) VALUES (%s, %s, 1)" % (i['EdgeID'], i['Distance'])
            db_cursor.execute(insert_sql)

    # Effect changes
    mysql_db.commit()

    # Close connections
    db_cursor.close()
    mysql_db.close()
