import networkx as nx
import pdb 
import matplotlib.pyplot as plt
import pydot
import heapq
from graphviz import Digraph
import pydot

def VisualiseGraph(multi_graph):
    """
    Visualize a MultiGraph using NetworkX and Matplotlib.
    
    Parameters:
    -----------
    multi_graph : networkx.MultiGraph
    The MultiGraph to visualize.
    """

    # create a layout for the nodes
    pos = nx.spring_layout(multi_graph)

    # draw nodes and edges with labels
    nx.draw(multi_graph, pos, with_labels=True)

    # get a dictionary of edge labels
    edge_labels = {}
    for (u, v, key, data) in multi_graph.edges(keys=True, data=True):
        route = data['route']
        weight = data['weight']
        label = (route, weight)
        if (u, v) in edge_labels:
            edge_labels[(u, v)].append(label)
        else:
            edge_labels[(u, v)] = [label]

    # draw edge labels
    for edge, labels in edge_labels.items():
        label = '\n'.join([f"{label[0]}: {label[1]}" for label in labels])
        nx.draw_networkx_edge_labels(multi_graph, pos, edge_labels={(edge[0], edge[1]): label})


    # display the visualization and save to file
    plt.savefig("spiderman.jpg", format='jpg')
    plt.show()

def shortest_path_with_min_transfers(graph, start, end):
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
			#Print the routes and the distance between each edge
			shortest_path = {}

			for i in range(len(path)-1):
			    u, v = path[i], path[i+1]
			    data = graph.get_edge_data(u, v)
			    min_weight = total_distance[v] - total_distance[u]
			    route = next(sub_data['route'] for sub_data in data.values() if sub_data['weight'] == min_weight)

			    shortest_path[f"{u}-{v}"] = f"route-{route}, distance={min_weight}"
			    distance += min_weight

			return shortest_path, total_distance[end]

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
			if previous[curr_node] is None or min_route_to_neighbor['route'] != min_route_to_prev_neighbor['route']:
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
	return None, None

#Create a graph with nodes representing bus stops and edges representing bus routes
graph = nx.MultiDiGraph()
graph.add_edge('A', 'B', weight=5, time=10, route='1')
graph.add_edge('A', 'C', weight=8, time=8, route='1')
graph.add_edge('A', 'C', weight=3, time=7, route='2')
graph.add_edge('B', 'D', weight=1, time=2, route='1')
graph.add_edge('C', 'D', weight=2, time=5, route='2')
graph.add_edge('D', 'E', weight=6, time=5, route='1')

graph.add_edge('D', 'F', weight=5, time=2, route='2')
graph.add_edge('D', 'F', weight=2, time=10, route='1')

graph.add_edge('E', 'F', weight=3, time=8, route='1')
graph.add_edge('F', 'G', weight=7, time=9, route='2')
graph.add_edge('G', 'H', weight=1, time=8, route='2')
graph.add_edge('F', 'H', weight=2, time=9, route='1')

#print("Library shortest path", nx.shortest_path(graph, 'A', 'C', weight='weight') )
path = nx.shortest_path(graph, 'A', 'G', weight='weight', method='dijkstra')
print(path)

shortest_path = {}
distance = 0
for i in range(len(path)-1):
    u, v = path[i], path[i+1]
    data = graph.get_edge_data(u, v)
    min_weight = min(value['weight'] for value in data.values())
    route = next(sub_data['route'] for sub_data in data.values() if sub_data['weight'] == min_weight)

    shortest_path[f"{u}-{v}"] = f"route-{route}, distance={min_weight}"
    distance += min_weight

print(shortest_path)
print(f"Shortest Distance: {distance}\n")

shortest_path_new, shortest_distance = shortest_path_with_min_transfers(graph, 'A', 'G')
print(shortest_path_new)
print(f"Shortest Distance: {shortest_distance}\n")

#VisualiseGraph(graph)
