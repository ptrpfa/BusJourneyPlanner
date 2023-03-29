from utils.mapping import *
from utils.utils import * 
from utils.algorithms import aStarAlgo
#from utils.alogrithms import aStarAlgo


def process_data(start, destination, option):

    """ Journey Planning """
    # Step 1: Get starting coordinates of user
    start_coordinates = get_coordinates(start)

    # Step 2: Get nearest bus stop to starting coordinates
    #start_bus_stop = {StopID, Name, Coordinate}
    start_bus_stop = get_nearest_bus_stop(start_coordinates[0], start_coordinates[1])
    print("Starting Bus Stop: ", start_bus_stop['StopID'], start_bus_stop['Name'])

    # Step 3: Get ending coordinates of user 
    end_coordinates = get_coordinates(destination)

    # Step 4: Get nearest bus stop to ending coordinates
    #start_bus_stop = {StopID, Name, Coordinate}
    end_bus_stop = get_nearest_bus_stop(end_coordinates[0], end_coordinates[1])
    print("Ending Bus Stop: ", end_bus_stop['StopID'], end_bus_stop['Name'])

    # Check if start and end locations are the same
    if(start_coordinates == end_coordinates): 
        print("Both starting and ending locations are the same! No bus journey planning will be provided.")
    else:
        # Guide user to starting bus stop
        if(start_bus_stop['Distance'] > 0):
            header = "\nHead to Bus Stop %s (%s)\n" % (start_bus_stop['StopID'], start_bus_stop['Name'])
            start_instructions = get_directions(start_coordinates, start_bus_stop['Coordinates'])
            # Print guiding instructions
            print(header)
            print(start_instructions)
        
            # Assumption: User will always take the bus, regardless of the distance between the start and end locations, unless both points are the same
            # Get bus route plan
            print("\n", "-" * 20)
            print("\n*" * 3)
            print("\n\nBUS ROUTE\n\n")
            print("\n*" * 3)
            print("\n", "-" * 20)
    
            #Main Test in util
            if option == '1':
                #If Shortest time in BusStopID
                busName,pathID = aStarAlgo(start_bus_stop['StopID'],end_bus_stop['StopID'])
                
                #start_bus_stop['StopID']

            elif option == '2':
                """
                Maintenace
                """
                #If Shortest path in BusStopID
                # pathID,total_distance= shortest_path_with_min_transfers(start, destination)
                # total_duration = total_distance / BUSSPEED * 60 * 60  # in seconds

                # # Convert the total duration to hours, minutes, and seconds
                # hours = int(total_duration // 3600)
                # minutes = int((total_duration % 3600) // 60)
                # seconds = int(total_duration % 60)

                # # Print the total duration in the desired format
                # print(f"Bus journey time is estimated to be about {hours} hours {minutes} minutes {seconds} seconds\n")

            # #Get the list of busStopID , names, lat , long from sql
            # ID_Name_Coordinates = getBusStopNamesFromID()
        
    
            # # Create a dictionary that maps each numeric ID to its corresponding name and coordinates
            # id_to_name_coordinates = {id_: (name, lat, long) for id_, name, lat, long in ID_Name_Coordinates}

            # # Convert the pathID list to a list of names and coordinates using the id_to_name_coordinates dictionary
            # path_names_coordinates = [id_to_name_coordinates[id_] for id_ in pathID]

            # Extract the coordinates from the list of names and coordinates
            #path_coordinates = [(lat, long) for _, lat, long in path_names_coordinates]

            # # Print out Bus stop names and coordinates 
            # for name, bus in zip(path_names_coordinates, busName):
            #     print(name[0], bus)
            #     print()

            # Plot bus stops and route on map
            if path_names_coordinates:
                map_html = generateUserMap(path_names_coordinates, start_coordinates, end_coordinates,start_bus_stop,end_bus_stop)

                # # Guide user to destination from end bus stop
                # if(end_bus_stop['Distance'] > 0):
                #     footer = "\nDirections to %s\n" % destination
                #     end_instructions = get_directions(end_bus_stop['Coordinates'], end_coordinates)
                #     # Print guiding instructions
                #     print(footer) 
                #     print(end_instructions)

                return map_html
























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


# def process_data():
#     # Get the input data from the request
#     start_address = request.form.get("Start")
#     end_address = request.form.get("Destination")
#     option = request.form.get("Option")

#     """ Journey Planning """

#     # Step 1: Get starting coordinates
#     #start_address = "Larkin Terminal"
#     start_coordinates = get_coordinates(start_address)

#     # Step 2: Get nearest bus stop to starting coordinates
#     start_bus_stop = get_nearest_bus_stop(start_coordinates[0], start_coordinates[1])
#     print("Starting Bus Stop: ", start_bus_stop['StopID'], start_bus_stop['Name'])
        
#     # Step 3: Get ending coordinates
#     #end_address = "Polilkinik Yap"
#     end_coordinates = get_coordinates(end_address)

#     # Step 4: Get nearest bus stop to ending coordinates
#     end_bus_stop = get_nearest_bus_stop(end_coordinates[0], end_coordinates[1])
#     print("Ending Bus Stop: ", end_bus_stop['StopID'], end_bus_stop['Name'])

#     # Check if start and end locations are the same
#     if(start_coordinates == end_coordinates): 
#         print("Both starting and ending locations are the same! No bus journey planning will be provided.")
#     else:
#         # Guide user to starting bus stop
#         if(start_bus_stop['Distance'] > 0):
#             header = "\nHead to Bus Stop %s (%s)\n" % (start_bus_stop['StopID'], start_bus_stop['Name'])
#             start_instructions = get_directions(start_coordinates, start_bus_stop['Coordinates'])
#             # Print guiding instructions
#             print(header)
#             print(start_instructions)
        
#         # Assumption: User will always take the bus, regardless of the distance between the start and end locations, unless both points are the same
#         # Get bus route plan
#         print("\n", "-" * 20)
#         print("\n*" * 3)
#         print("\n\nBUS ROUTE\n\n")
#         path_names_coordinates, path_coordinates = mainTest(start_bus_stop['StopID'], end_bus_stop['StopID'], option)
#         print("\n*" * 3)
#         print("\n", "-" * 20)

#         # Plot bus stops and route on map
#         if path_names_coordinates:
#             map = folium.Map(location=start_coordinates, zoom_start=13)

#             # Add markers for starting and ending locations
#             folium.Marker(start_coordinates, popup='Starting Location').add_to(map)
#             folium.Marker(end_coordinates, popup='Ending Location').add_to(map)

#             # Add markers for all locations on the path
#             for location in path_names_coordinates:
#                 name = location[0]
#                 coordinates = location[1:]
#                 if coordinates is not None:
#                     folium.Marker(coordinates, popup=name).add_to(map)

#             # Generate the Google Maps API request for the walking path from the starting location to the first stop
#             origin = f'{start_coordinates[0]},{start_coordinates[1]}'
#             destination = f'{start_bus_stop["Latitude"]},{start_bus_stop["Longitude"]}'
#             url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=walking&key={API_KEY}'
#             response = requests.get(url)
#             route = response.json()['routes'][0]['overview_polyline']['points']

#             # Decode the polyline into a list of latitude and longitude coordinates
#             decoded_route = polyline.decode(route)

#             # Add polyline to map
#             folium.PolyLine(locations=decoded_route, color='red').add_to(map)

#             # Generate the Google Maps API request for the walking path from the last stop to the destination
#             origin = f'{end_bus_stop["Latitude"]},{end_bus_stop["Longitude"]}'
#             destination = f'{end_coordinates[0]},{end_coordinates[1]}'
#             url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&mode=walking&key={API_KEY}'
#             response = requests.get(url)
#             route = response.json()['routes'][0]['overview_polyline']['points']

#             # Decode the polyline into a list of latitude and longitude coordinates
#             decoded_route = polyline.decode(route)

#             # Add polyline to map
#             folium.PolyLine(locations=decoded_route, color='red').add_to(map)

#             # Generate the Google Maps API request for the route between stops
#             stops = [location[1:] for location in path_names_coordinates if location[1:] is not None]
#             origin = f'{stops[0][0]},{stops[0][1]}'
#             destination = f'{stops[-1][0]},{stops[-1][1]}'
#             waypoints = '|'.join([f'{stop[0]},{stop[1]}' for stop in stops[1:]])
#             url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&waypoints={waypoints}&mode=driving&key={API_KEY}'
#             response = requests.get(url)
#             route = response.json()['routes'][0]['overview_polyline']['points']

#             # Decode the polyline into a list of latitude and longitude coordinates
#             decoded_route = polyline.decode(route)

#             # Add polyline to map
#             folium.PolyLine(locations=decoded_route, color='blue').add_to(map)

#             # Save map to HTML file
#             map.save('C:/Users/Jeffr/Desktop/123/flask_application/utils/map.html')

#         map_html = map._repr_html_()

#         # Guide user to destination from end bus stop
#         if(end_bus_stop['Distance'] > 0):
#             footer = "\nDirections to %s\n" % end_address
#             end_instructions = get_directions(end_bus_stop['Coordinates'], end_coordinates)
#             # Print guiding instructions
#             print(footer) 
#             print(end_instructions)

#         # Check for email notification
#         user_input = input("\nDo you want a copy of these directions sent to your email? (Yes or No): ")
#         if(user_input.lower() == "yes"):
#             user_email = input("Enter your email address: ")
#             # Send email
#             email_subject = "Directions from %s to %s" % (start_address, end_address)
#             email_message = header + start_instructions + footer + end_instructions
#             email_message = email_message.replace("\n", "<br>")
#             if(send_email(user_email, email_subject, email_message)):
#                 print("Email sent to", user_email, "!")



#     # Return the processed data as a string
#     return map_html


# if __name__ == '__main__':
#     app.run(host="localhost", port=8080, debug=True)                                                                         


# start = 'Larkin Terminal'
# end = 'Hospital Sultanah Aminah'
# user_input = '1'
# process_data(start, end, user_input)
