import mysql.connector
import networkx as nx
import matplotlib.pyplot as plt
import pydot
from graphviz import Digraph
import pickle
import json


def DBQuery(query):
    # connect to the database
    cnx = mysql.connector.connect(
        host='34.143.210.189',
        user='root',
        password='LKP_OOP_STRONG',
        database='DSA_JP'
    )
    cursor = cnx.cursor()

    # Execute the query
    cursor.execute(query)

    #Fetch the results and add edges to the graph
    results = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    cnx.close()

    return results

def getGraph():
    # create the graph object
    graph = nx.MultiGraph()

    # Define the SELECT query
    query = """
        SELECT e.FromBusStopID, e.ToBusStopID, 
        CASE WHEN w.Type = 1 THEN w.Weight ELSE NULL END AS Distance, 
        CASE WHEN w.Type = 2 THEN w.Weight ELSE NULL END AS Time,
        br.BusID
        FROM Edge e
        JOIN Weight w ON e.EdgeID = w.EdgeID 
        JOIN BusRoute br ON e.RouteID = br.RouteID
        """
    #Get Results
    results = DBQuery(query)

    #Populate the edges
    for row in results:
        from_bus_stop_id = row[0] #FromBusStopID
        to_bus_stop_id = row[1] #ToBusStopID
        distance = row[2] #Distance
        time = row[3] #Time
        bus_id =  row[4] #BusID
        graph.add_edge(from_bus_stop_id, to_bus_stop_id, weight=distance, time=time, bus=bus_id)

    return graph

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

    # create a figure with a bigger size
    plt.figure(figsize=(30, 30))

    # draw nodes and edges with labels
    nx.draw(multi_graph, pos, with_labels=True)

    # get a dictionary of edge labels
    edge_labels = {}
    for (u, v, key, data) in multi_graph.edges(keys=True, data=True):
        bus_id = data['bus']
        weight = data['weight']
        label = (bus_id, weight)
        if (u, v) in edge_labels:
            edge_labels[(u, v)].append(label)
        else:
            edge_labels[(u, v)] = [label]

    # draw edge labels
    for edge, labels in edge_labels.items():
        label = '\n'.join([f"{label[0]}: {label[1]}" for label in labels])
        nx.draw_networkx_edge_labels(multi_graph, pos, edge_labels={(edge[0], edge[1]): label})


    # display the visualization and save to file
    # plt.savefig("spiderman.jpg", format='jpg')
    plt.show()


# Function to pickle object (accepts object to pickle and its filename to save as)
def pickle_object (pickle_object, filepath):
    # Create file object to store object to pickle
    file_pickle = open (filepath, 'wb') # w = write, b = bytes (overwrite pre-existing files if any)

    # Pickle (serialise) object [store object as a file]
    pickle.dump (pickle_object, file_pickle)

    # Close file object
    file_pickle.close ()


def schedule (bus_stop_id,bus_id):

    # Create a empty dictionary 
    schedule = {}

    # Define the SELECT query
    query2 = """
            SELECT 
            bs.BusStopID, 
            JSON_OBJECTAGG(br.BusID, (
                SELECT 
                CONCAT('[', GROUP_CONCAT(TIME_FORMAT(s.Time, '"%h:%i%p"')), ']')
                FROM 
                Schedule s
                WHERE 
                s.RouteID = br.RouteID
            )) AS Schedule
            FROM 
            BusStop bs
            LEFT JOIN BusRoute br ON bs.BusStopID = br.BusStopID
            GROUP BY 
            bs.BusStopID;
            """
    
    #Get Results 
    rows = DBQuery(query2)

    for row in rows:
        bus_stop_id = int(row[0])
        schedule[bus_stop_id] = {}
        schedule_json = row[1]
        if schedule_json:                                  # If the schedule JSON string is not `None`, parse it as a JSON object
            schedule_json = json.loads(schedule_json)
            for bus_id_str, times_json in schedule_json.items():            # Iterate over each bus ID and corresponding schedule times in the JSON object
                bus_id = int(bus_id_str)
                if isinstance(times_json, str):                     # If the schedule times are in string format, parse them as a JSON array
                    times = json.loads(times_json)
                else:
                    times = times_json
                schedule[bus_stop_id][bus_id] = times


    if bus_stop_id not in schedule:
        print(f"Bus stop ID {bus_stop_id} not found in schedule.")
    elif bus_id not in schedule[bus_stop_id]:
        print(f"Bus ID {bus_id} not found for bus stop ID {bus_stop_id}.")
    else:
        print(schedule[bus_stop_id][bus_id])

    return rows




#graph = getGraph()
#print(vars(graph))      # VisualiseGraph(graph)
#pickle_object(graph,'Dataset/graph.pkl')               # pickle object to file path

BusstopID= 160      # Example
BusID = 10          # Example 

schedule_obj = schedule(BusstopID,BusID)     

# Get schedule timing of the bus stop  use --->  schedule(BusstopID,BusID)
#bus_stop_id1 = {
#    "bus1": ["8:00am", "10:00am", "12:00pm"],
#    "bus2": ["9:00am", "11:00am", "1:00pm"],
#    "bus3": ["8:30am", "10:30am", "12:30pm"]},
#bus_stop_id2 = {
#    "bus1": ["8:00am", "10:00am", "12:00pm"],
#    "bus2": ["9:00am", "11:00am", "1:00pm"],
#    "bus3": ["8:30am", "10:30am", "12:30pm"]}

# Display the query
#for bus_stop_id, bus_stops in schedule.items():
#    for bus_id, times in bus_stops.items():
#        print(f"Bus stop ID: {bus_stop_id}, Bus ID: {bus_id}, Timing: {times}")

#pickle_object(schedule_obj, 'schedule.pkl')               # pickle object to file path 