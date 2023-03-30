import networkx as nx
import pdb 
import matplotlib.pyplot as plt
import pydot
import heapq
from graphviz import Digraph
import pydot
import pickle 

def getData():
	# Open the pickled file in read binary mode
	data = None
	with open('flask_application/utils/Dataset/graph.pkl', 'rb') as f:
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

			return path_data

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

def validaeWithLib():
	graph = getData()

	#This the Python networtx lib to find shortest path
	path = nx.shortest_path(graph, 1, 5, weight='weight', method='dijkstra')

	shortest_path = {}
	distance = 0
	for i in range(len(path)-1):
		u, v = path[i], path[i+1]
		data = graph.get_edge_data(u, v)
		min_weight = min(value['weight'] for value in data.values())
		bus = next(sub_data['bus'] for sub_data in data.values() if sub_data['weight'] == min_weight)

		shortest_path[f"{u}-{v}"] = f"bus-{bus}, distance={min_weight}"
		distance += min_weight

	print(shortest_path)
	print(f"Shortest Distance: {distance}\n")

def mainTest(start, end):
	graph = getData()

	path_data = shortest_path_with_min_transfers(graph, start, end)

	print(path_data)

