from mapping import *
from utils import *
from algorithms import dijkstra_Algo
from algorithms import *



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
                
def process_data(start, destination, option):

    # Fixed string for errors
    error_header = "ERROR: "
    invalid_input = None

    """ Journey Planning """
    # Step 1: Get starting coordinates of user
    start_coordinates, invalid_input = process_inputs(start)
    # Check for invalid inputs
    if(invalid_input):
        return error_header + invalid_input

    # Step 2: Get nearest bus stop to starting coordinates
    start_bus_stop = get_nearest_bus_stop(start_coordinates[0], start_coordinates[1])
    print("Starting Bus Stop: ", start_bus_stop['StopID'], start_bus_stop['Name'])

    # Step 3: Get ending coordinates of user 
    end_coordinates, invalid_input = process_inputs(destination)
    # Check for invalid inputs
    if(invalid_input):
        return error_header + invalid_input

    # Step 4: Get nearest bus stop to ending coordinates
    #start_bus_stop = {StopID, Name, Coordinate}
    end_bus_stop = get_nearest_bus_stop(end_coordinates[0], end_coordinates[1])
    print("Ending Bus Stop: ", end_bus_stop['StopID'], end_bus_stop['Name'])

    # Check if start and end locations are the same
    if(start_coordinates == end_coordinates): 
        return error_header + "Both starting and ending locations are the same! No bus journey planning will be provided."
    else:
        #Step 5 Guide user to nearest bus stop => Error in Google AP
        
        #Step 6 Find Shortest Path for bus to travel to end bus stop

        if option == '1':  #Shortest-Distance
            pathID,total_distance,busName = dijkstra_Algo.shortest_path_with_min_transfers(start_bus_stop['StopID'],end_bus_stop['StopID'])
            getBusRouteDuration(total_distance)
            busName = convertBusIDListToNameList(busName)
            
        elif option == '2': #Shortest-Time
            busName, pathID = aStarAlgo(start_bus_stop['StopID'],end_bus_stop['StopID'])
            
        else:
            print("Error in Options")


        #Get the list of [busStopID , names, lat , long] 
        ID_Name_Coordinates = getBusStopNamesFromID()

        # Create a dictionary that maps each numeric ID to its corresponding name and coordinates
        id_to_name_coordinates = {id_: (name, lat, long) for id_, name, lat, long in ID_Name_Coordinates}

        # Convert the pathID list to a list of names and coordinates using the id_to_name_coordinates dictionary
        path_names_coordinates = [id_to_name_coordinates[id_] for id_ in pathID]

        #this is the list for the routes
        print(path_names_coordinates)
        process_routes()
        #Extract the coordinates from the list of names and coordinates
        path_coordinates = [(lat, long) for _, lat, long in path_names_coordinates]

        # Print out Bus stop names and coordinates 
        for name, bus in zip(path_names_coordinates, busName):
            print(name[0], ",", bus)
            print()

        if path_names_coordinates:
            
            map_html = generateUserMap(path_names_coordinates, start_coordinates, end_coordinates,start_bus_stop,end_bus_stop)

            # Guide user to destination from end bus stop
            if(end_bus_stop['Distance'] > 0):
                footer = "\nDirections to %s\n" % destination
                end_instructions = get_directions(end_bus_stop['Coordinates'], end_coordinates)
                # Print guiding instructions
                print(footer) 
                print(end_instructions)

            return map_html

    def process_routes():
        ID_Name = getBusStopNamesFromID()

        # Create a dictionary that maps each numeric ID to its corresponding name and coordinates
        id_to_name = {id_: (name) for id_, name in ID_Name}

        # Convert the pathID list to a list of names and coordinates using the id_to_name_coordinates dictionary
        path_names = [id_to_name[id_] for id_ in pathID]
        path_string = ""
        for item in path_names:
            path_string += str(item[0]) + ";"
            #remove last semicolon from string
            path_string = path_string[:-1]
            
        return path_string

    

        # Check for email notification
        # user_input = input("\nDo you want a copy of these directions sent to your email? (Yes or No): ")
        # if(user_input.lower() == "yes"):
        #     user_email = input("Enter your email address: ")
        #     # Send email
        #     email_subject = "Directions from %s to %s" % (start_address, end_address)
        #     email_message = header + start_instructions + footer + end_instructions
        #     email_message = email_message.replace("\n", "<br>")
        #     if(send_email(user_email, email_subject, email_message)):
        #         print("Email sent to", user_email, "!")

                                           

# for testing 
# start = 'Larkin Terminal'
# end = 'Hospital Sultanah Aminah'
# user_input = '1'
# process_data(start, end, user_input)
