from cloud_config import *
from setup import *
# from algorithms import *

from bs4 import BeautifulSoup as bs_4
from email.mime.text import MIMEText            
from email.mime.multipart import MIMEMultipart  
from email.header import Header                 
from email.utils import formataddr    
from queue import PriorityQueue
from pathlib import Path
import re
import mysql.connector
import datetime
import smtplib      
import pickle
import haversine as hs
import heapq
import requests
import math
import json

def save_file(text, file_name):
    """
    Function to write to a file
    """
    with open(file_name, 'w') as f:
        f.write(text)

def check_file_exists(file_path):
    """
    Function to check if a particular file exists
    """
    return Path(file_path).exists()

def pickle_object (pickle_object, filepath):
    """ 
    Function for pickling an object
    """
    # Create file object to store object to pickle
    file_pickle = open (filepath, 'wb') # w = write, b = bytes (overwrite pre-existing files if any)

    # Pickle (serialise) object [store object as a file]
    pickle.dump (pickle_object, file_pickle)

    # Close file object
    file_pickle.close ()

def load_pickle (filepath):
    """
    Function for de-pickling an object
    """
    # Create file object accessing the pickle file
    file_pickle = open (filepath, 'rb') # r = read, b = bytes

    # Get pickled object
    pickled_object = pickle.load (file_pickle)

    # Close file object
    file_pickle.close ()

    # Return pickle object
    return pickled_object

def validate_coordinates(latitude, longitude):
    """
    Function to validate a set of coordinates

    """

    if(latitude >= -90 and latitude <= 90 and longitude >= -180 and longitude <= 180):
        return True
    else:
        return False

def get_location(latitude, longitude):
    """
    Function to get a readable address from a set of coordinates

    """

    coordinates = (latitude, longitude)
    address = gmaps.reverse_geocode(coordinates)[0]['formatted_address']
    return address

def get_coordinates(location):
    """
    Function to get the approximate coordinates of a given address
    Note: inputs should be as unambiguous as possible for better accuracy

    """

    coordinates = gmaps.geocode(location)
    # Check if a result was received
    if(coordinates):
        coordinates = coordinates[0]
        coordinates = (coordinates['geometry']['location']['lat'], coordinates ['geometry']['location']['lng'])
        return coordinates
    else:
        return None
    
def get_nearest_bus_stop(latitude, longitude, limit=True): # Weight: Distance
    """
    Function to get the nearest bus stop to a set of coordinates

    """
    if(limit):
        # Get nearest bus stop
        nearest_bus_stop = None
        sql = "SELECT *, ST_Distance_Sphere(POINT(Longitude, Latitude), POINT(%s, %s)) / 1000 as Distance FROM BusStop ORDER BY Distance LIMIT 1;" % (longitude, latitude)
        results = sql_query(sql)

        for i in results:
            nearest_bus_stop = {'StopID': i[0], 'Name': i[1], 'Latitude': i[2], 'Longitude': i[3], 'Coordinates': [i[2], i[3]], 'Distance': i[4]}
    else:
        # Get nearest bus stop
        nearest_bus_stop = []
        sql = "SELECT *, ST_Distance_Sphere(POINT(Longitude, Latitude), POINT(%s, %s)) / 1000 as Distance FROM BusStop ORDER BY Distance;" % (longitude, latitude)
        results = sql_query(sql)

        for i in results:
            current_bus_stop = {'StopID': i[0], 'Name': i[1], 'Latitude': i[2], 'Longitude': i[3], 'Coordinates': [i[2], i[3]], 'Distance': i[4]}
            nearest_bus_stop.append(current_bus_stop)

    # Return nearest bus stop
    return nearest_bus_stop

def get_bearing(lat1, long1, lat2, long2):
    """
    Function to calculate the bearing between two given coordinates
    From: (lat1, long1)
    To: (lat2, long2)
    """
    # Convert latitude and longitude to radians
    lat1 = math.radians(lat1)
    long1 = math.radians(long1)
    lat2 = math.radians(lat2)
    long2 = math.radians(long2)

    # Calculate the bearing
    bearing = math.degrees(math.atan2(math.sin(long2 - long1) * math.cos(lat2), math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(long2 - long1)))

    # Ensure bearing is positive
    bearing = (bearing + 360) % 360

    # Return bearing
    return bearing

def get_live_bus():
    """ 
    Function to get live bus data from PAJ's API, function will add new bus arrival timings into the Schedule table 
    and return a list of the respective ScheduleIDs that have been added. These temporary rows will be required to be removed in later parts of the program.
    """
    # Initialise list of scheduleIDs that have been added by this function
    list_schedules = []

    # Initialise list of live buses
    list_buses = []

    # API endpoint and key
    headers = {'api-key': paj_api_key}

    # Check if live bus data JSON file exists
    if(not check_file_exists(file_live_bus)):
        # Make API request to get bus data only if the file does not exist (calling of PAJ API left to mapping functions)
        live_bus = requests.get(paj_api_live_bus, headers=headers, verify=True)
        # Save file
        save_file(live_bus.text, file_live_bus)
        live_bus = live_bus.json()['data']
    else:
        # Load bus data from JSON file directly
        live_bus = json.load(open(file_live_bus))
        live_bus = live_bus['data']

    # Parse API data
    for bus in live_bus:
        # Check bus service and moving buses
        if((bus['route'][0] in loop_buses + one_way_buses) and bus['speed'] > 0):
            current_bus = {'Bus': bus['route'][0], 'BusPlate': bus['bus'], 'Datetime': datetime.datetime.strptime(bus['timestamp'], '%Y-%m-%d %H:%M:%S'), 
                           'Latitude': bus['latitude'], 'Longitude': bus['longitude'], 'Coordinates': [bus['latitude'], bus['longitude']], 'Speed': bus['speed'], 'Bearing': bus['bearing']}
            list_buses.append(current_bus)

    # Initialise database connection
    mysql_db = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_schema)
    db_cursor = mysql_db.cursor(buffered=True)

    # Get max scheduleID from database
    max_sql = "SELECT MAX(ScheduleID) FROM Schedule;"
    db_cursor.execute(max_sql)
    schedule_id = db_cursor.fetchall()[0][0] + 1

    # Loop through each bus to determine the bus stop that the bus is heading towards
    for bus in list_buses:
        # Initialise target bus stop
        target_bus_stop = None
        # Initialise routeID
        route_id = None
        # Initialise list of potential bus stops that the bus is heading to
        list_bus_stops = []
        # Get the distance between the bus and all other bus stops in the database (list returned will be sorted in ascending order, according to the distance between the bus stop and the bus)
        bus_stops = get_nearest_bus_stop(bus['Latitude'], bus['Longitude'], False)

        # Loop through each bus stop
        for bus_stop in bus_stops:
            # Calculate the bearing between the bus to the current bus stop (order matters)
            bus_stop['Bearing'] = abs(bus['Bearing'] - get_bearing(bus['Latitude'], bus['Longitude'], bus_stop['Latitude'], bus_stop['Longitude']))
            # Add bus stop to list of potential bus stops if its bearing is within 45 degrees of the bus's current bearing 
            if(abs(bus_stop['Bearing']) <= bearing_threshhold):    # Bus is assumed to be headed towards the bus stop if its bearing is within the specified threshold
                list_bus_stops.append(bus_stop)

        # Loop through each potential bus stop
        for bus_stop in list_bus_stops:
            # Check if an edge exists between the bus to the bus stop
            # Limitation: We are unable to distinguish which one-way bus service is being used currently (direction 1 or 2), queries for one-way buses might be wrong
            sql = "SELECT Edge.*, BusRoute.BusID, Bus.Name FROM Edge JOIN BusRoute ON Edge.RouteID = BusRoute.RouteID JOIN Bus ON BusRoute.BusID = Bus.BusID WHERE Edge.ToBusStopID = %s AND Bus.Name LIKE \"%%%s%%\";" % (bus_stop['StopID'], bus['Bus'])
            db_cursor.execute(sql)
            # Get first matching bus stop to be the target bus stop (current list of bus stops is already implicitly sorted according to its distance from the bus, lower index = closer to bus)
            if(db_cursor.rowcount):
                # Set target bus stop to be the first match
                target_bus_stop = bus_stop
                # Get RouteID
                route_id = db_cursor.fetchall()[0][3]
                # Break out of loop
                break

        # Check for a matching bus stop
        if(target_bus_stop and route_id):
            # Calculate duration (in minutes)
            duration = (target_bus_stop['Distance'] / bus['Speed']) * 60
            # Get estimated time of bus arrival
            arrival_time = datetime.timedelta(minutes=duration) + datetime.datetime.now()
            # Add new bus schedule into the database
            insert_sql = "INSERT INTO Schedule VALUES (%s, %s, \"%s\");" % (schedule_id, route_id, arrival_time.time())
            db_cursor.execute(insert_sql)
            # Add scheduleID into list of temporarily created bus schedules
            list_schedules.append(schedule_id)
            # Update scheduleID
            schedule_id += 1

    # Effect changes
    mysql_db.commit()
                
    # Close connections
    db_cursor.close()
    mysql_db.close()

    # Return list of scheduleIDs that have been added
    return list_schedules

def get_fastest_bus_stop(start_bus_stop_id): # Weight: Duration (time)
    """
    Function to get fastest bus stop, taking into account the duration from the starting bus stop to the next bus stop, 
    as well as the next available bus
    """

    # Initialise database connection
    mysql_db = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_schema)
    db_cursor = mysql_db.cursor(buffered=True)

    # Check if live bus data is to be incorporated
    if(INTEGRATE_LIVE_BUS):
        # Get list of scheduleIDs for the arrival timings of live buses, if the program flag is set (limitation: function execution is slow due to the calculations required to determine the direction of each bus, and which bus stop that it is headed to)
        list_schedules = get_live_bus()

    # Get list of nearest bus stops, in ascending order (fastest one in lower index)
    bus_stops = []

    # Check if there are any scheduled buses for the day
    check_sql = "SELECT IF(CURRENT_TIME() <= (SELECT MAX(Time) FROM Schedule), \"Today\", \"Tomorrow\");"
    db_cursor.execute(check_sql)
    bus_day = db_cursor.fetchall()[0][0]

    # Boolean to check bus day
    today = None

    # Get bus stops
    if(bus_day == "Today"):
        # Get buses for the day
        today = True
        sql = "SELECT Edge.*, Bus.BusID, Bus.Name, Schedule.Time AS Time, Weight.Weight As Duration, TIMESTAMPDIFF(SECOND, CURRENT_TIME(), Time) / 60 AS Waiting_Time, (Weight.Weight + (TIMESTAMPDIFF(SECOND, CURRENT_TIME(), Time) / 60)) AS Total_Time FROM Edge JOIN BusRoute ON Edge.RouteID = BusRoute.RouteID  JOIN Bus ON BusRoute.BusID = Bus.BusID JOIN Weight ON Edge.EdgeID = Weight.EdgeID  JOIN Schedule ON BusRoute.RouteID = Schedule.RouteID  WHERE Edge.FromBusStopID = %s AND Weight.Type = 2 AND Time >= CURRENT_TIME() ORDER BY Total_Time ASC;" % start_bus_stop_id
    else:
        # Get buses for the next day
        today = False
        sql = "SELECT Edge.*, Bus.BusID, Bus.Name, Schedule.Time AS Time, Weight.Weight As Duration, TIMESTAMPDIFF(SECOND, CURRENT_TIME(), CONCAT(DATE(NOW() + INTERVAL 1 DAY), \' \', Time)) / 60 AS Waiting_Time, (Weight.Weight + (TIMESTAMPDIFF(SECOND, CURRENT_TIME(), CONCAT(DATE(NOW() + INTERVAL 1 DAY), \' \', Time)) / 60)) AS Total_Time FROM Edge JOIN BusRoute ON Edge.RouteID = BusRoute.RouteID  JOIN Bus ON BusRoute.BusID = Bus.BusID JOIN Weight ON Edge.EdgeID = Weight.EdgeID JOIN Schedule ON BusRoute.RouteID = Schedule.RouteID WHERE Edge.FromBusStopID = %s AND Weight.Type = 2 ORDER BY Total_Time ASC;" % start_bus_stop_id
    db_cursor.execute(sql)

    # Check for edge cases whereby the bus stop only has few buses (ie only one bus service), and there is no more scheduled buses for the day
    if(today and db_cursor.rowcount == 0):
        # Get buses for the next day instead in this case
        today = False
        sql = "SELECT Edge.*, Bus.BusID, Bus.Name, Schedule.Time AS Time, Weight.Weight As Duration, TIMESTAMPDIFF(SECOND, CURRENT_TIME(), CONCAT(DATE(NOW() + INTERVAL 1 DAY), \' \', Time)) / 60 AS Waiting_Time, (Weight.Weight + (TIMESTAMPDIFF(SECOND, CURRENT_TIME(), CONCAT(DATE(NOW() + INTERVAL 1 DAY), \' \', Time)) / 60)) AS Total_Time FROM Edge JOIN BusRoute ON Edge.RouteID = BusRoute.RouteID  JOIN Bus ON BusRoute.BusID = Bus.BusID JOIN Weight ON Edge.EdgeID = Weight.EdgeID JOIN Schedule ON BusRoute.RouteID = Schedule.RouteID WHERE Edge.FromBusStopID = %s AND Weight.Type = 2 ORDER BY Total_Time ASC;" % start_bus_stop_id
        db_cursor.execute(sql)

    # Loop through buses obtained
    for i in db_cursor:
        # Parse each row
        schedule_time = datetime.datetime.min + i[6]
        bus_stop = {'EdgeID': i[0], 'BusStopID': i[2], 'BusID': i[4], 'Bus': i[5], 'NextBus': schedule_time, 'Duration': i[7], 'Wait': float(i[8]), 'Total': i[9]}
        # Get BusID
        bus_stops.append(bus_stop)

    # Check if live bus data is to be incorporated
    if(INTEGRATE_LIVE_BUS):
        # Loop through each scheduleID that have been created for live bus
        for schedule_id in list_schedules:
            # Delete temporarily created schedule
            delete_sql = "DELETE FROM Schedule WHERE ScheduleID = %s;" % schedule_id
            db_cursor.execute(delete_sql)

    # Effect changes
    mysql_db.commit()
    
    # Close the cursor and connection
    db_cursor.close()
    mysql_db.close()

    # Return next fastest path
    return bus_stops

def get_directions(origin_coordinates, destination_coordinates):
    """
    Function to get directions from an origin to a destination point

    """

    # Set strings
    origin_string = "%s,%s" % (origin_coordinates[0], origin_coordinates[1])
    destination_string = "%s,%s" % (destination_coordinates[0], destination_coordinates[1])

    # Initialise direction string
    str_directions = None

    # Get directions
    directions = gmaps.directions(origin_string, destination_string, mode='walking', departure_time=datetime.datetime.now())[0]['legs'][0]
    
    # Prepare overall directions
    str_directions = "Total Distance: %s" % directions['distance']['text']
    str_directions += "\nEstimated Duration: %s" % directions['duration']['text']  

    # Parse instructions
    directions = directions['steps']
    for i in range(len(directions)):
        # Header
        if('maneuver' in directions[i].keys()):
            str_directions += "\n\nStep %s:\nInstruction: %s\nGuide: %s" % (i + 1, directions[i]['maneuver'].title().replace("-", " "), bs_4(directions[i]['html_instructions'], 'html.parser').get_text())
        else:
            str_directions += "\n\nStep %s:\nInstruction: %s" % (i + 1, bs_4(directions[i]['html_instructions'], 'html.parser').get_text())
        # Body
        str_directions += "\nDistance: %s m\nWalking Time: %s" % (directions[i]['distance']['value'], directions[i]['duration']['text'])
        str_directions += "\nStart Point: %s (%s, %s)" % (get_location(directions[i]['start_location']['lat'], directions[i]['start_location']['lng']), directions[i]['start_location']['lat'], directions[i]['start_location']['lng'])
        str_directions += "\nEnd Point: %s (%s, %s)" % (get_location(directions[i]['end_location']['lat'], directions[i]['end_location']['lng']), directions[i]['end_location']['lat'], directions[i]['end_location']['lng'])
    # Return directions
    return str_directions

def send_email(incoming_email, subject, message):
    """ 
    Function for sending email
    """
    # Set email header
    msg = MIMEMultipart ()
    msg ['From'] = formataddr ((str (Header (outgoing_email_name, 'utf-8')), outgoing_email))
    msg ['To'] = incoming_email
    msg ['Subject'] = subject
    # Set email message
    msg.attach (MIMEText(message + email_footer, 'html'))
    text = msg.as_string () 
    # Initialise send status
    email_sent = None
    try:
        # Start SMTP server
        server = smtplib.SMTP ('smtp.gmail.com', 587)
        server.starttls ()
        # Login to server
        server.login (outgoing_email, outgoing_email_password)
        # Send email notification
        server.sendmail (outgoing_email, incoming_email, text)
        email_sent = True
    except Exception as error:
        email_sent = False
    finally:
        # Close server regardless whether the email was sent successfully or not
        server.quit ()
        return email_sent
    
def test_function():
    for start_bus_stop_id in range(1, 168):
        print("Bus Stop: %s (%s)" % (start_bus_stop_id, len(get_fastest_bus_stop(start_bus_stop_id))))

#------------------------------------------------------------------------------------------------------------------------------------------------------------

def getData():
    """ 
    Function to load graph and return the graph object to caller 
    """

    # Open the pickled file in read binary mode
    data = None
    with open(file_pkl_graph, 'rb') as f:
        # Load the contents of the file
        data = pickle.load(f)

    # Close the file
    f.close()
    return data

def shortest_path_with_min_transfers(start, end):
	"""
	Dijkstra algo to get the shortest path with minumum # of transfers
    
    Parameters:
    -----------
	start - FromBusStopID
	end - EndBusStopID

	Output:
	------
	path_data = {
		"Path":[ busStopID_1, busStopID_2, busStopID_3 ], 
		"Total-Distance": Distance for journey from start to end bus stop
	}
    """

	#Get Graph
	graph = getData()

	if graph is None:
		return None #Error

	# Create a dictionary to keep track of the minimum number of transfers required to reach each node
	min_transfers = {node: float('inf') for node in graph.nodes()}
	min_transfers[start] = 0

	# Create a dictionary to keep track of the total distance from the source to each node
	total_distance = {node: float('inf') for node in graph.nodes()}
	total_distance[start] = 0

	# Create a dictionary to keep track of the number of transfers made so far
	num_transfers = {node: 0 for node in graph.nodes()}

	# Create a dictionary to keep track of the previous node in the shortest
	# path from the source to each node
	previous = {node: None for node in graph.nodes()}

	# Create a priority queue to store the nodes to be visited
	queue = [(0, start, 0)]  # (total_distance, node, num_transfers)

	while queue:
		curr_distance, curr_node, curr_transfers = heapq.heappop(queue)

		# Check if we've reached the target
		if curr_node == end:
			# Construct the shortest path from the previous nodes
			path = []

			while curr_node is not None:
				path.append(curr_node)
				curr_node = previous[curr_node]

			path.reverse()
			path_data = {"Path":path, "Total-Distance":total_distance[end]}


			# #Print the routes and the distance between each edge
			# shortest_path = {}

			# for i in range(len(path)-1):
			#     u, v = path[i], path[i+1]
			#     data = graph.get_edge_data(u, v)
			#     min_weight = round(total_distance[v] - total_distance[u],3)
			#     bus = next(sub_data['bus'] for sub_data in data.values() if sub_data['weight'] == min_weight)

			#     shortest_path[f"{u}-{v}"] = f"bus-{bus}, distance={min_weight}"
			#     distance += min_weight
        
			return path,total_distance[end]

		# Check if we've already visited this node with a smaller number of transfers
		if curr_transfers > min_transfers[curr_node]:
			continue

		# Update the minimum number of transfers required to reach each neighbor
		for neighbor in graph.neighbors(curr_node):
			#If visited then ignore
			if previous[curr_node] == neighbor:
				continue

			#Calculate minimum of the current->neighbor. Two nodes two different routes.
			#E.g A->C, route 1 and route 2
			min_route_to_prev_neighbor = None	
			min_route_to_neighbor = min(graph[curr_node][neighbor].values(), key=lambda x: x['weight'])
			if previous[curr_node] is not None:
				min_route_to_prev_neighbor = min(graph[previous[curr_node]][curr_node].values(), key=lambda x: x['weight'])

			# Calculate the number of transfers made to reach this neighbor
			# previous[current_node] = gives the linking node to this current_node
			if previous[curr_node] is None or min_route_to_neighbor['bus'] != min_route_to_prev_neighbor['bus']:
				transfers = curr_transfers + 1
			else:
				transfers = curr_transfers

			# Calculate the total distance from the source to this neighbor
			distance = curr_distance + min_route_to_neighbor['weight']

			# Update the minimum number of transfers required to reach this neighbor
			if transfers < min_transfers[neighbor]:
				min_transfers[neighbor] = transfers

			# Check if we've found a shorter path to this neighbor
			if distance < total_distance[neighbor]:
				# Update the total distance to this neighbor
				total_distance[neighbor] = distance

				# Update the number of transfers made to reach this neighbor
				num_transfers[neighbor] = transfers

				# Update the previous node in the shortest path to this neighbor
				previous[neighbor] = curr_node

				# Add this neighbor to the priority queue
				heapq.heappush(queue, (distance, neighbor, transfers))

	# If we've exhausted all possible paths and haven't found the target,
	# return None to indicate that there is no path between the nodes
	return None

#------------------------------------------------------------------------------------------------------------------------------------------------------------

# A-Star algoritm which is Djikstra but with heuristic function
def aStarAlgo(startNode, endNode):
    # Unvisited is priority queue of nodes which has been visited but neighbors havent all been inspected
    unvisited = PriorityQueue()
    unvisited.put((0, startNode)) 
    
    # Set of nodes which has been visited and neighbors have been inspected
    visited = set([])

    # Store time from startNode to other nodes
    time = {}
    time[startNode] = 0

    # Store current node as parent to check edges
    previous = {}
    previous[startNode] = startNode

    # Store bus changes along the way
    previousBus = None
    busChanges = {}
    busChanges[startNode] = previousBus

    # Traverse through all nodes that hasnt been visited
    while not unvisited.empty():
        # Get neighbors of the current node with smallest f(n) value
        f, neighbour = unvisited.get()  

        # If node is endNode, goal reached and reverse path to show travel sequence
        if neighbour == endNode:
            tempPath = {}    
            busList = []
            stopList = []

            # Convert journet time in mins to hours, minutes and seconds 
            totalTime = getTimeFromHour(time[neighbour] / 60)

            # Take note of current and previous node to get route info and reverse the list
            while previous[neighbour] != neighbour:
                previousNode = previous[neighbour]
                previousBus = busChanges[neighbour]
                stopList.append(previousNode)

                if previousBus != None:
                    tempPath[str(previousNode) + "-" + str(neighbour)] = getBusFromBusID(previousBus)
                    busList.append(getBusFromBusID(previousBus))
                neighbour = previousNode

            # Reverse dictionary and print sequential steps
            reversedDict = {}
            stopList.reverse()
            #print("No | Stops      Bus")
            #print("------------------------")
            
            # Count stops and busIDs for bus changes
            for count, (key, value) in enumerate(reversed(tempPath.items()), start=1):                
                reversedDict[key] = str(value)

                # Print format to left align with 3 and 11 width counts
                #print(f"{count: <3}| {key: <11}{reversedDict[key]}")

            # Prints total duration of journey
            print("\nJourney time is estimated to be about {} hours {} minutes {} seconds".format(totalTime[0], totalTime[1], totalTime[2]))
            return busList, stopList

        # Add neighbour to visited because edges will be inspected
        visited.add(neighbour)

        # Iterate current node's neighbours
        for (node, weight, busID) in getNeighbours(neighbour, previousBus):
            # If any node not in visited set new time for it
            if node not in visited:
                newTime = time[neighbour] + weight

                if node not in time or newTime < time[node]:
                    time[node] = newTime
                    f = newTime + getHeuristic(node, endNode) 
                    previous[node] = neighbour
                    unvisited.put((f, node))
                    busChanges[node] = busID if previousBus != busID else busChanges[neighbour]

            previousBus = busID

    print("No path found")
    return None

# Method to get edgeTo nodes yet to be visited and its data given its currentNode. Eg. total time (waiting + travelling) and busID
def getNeighbours(currentNode, previousBus):
    # Returns a list of dictionaries that with each busstop details/schdules
    fastestBusList = get_fastest_bus_stop(currentNode)

    neighbours = []

    # Convert list of dictionaries into tuples to read multiple data at once
    for index in fastestBusList:
        busStopID = index['BusStopID']
        busID = index['BusID']
        weight = index['Duration']
        totalTime = index['Total']

        # Check if there is a bus change or not
        if previousBus != busID:
            neighbours.append((busStopID, totalTime, busID))
            
        else:
            neighbours.append((busStopID, weight, busID))

    # print("\nCurrent node: ", currentNode)
    # print("Current bus: ", previousBus)
    # print("\n", neighbours)

    # Return tuple with BusStopID[x], Time[x], BusID[x]
    return neighbours

# Method to get estimated time to endNode given its currentNode 
def getHeuristic(currentNode, endNode):
    # Get coordinates of both current and end stops
    currentNodeCoord = getCoordinatesOfBusStop(currentNode)
    endNodeCoord = getCoordinatesOfBusStop(endNode)
    
    # Filter into location1 and location2
    loc1 = currentNodeCoord[0][0], currentNodeCoord[0][1]
    loc2 = endNodeCoord[0][0], endNodeCoord[0][1]

    # Get Haversine/Euclidean distance of location1 and location2
    distance1 = hs.haversine(loc1, loc2)
    
    # Get estimated time in minutes between the 2 busstops. Time = Distance / Speed
    time = distance1 / bus_speed
    estimatedTime = getTimeFromHour(time)

    # Return heuristic time of currentNode in minutes
    return estimatedTime[1]

# Method to get time in hours, minutes and seconds given the hours in decimals 
def getTimeFromHour(time):
    totalSeconds = int(time * 3600)
    hours = totalSeconds // 3600
    minutes = (totalSeconds % 3600) // 60
    seconds = totalSeconds % 60
    timeList = [hours, minutes, seconds]
    return timeList

# Method to get coordinates of busstop given its busStopID
def getCoordinatesOfBusStop(busStopID):
    # Connection cursor
    connection = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_schema)
    cursor = connection.cursor()

    # Get latitude and longitude from BusStop table in DB
    query = "SELECT Latitude, Longitude FROM BusStop WHERE BusStopID = {}".format(busStopID)
    cursor.execute(query)
    result = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    # Return coordinates in list form [Latitude][Longitude]
    return result

# Method to get bus numbers given its busID
def getBusFromBusID(busID):
    # Initialise database connection
    connection = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_schema)
    cursor = connection.cursor()

    # Get busName from busID from Bus table in DB
    query = "SELECT Name FROM Bus WHERE BusID = {}".format(busID)
    cursor.execute(query)
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    # Return next fastest path
    return result[0]

#Store all BusStopID and corresponding names and coordinates into name_list 
def getBusStopNamesFromID():
    # Connection cursor
    connection = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_schema)
    cursor = connection.cursor()

    # Get BusStopID,Names,Latitude and longitude from BusStop table in DB
    query = "SELECT * FROM BusStop"
    cursor.execute(query)


    # Store the result set in a list
    result_set = []
    for row in cursor:
        result_set.append(row)

    # Close the cursor and connection
    cursor.close()
    connection.close()


    # Return coordinates in list form [Latitude][Longitude]
    return result_set

def getBusRouteDuration(total_distance):
    total_duration = total_distance / 70 * 60 * 60  # in seconds
    
    # Convert the total duration to hours, minutes, and seconds
    hours = int(total_duration // 3600)
    minutes = int((total_duration % 3600) // 60)
    seconds = int(total_duration % 60)

    duration = str(hours) + " hr " + str(minutes) + " min"
    # Print the total duration in the desired format
    print(f"Bus journey time is estimated to be about {hours} hours {minutes} minutes {seconds} seconds\n")
    return duration

def convertBusIDListToNameList(busIDList):
    busNameList = []
    for busID in busIDList:
        busName = getBusFromBusID(busID)
        busNameList.append(busName)
    return busNameList

#------------------------------------------------------------------------------------------------------------------------------------------------------------

# def mainTest(start, end, option):

#     # user_input = input("Select route method:\n1) Shortest time\n2) Shortest path \n")

#     if option == '1':
#         #If Shortest time in BusStopID
#         busName,pathID = aStarAlgo(start, end)


#     elif option == '2':
#         #If Shortest path in BusStopID
#         pathID,total_distance= shortest_path_with_min_transfers(start, end)
#         print(total_distance)

#     #Get the list of busStopID , names, lat , long from sql
#     ID_Name_Coordinates = getBusStopNamesFromID()
        
    
#     # Create a dictionary that maps each numeric ID to its corresponding name and coordinates
#     id_to_name_coordinates = {id_: (name, lat, long) for id_, name, lat, long in ID_Name_Coordinates}

#     # Convert the pathID list to a list of names and coordinates using the id_to_name_coordinates dictionary
#     path_names_coordinates = [id_to_name_coordinates[id_] for id_ in pathID]

#     # Extract the coordinates from the list of names and coordinates
#     path_coordinates = [(lat, long) for _, lat, long in path_names_coordinates]

#     # Print out Bus stop names and coordinates 
#     for name, bus in zip(path_names_coordinates, busName):
#         print(name[0], bus)
#         print()

    # return path_names_coordinates, path_coordinates


# start = int(input("Enter starting busStopID: "))
# end = int(input("Enter ending busStopID: "))
# user_input = input("\n1) Shortest time\n2) Shortest path \nSelect route method: ")
# mainTest(start, end, user_input)
