import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import *
from queue import PriorityQueue

import mysql.connector
import haversine as hs
import networkx as nx
import matplotlib.pyplot as plt

# Initialise constant assumed speed
BUSSPEED = 70 #km/h  

# A-Star algoritm which is Djikstra but with heuristic function
def get_path(startNode, endNode):
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

# (NOT IN USE ANYMORE) Method to get and display graph with weight and edges
def VisualiseGraph(multiGraph):
    # Create a layout for the nodes
    pos = nx.spring_layout(multiGraph)

    # Draw nodes and edges with labels
    nx.draw(multiGraph, pos, with_labels=True)

    # Get a dictionary of edge labels
    edge_labels = {}
    for (u, v, key, data) in multiGraph.edges(keys=True, data=True):
        route = data['bus']
        weight = data['time']
        label = (route, weight)
        if (u, v) in edge_labels:
            edge_labels[(u, v)].append(label)
        else:
            edge_labels[(u, v)] = [label]

    # Draw edge labels
    for edge, labels in edge_labels.items():
        label = '\n'.join([f"{label[0]}: {label[1]}" for label in labels])
        nx.draw_networkx_edge_labels(multiGraph, pos, edge_labels={(edge[0], edge[1]): label})


    # Display the visualization and save to file
    # plt.savefig("amogus.jpg", format='jpg')
    plt.show()


# Current location and destination
# currentBusStop = 1
# endBusStop = 2

# aStarAlgo(currentBusStop, endBusStop)
