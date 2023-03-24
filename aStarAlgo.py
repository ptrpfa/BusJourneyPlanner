# import mysql.connector
# import haversine as hs
import networkx as nx
import matplotlib.pyplot as plt

BUSSPEED = 70 #km/h  

#Create a graph with nodes representing bus stops and edges representing bus routes
graph = nx.MultiDiGraph()
graph.add_edge('A', 'B', time=10, route='3')
graph.add_edge('A', 'C', time=12, route='4')
graph.add_edge('A', 'D', time=5, route='8')

graph.add_edge('B', 'A', time=10, route='3')
graph.add_edge('B', 'E', time=11, route='4')

graph.add_edge('C', 'A', time=12, route='3')
graph.add_edge('C', 'D', time=6, route='4')
graph.add_edge('C', 'E', time=11, route='8')
graph.add_edge('C', 'F', time=8, route='3')


graph.add_edge('D', 'A', time=5, route='3')
graph.add_edge('D', 'C', time=6, route='4')
graph.add_edge('D', 'F', time=14, route='8')

graph.add_edge('E', 'B', time=11, route='3')
graph.add_edge('E', 'C', time=1, route='4')

graph.add_edge('F', 'C', time=8, route='3')
graph.add_edge('F', 'D', time=14, route='4')

def VisualiseGraph(multi_graph):
    # Create a layout for the nodes
    pos = nx.spring_layout(multi_graph)

    # Draw nodes and edges with labels
    nx.draw(multi_graph, pos, with_labels=True)

    # Get a dictionary of edge labels
    edge_labels = {}
    for (u, v, key, data) in multi_graph.edges(keys=True, data=True):
        route = data['route']
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
    plt.savefig("amogus.jpg", format='jpg')
    plt.show()

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
        # For all neighbors of the current node
        for neighbour in graph.nodes():
            neighbour = None

            # Finding node with the lowest value of estimatedTotalTime(): shortestTime() + heuristicTime(), f(n) = g(n) + h(n)
            for count1 in unvisited:
                if (neighbour == None) or (time[count1] + getHeuristic(count1)) < (time[neighbour] + getHeuristic(count1)):
                    neighbour = count1;

            # If no more neighbours and is not endNode, no path found
            if neighbour == None:
                print("No path found")
                return None

            # If node is endNode, goal reached and reverse path to show travel seqeuence
            if neighbour == endNode:
                tempPath = []
                totalTime = time[neighbour]

                while previous[neighbour] != neighbour:
                    tempPath.append(neighbour)
                    neighbour = previous[neighbour]

                tempPath.append(startNode)
                tempPath.reverse()

                print("Path found: {}".format(tempPath))
                print("Total time taken in minutes:", totalTime)
                return tempPath

            for (node, weight) in getNeighbours(neighbour):
                # If current node not in both unvisited and visited set, add it to unvisited and note neighbour as its parent
                if node not in unvisited and node not in visited:
                    unvisited.add(node)
                    previous[node] = neighbour
                    time[node] = time[neighbour] + weight

                # Otherwise, check if quicker to visit other neighbours first, then node
                # If yes, update parent data and g data and if the node was in the visited, move it to unvisited
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

# Returns edgeTo nodes to visit
def getNeighbours(v):
    # print(graph.edges(v, data = "time"))
    nextNodes = [(j, graph.get_edge_data(u, j, k)['time']) for u in [v] for j in graph.successors(u) for k in graph[u][j]]
    return nextNodes

# Method to find the estimated time from currentNode to endNode 
def getHeuristic(v):
    H = {
        'A': 10,
        'B': 15,
        'C': 5,
        'D': 5,
        'E': 10,
        'F': 0,
    }

    # # Get coordinates of both bus stops
    # currentNodeCoord = getCoordinatesOfBusStop(currentNode)
    # endNodeCoord = getCoordinatesOfBusStop(endNode)
    
    # # Filter them into location1 and location2
    # loc1 = currentNodeCoord[0][0], currentNodeCoord[0][1]
    # loc2 = endNodeCoord[0][0], endNodeCoord[0][1]

    # # Get Haversine/Euclidean distance of location1 and location2
    # distance1 = hs.haversine(loc1, loc2)
    
    # # Get estimated time in minutes between the 2 busstops
    # time = distance1 / BUSSPEED
    # estimatedTime = convertHourToMinSec(time)

    return H[v]

# Method to convert time in hours to minutes
# def convertHourToMinSec(time):
#     totalSeconds = int(time * 3600)
#     # hours = totalSeconds // 3600
#     minutes = (totalSeconds % 3600) // 60
#     # seconds = totalSeconds % 60
#     return minutes

# # Method to get coordinates of busstop given its ID
# def getCoordinatesOfBusStop(busstopID):
#     query1 = "SELECT Latitude, Longitude FROM BusStop WHERE BusStopID = {}".format(busstopID)
#     cursor = connection.cursor()
#     cursor.execute(query1)
#     result = cursor.fetchall()

#     return result


# VisualiseGraph(graph)
aStarAlgo('A', 'F')
# currentBusStop = 67 
# endBusStop = 110
# aStarAlgo('67', '71')

