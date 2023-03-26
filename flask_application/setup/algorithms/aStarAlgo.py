import mysql.connector
import haversine as hs
import pickle
import networkx as nx
import matplotlib.pyplot as plt

from queue import PriorityQueue

# Initialise constant assumed speed and connection to database
BUSSPEED = 70 #km/h  
connection = mysql.connector.connect(
    user = "root",
    password = "LKP_OOP_STRONG",
    host = "34.143.210.189",
    database = "DSA_JP"
)

# A-Star algoritm which is Djikstra but with heuristic function
def aStarAlgo(startNode, endNode):
    # Unvisited is priority queue of nodes which has been visited but neighbors havent all been inspected
    unvisited = PriorityQueue()
    unvisited.put((0, startNode))  # Priority is the shortestTime() + heuristicTime(), which is 0 for startNode
    
    # Set of nodes which has been visited and neighbors have been inspected
    visited = set([])

    # Store time from startNode to other nodes, default value is infinity
    time = {}
    time[startNode] = 0

    # Store current node as parent then check edges
    previous = {}
    previous[startNode] = startNode

    # Traverse through all nodes that hasnt been visited
    while not unvisited.empty():
        # Checking the neighbors of the current node and get node with smallest f(n) value
        f, neighbour = unvisited.get()  

        # If node is endNode, goal reached and reverse path to show travel sequence
        if neighbour == endNode:
            tempPath = {}            
            totalTime = time[neighbour]
            totalSeconds = int(totalTime * 60)
            minutes = (totalSeconds % 3600) // 60
            seconds = totalSeconds % 60

            # Take note of current and previous node to get route info and reverse the list
            while previous[neighbour] != neighbour:
                previousNode = previous[neighbour]
                data = graph.get_edge_data(previousNode, neighbour)
                tempPath[str(previousNode) + "-" + str(neighbour)] = data[0]['bus']
                neighbour = previousNode

            # Reverse dictionary and print sequential steps
            count = 0
            reversedDict = {}
            print("No | Stops        (BusID)")
            print("--------------------------")
            
            # Print counter, steps and bus taken
            for key, value in reversed(tempPath.items()):
                count += 1
                minutes += 2 # Assumes every stop is being held for average of 2 mins
                reversedDict[key] = "BusID - " + str(value)
                print(f"{count:<3}| {key:<12}({reversedDict[key]})")

            # Prints total duration of journey
            print("\nJourney time is estimated to be about {} minutes {} seconds".format(minutes, seconds))
            return tempPath

        # Add neighbour to visited because edges will be inspected
        visited.add(neighbour)

        for (node, weight) in getNeighbours(neighbour):
            # If current node not in both unvisited and visited set, add it to unvisited and note neighbour as its parent
            if node not in visited:
                newTime = time[neighbour] + weight

                if node not in time or newTime < time[node]:
                    time[node] = newTime
                    f = newTime + getHeuristic(node, endNode) 
                    previous[node] = neighbour
                    unvisited.put((f, node))

    print("No path found")
    return None

# Returns edgeTo nodes yet to be visited and its data. Eg. time and/or route
def getNeighbours(currentNode):
    nextNodes = [(j, 
                 graph.get_edge_data(u, j, k)['weight']) for u in [currentNode] for j in graph.neighbors(u) for k in graph[u][j]]

    # nextNodes = [(j, 
    #               graph.get_edge_data(u, j, k)['time'], 
    #               graph[u][j][k]['route']) for u in [v] for j in graph.neighbors(u) for k in graph[u][j]]

    return nextNodes

# Method to find the estimated time from currentNode to endNode 
def getHeuristic(currentNode, endNode):
    # Get coordinates of both current and end stops
    currentNodeCoord = getCoordinatesOfBusStop(currentNode)
    endNodeCoord = getCoordinatesOfBusStop(endNode)
    
    # Filter them into location1 and location2
    loc1 = currentNodeCoord[0][0], currentNodeCoord[0][1]
    loc2 = endNodeCoord[0][0], endNodeCoord[0][1]

    # Get Haversine/Euclidean distance of location1 and location2
    distance1 = hs.haversine(loc1, loc2)
    
    # Get estimated time in minutes between the 2 busstops. Time = Distance / Speed
    time = distance1 / BUSSPEED
    estimatedTime = convertHourToMinSec(time)

    # Return heuristic time of currentNode in minutes
    return estimatedTime

# Method to convert time in hours to minutes
def convertHourToMinSec(time):
    totalSeconds = int(time * 3600)
    # hours = totalSeconds // 3600
    minutes = (totalSeconds % 3600) // 60
    # seconds = totalSeconds % 60
    return minutes

# Method to get coordinates of busstop given its ID
def getCoordinatesOfBusStop(busstopID):
    # Query template to pull from DB
    query1 = "SELECT Latitude, Longitude FROM BusStop WHERE BusStopID = {}".format(busstopID)

    # Connection cursor
    cursor = connection.cursor()

    # Pull requested data which is coordinates of inputted busstopID
    cursor.execute(query1)
    result = cursor.fetchall()

    # Return coordinates in list form [Latitude][Longitude]
    return result

# Method to generate and display graph with weight and edges
def VisualiseGraph(multi_graph):
    # Create a layout for the nodes
    pos = nx.spring_layout(multi_graph)

    # Draw nodes and edges with labels
    nx.draw(multi_graph, pos, with_labels=True)

    # Get a dictionary of edge labels
    edge_labels = {}
    for (u, v, key, data) in multi_graph.edges(keys=True, data=True):
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
        nx.draw_networkx_edge_labels(multi_graph, pos, edge_labels={(edge[0], edge[1]): label})


    # Display the visualization and save to file
    # plt.savefig("amogus.jpg", format='jpg')
    plt.show()

# Method to pre-load graph
def loadPickle(filepath):
    # Create file object accessing the pickle file
    file_pickle = open(filepath, 'rb') # r = read, b = bytes

    # Get pickled object
    pickled_object = pickle.load(file_pickle)

    # Close file object
    file_pickle.close ()

    # Return pickle object
    return pickled_object

# Load map
graph = loadPickle('flask_application/setup/graph.pkl')
# print(vars(graph))
# VisualiseGraph(graph)

# Get user to input current location and destination
currentBusStop = 1
endBusStop = 5
aStarAlgo(currentBusStop, endBusStop)

