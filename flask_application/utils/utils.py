from cloud_config import *
from setup import *
from bs4 import BeautifulSoup as bs_4
from email.mime.text import MIMEText            
from email.mime.multipart import MIMEMultipart  
from email.header import Header                 
from email.utils import formataddr    
from queue import PriorityQueue

import re
import mysql.connector
import datetime
import smtplib      
import pickle
import haversine as hs
import heapq

BUSSPEED = 70 #km/h  

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
    
def get_nearest_bus_stop(latitude, longitude):
    """
    Function to get the nearest bus stop to a set of coordinates

    """

    # Get nearest bus stop
    nearest_bus_stop = None
    sql = "SELECT *, ST_Distance_Sphere(POINT(Longitude, Latitude), POINT(%s, %s)) / 1000 as Distance FROM BusStop ORDER BY Distance LIMIT 1;" % (longitude, latitude)
    results = sql_query(sql)

    for i in results:
        nearest_bus_stop = {'StopID': i[0], 'Name': i[1], 'Latitude': i[2], 'Longitude': i[3], 'Coordinates': [i[2], i[3]], 'Distance': i[4]}

    # Return nearest bus stop
    return nearest_bus_stop

# Function to get fastest bus stop, taking into account the duration from the starting bus stop to the next bus stop, as well as the next available bus
def get_fastest_bus_stop(start_bus_stop_id):
    # Initialise database connection
    mysql_db = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_schema)
    db_cursor = mysql_db.cursor(buffered=True)

    # Get list of nearest bus stops, in ascending order (fastest one in lower index)
    bus_stops = []
    sql = "SELECT Edge.*, Bus.BusID, Bus.Name, Schedule.Time AS Time, Weight.Weight As Duration, TIMESTAMPDIFF(SECOND, CURRENT_TIME(), Time) / 60 AS Waiting_Time, (Weight.Weight + (TIMESTAMPDIFF(SECOND, CURRENT_TIME(), Time) / 60)) AS Total_Time FROM Edge JOIN BusRoute ON Edge.RouteID = BusRoute.RouteID  JOIN Bus ON BusRoute.BusID = Bus.BusID JOIN Weight ON Edge.EdgeID = Weight.EdgeID  JOIN Schedule ON BusRoute.RouteID = Schedule.RouteID  WHERE Edge.FromBusStopID = %s AND Weight.Type = 2 AND Time >= CURRENT_TIME() ORDER BY Total_Time ASC;" % start_bus_stop_id
    db_cursor.execute(sql)
    for i in db_cursor:
        # Parse each row
        schedule_time = datetime.datetime.min + i[6]
        bus_stop = {'EdgeID': i[0], 'BusStopID': i[2], 'BusID': i[4], 'Bus': i[5], 'NextBus': schedule_time, 'Duration': i[7], 'Wait': float(i[8]), 'Total': i[9]}
        # Get BusID
        bus_stops.append(bus_stop)

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
    
#------------------------------------------------------------------------------------------------------------------------------------------------------------

def getData():
	# Open the pickled file in read binary mode
	data = None
	with open('C:/Users/Jeffr/Desktop/123/flask_application/utils/graph.pkl', 'rb') as f:
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

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

            # Convert journet time in mins to hours, minutes and seconds 
            totalTime = getTimeFromHour(time[neighbour] / 60)

            # Take note of current and previous node to get route info and reverse the list
            while previous[neighbour] != neighbour:
                previousNode = previous[neighbour]
                previousBus = busChanges[neighbour]

                if previousBus != None:
                    tempPath[str(previousNode) + "-" + str(neighbour)] = getBusFromBusID(previousBus)
                neighbour = previousNode

            # Reverse dictionary and print sequential steps
            reversedDict = {}
            print("No | Stops      Bus")
            print("------------------------")
            
            # Count stops and busIDs for bus changes
            for count, (key, value) in enumerate(reversed(tempPath.items()), start=1):                
                reversedDict[key] = str(value)

                # Print format to left align with 3 and 11 width counts
                print(f"{count: <3}| {key: <11}{reversedDict[key]}")

            # Prints total duration of journey
            print("\nJourney time is estimated to be about {} hours {} minutes {} seconds".format(totalTime[0], totalTime[1], totalTime[2]))
            return tempPath

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
    time = distance1 / BUSSPEED
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

def mainTest(start, end, option):

    # user_input = input("Select route method:\n1) Shortest time\n2) Shortest path \n")

    if option == '1':
        #If Shortest time in BusStopID
        pathID = aStarAlgo(start, end)

    elif option == '2':
        #If Shortest path in BusStopID
        pathID,total_distance= shortest_path_with_min_transfers(start, end)
    
    
    #Store all BusStopID and corresponding names and coordinates into name_list  
    ID_Name_Coordinates = load_pickle('pickles/BusStopIDNamesLatLong.pkl')
    
    # Create a dictionary that maps each numeric ID to its corresponding name and coordinates
    id_to_name_coordinates = {id_: (name, lat, long) for id_, name, lat, long in ID_Name_Coordinates}

    # Convert the pathID list to a list of names and coordinates using the id_to_name_coordinates dictionary
    path_names_coordinates = [id_to_name_coordinates[id_] for id_ in pathID]

    # Extract the coordinates from the list of names and coordinates
    path_coordinates = [(lat, long) for _, lat, long in path_names_coordinates]

    # Print out Bus stop names and coordinates 
    for name in path_names_coordinates:
        print(name)
        print()

    return path_names_coordinates, path_coordinates
         

start = int(input("Enter starting busStopID: "))
end = int(input("Enter ending busStopID: "))
user_input = input("\n1) Shortest time\n2) Shortest path \nSelect route method: ")
mainTest(start, end, user_input)
