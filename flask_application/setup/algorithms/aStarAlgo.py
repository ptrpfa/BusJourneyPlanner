import mysql.connector
import haversine as hs
import pickle
import networkx as nx
import matplotlib.pyplot as plt

BUSSPEED = 70 #km/h  

connection = mysql.connector.connect(
    user = "root",
    password = "LKP_OOP_STRONG",
    host = "34.143.210.189",
    database = "DSA_JP"
)

# Generate graph to view weight and edges
def VisualiseGraph(multi_graph):
    # Create a layout for the nodes
    pos = nx.spring_layout(multi_graph)

    # Draw nodes and edges with labels
    nx.draw(multi_graph, pos, with_labels=True)

    # Get a dictionary of edge labels
    edge_labels = {}
    for (u, v, key, data) in multi_graph.edges(keys=True, data=True):
        route = data['route']
        weight = data['weight']
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

# Djikstra but with heuristic function
def aStarAlgo(startNode, endNode):
    # unvisited is list of nodes which has been visited but neighbors havent all been inspected
    unvisited = set([startNode])
    
    # visited is list of nodes which has been visited and neighbors have been inspected
    visited = set([])

    # Store time from startNode to other nodes, default value is infinity
    time = {}
    time[startNode] = 0

    # Store current node as parent then check edges
    previous = {}
    previous[startNode] = startNode

    # Traverse through all nodes that hasnt been visited
    while len(unvisited) > 0:
        # Checking the neighbors of the current node
        neighbour = None

        # Finding node with the lowest value of estimatedTotalTime(): shortestTime() + heuristicTime(), f(n) = g(n) + h(n)
        for count1 in unvisited:
            if neighbour == None or time[count1] + getHeuristic(count1, endNode) < time[neighbour] + getHeuristic(neighbour, endNode):
                neighbour = count1

        # If no more neighbours and is not endNode, no path found
        if neighbour == None:
            print("No path found")
            return None

        for (node, weight) in getNeighbours(neighbour):
            # If node is endNode, goal reached and reverse path to show travel seqeuence
            if neighbour == endNode:
                tempPath = {}
                totalTime = time[neighbour]

                # Take note of current and previous node to get route info and reverse the list
                while previous[neighbour] != neighbour:
                    u = previous[neighbour]
                    data = graph.get_edge_data(u, neighbour)
                    tempPath[str(u) + "-" + str(neighbour)] = data[0]['bus']
                    neighbour = u

                # Reverse the dictionary and template to display format
                reversedDict = {}
                count = 1
                print("No | Stops        (BusID)")
                print("--------------------------")
                count = 1
                for key, value in reversed(tempPath.items()):
                    reversedDict[key] = "BusID - " + str(value)
                    print(f"{count:<3}| {key:<12}({reversedDict[key]})")
                    count += 1

                # Prints path found and duration of journey
                print("\nJourney time in minutes:", totalTime)
                return tempPath

            # If current node not in both unvisited and visited set, add it to unvisited and note neighbour as its parent
            if node not in unvisited and node not in visited:
                unvisited.add(node)
                previous[node] = neighbour
                time[node] = time[neighbour] + weight

            # Otherwise, check if quicker to visit other neighbours first, then node
            # If yes, update parent data and time data and if the node was in the visited, move it to unvisited
            else:
                if time[node] > time[neighbour] + weight:
                    time[node] = time[neighbour] + weight
                    previous[node] = neighbour

                    if node in visited:
                        visited.remove(node)
                        unvisited.add(node)

        # Remove neighbour from unvisited and add to visited because edges already inspected
        unvisited.remove(neighbour)
        visited.add(neighbour)

    print("No path found")
    return None

# Returns edgeTo nodes yet to be visited and its data. eg. time and/or route
def getNeighbours(v):
    nextNodes = [(j, 
                 graph.get_edge_data(u, j, k)['weight']) for u in [v] for j in graph.neighbors(u) for k in graph[u][j]]

    # nextNodes = [(j, 
    #               graph.get_edge_data(u, j, k)['time'], 
    #               graph[u][j][k]['route']) for u in [v] for j in graph.neighbors(u) for k in graph[u][j]]

    return nextNodes

# Method to find the estimated time from currentNode to endNode 
def getHeuristic(currentNode, endNode):
    # Get coordinates of both bus stops
    currentNodeCoord = getCoordinatesOfBusStop(currentNode)
    endNodeCoord = getCoordinatesOfBusStop(endNode)
    
    # Filter them into location1 and location2
    loc1 = currentNodeCoord[0][0], currentNodeCoord[0][1]
    loc2 = endNodeCoord[0][0], endNodeCoord[0][1]

    # Get Haversine/Euclidean distance of location1 and location2
    distance1 = hs.haversine(loc1, loc2)
    
    # Get estimated time in minutes between the 2 busstops
    time = distance1 / BUSSPEED
    estimatedTime = convertHourToMinSec(time)

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
    query1 = "SELECT Latitude, Longitude FROM BusStop WHERE BusStopID = {}".format(busstopID)
    cursor = connection.cursor()
    cursor.execute(query1)
    result = cursor.fetchall()

    return result

# Method to pre-load graph
def load_pickle (filepath):
    # Create file object accessing the pickle file
    file_pickle = open (filepath, 'rb') # r = read, b = bytes

    # Get pickled object
    pickled_object = pickle.load (file_pickle)

    # Close file object
    file_pickle.close ()

    # Return pickle object
    return pickled_object


graph = load_pickle('flask_application/setup/graph.pkl')
# print(vars(graph))
# VisualiseGraph(graph)

currentBusStop = 1 #'A'
endBusStop = 40 #'F'

aStarAlgo(currentBusStop, endBusStop)

