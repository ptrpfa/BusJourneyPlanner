from utils import *
from algorithms import aStarAlgo
from algorithms import dijkstra_Algo

# Function to get the coordinates of a given coordinate/address input
def process_inputs(address):
    # Initialise return variables
    coordinates = None
    error_msg = None

    # Check if input received are coordinates
    if(re.match('(\d+\.\d+)\s*,\s*(\d+\.\d+)', address)):
        # Get coordinates
        coordinates = [float(i.strip()) for i in address.split(",")]
        # Check if coordinates are wrong
        if(not validate_coordinates(*coordinates)):
            # Try swapping coordinates around to see if they are in the wrong order
            coordinates[0], coordinates[1] = coordinates[1], coordinates[0]
            # Check coordinates again
            if(not validate_coordinates(*coordinates)):
                coordinates = None
                error_msg = "Coordinates received are wrong."
    # Check for empty inputs
    elif(address == ""):
        error_msg = "Empty inputs! Please enter a valid input."
    else:
        # Get coordinates of address
        coordinates = get_coordinates(address)
        # Check if address received is valid
        if(coordinates is None):
            error_msg = "Please re-enter a valid address! Address received is invalid."

    # Return coordinates and error message, if any
    return coordinates, error_msg

# def process_data(start, destination):
#     option = '1'

#     # Fixed string for errors
#     error_header = "ERROR: "
#     invalid_input = None

#     """ Journey Planning """

#     # Step 2: Get nearest bus stop to starting coordinates
#     start_bus_stop = get_nearest_bus_stop(start_coordinates[0], start_coordinates[1])
#     print("Starting Bus Stop: ", start_bus_stop['StopID'], start_bus_stop['Name'])


#     # Step 4: Get nearest bus stop to ending coordinates
#     #start_bus_stop = {StopID, Name, Coordinate}
#     end_bus_stop = get_nearest_bus_stop(end_coordinates[0], end_coordinates[1])
#     print("Ending Bus Stop: ", end_bus_stop['StopID'], end_bus_stop['Name'])

#     # Check if start and end locations are the same
#     if(start_coordinates == end_coordinates): 
#         return error_header + "Both starting and ending locations are the same! No bus journey planning will be provided."
#     else:
#         #Step 5 Guide user to nearest bus stop => Error in Google AP
        
#         #Step 6 Find Shortest Path for bus to travel to end bus stop
#         busName, pathID = None, None
#         if option == '1':  #Shortest-Distance
#             pathID,total_distance,busName = dijkstra_Algo.shortest_path_with_min_transfers(start_bus_stop['StopID'],end_bus_stop['StopID'])
#             getBusRouteDuration(total_distance)
#             busName = convertBusIDListToNameList(busName)

#         #Get the list of [busStopID , names, lat , long] 
#         ID_Name_Coordinates = getBusStopNamesFromID()

#         # Create a dictionary that maps each numeric ID to its corresponding name and coordinates
#         id_to_name_coordinates = {id_: (name, lat, long) for id_, name, lat, long in ID_Name_Coordinates}

#         # Convert the pathID list to a list of names and coordinates using the id_to_name_coordinates dictionary
#         path_names_coordinates = [id_to_name_coordinates[id_] for id_ in pathID]

#         #Extract the coordinates from the list of names and coordinates
#         path_coordinates = [(lat, long) for _, lat, long in path_names_coordinates]

#         # Print out Bus stop names and coordinates 
#         for name, bus in zip(path_names_coordinates, busName):
#             print(name[0], ",", bus)
#             print()

#         if path_names_coordinates:

#             # Guide user to destination from end bus stop
#             if(end_bus_stop['Distance'] > 0):
#                 footer = "\nDirections to %s\n" % destination
#                 end_instructions = get_directions(end_bus_stop['Coordinates'], end_coordinates)

#                 return end_instructions