from config import *
import re
import mysql.connector


# Function to validate a set of coordinates
def validate_coordinates(latitude, longitude):
    if(latitude >= -90 and latitude <= 90 and longitude >= -180 and longitude <= 180):
        return True
    else:
        return False

# Function to get a readable address from a set of coordinates (latitude & longitude)
def get_location(latitude, longitude):
    coordinates = (latitude, longitude)
    address = gmaps.reverse_geocode(coordinates)[0]['formatted_address']
    return address

# Function to get the approximate coordinates of a given address (inputs should be as unambiguous as possible for better accuracy)
def get_coordinates(location):
    coordinates = gmaps.geocode(location)
    # Check if a result was received
    if(coordinates):
        coordinates = coordinates[0]
        coordinates = (coordinates['geometry']['location']['lat'], coordinates ['geometry']['location']['lng'])
        return coordinates
    else:
        return None
    
# Function to get the nearest bus stop to a set of coordinates
def get_nearest_bus_stop(latitude, longitude):
    # Initialise database connection
    mysql_db = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_schema)
    db_cursor = mysql_db.cursor(buffered=True)

    # Get nearest bus stop
    nearest_bus_stop = None
    sql = "SELECT *, ST_Distance_Sphere(POINT(Longitude, Latitude), POINT(%s, %s)) / 1000 as Distance FROM BusStop ORDER BY Distance LIMIT 1;" % (longitude, latitude)
    db_cursor.execute(sql)
    for i in db_cursor:
        nearest_bus_stop = {'BusStopID': i[0], 'Name': i[1], 'Latitude': i[2], 'Longitude': i[3], 'Distance': i[4]}

    # Close connections
    db_cursor.close()
    mysql_db.close()

    # Return nearest bus stop
    return nearest_bus_stop

# from datetime import datetime
# # Request directions via public transit
# now = datetime.now()
# directions_result = gmaps.directions("Sydney Town Hall",
#                                      "Parramatta, NSW",
#                                      mode="transit",
#                                      departure_time=now)

# Program entrypoint
# Initialise variables
start = None
start_coordinates = None
start_bus_stop = None
end = None
end_coordinates = None
end_bus_stop = None

# Keep looping until a valid starting point is entered
while(True):
    # Get user's input
    user_input = input("Enter the starting location (address or coordinates): ")

    """ Input validation """
    # Coordinates received
    if(re.match('(\d+\.\d+)\s*,\s*(\d+\.\d+)', user_input)):
        # Get coordinates
        coordinates = [float(i.strip()) for i in user_input.split(",")]
        # Check if coordinates are wrong
        if(not validate_coordinates(*coordinates)):
            # Try swapping coordinates around to see if they are in the wrong order
            coordinates[0], coordinates[1] = coordinates[1], coordinates[0]
            # Check coordinates again
            if(not validate_coordinates(*coordinates)):
                print("Please re-enter a valid starting location! Coordinates received are wrong.")
            else:
                # Set starting values
                start_coordinates = coordinates
                start = get_location(*start_coordinates)
                start_bus_stop = get_nearest_bus_stop(*start_coordinates)
                # Break out of loop
                break
        else:
            # Set starting values
            start_coordinates = coordinates
            start = get_location(*start_coordinates)
            start_bus_stop = get_nearest_bus_stop(*start_coordinates)
            # Break out of loop
            break
    # Address received
    else:
        # Get starting coordinates
        coordinates = get_coordinates(user_input)
        # Check if address received is valid
        if(coordinates is None):
            print("Please re-enter a valid starting location! Address received is invalid.")
        else:
            # Set starting values
            start_coordinates = coordinates
            start = user_input
            start_bus_stop = get_nearest_bus_stop(*start_coordinates)
            # Break out of loop
            break

# Keep looping until a valid destination point is entered
while(True):
    # Get user's input
    user_input = input("Enter the destination location (address or coordinates): ")

    """ Input validation """
    # Coordinates received
    if(re.match('(\d+\.\d+)\s*,\s*(\d+\.\d+)', user_input)):
        # Get coordinates
        coordinates = [float(i.strip()) for i in user_input.split(",")]
        # Check if coordinates are wrong
        if(not validate_coordinates(*coordinates)):
            # Try swapping coordinates around to see if they are in the wrong order
            coordinates[0], coordinates[1] = coordinates[1], coordinates[0]
            # Check coordinates again
            if(not validate_coordinates(*coordinates)):
                print("Please re-enter a valid destination location! Coordinates received are wrong.")
            else:
                # Set destination values
                end_coordinates = coordinates
                end = get_location(*end_coordinates)
                end_bus_stop = get_nearest_bus_stop(*end_coordinates)
                # Break out of loop
                break
        else:
            # Set starting values
            end_coordinates = coordinates
            end = get_location(*end_coordinates)
            end_bus_stop = get_nearest_bus_stop(*end_coordinates)
            # Break out of loop
            break
    # Address received
    else:
        # Get starting coordinates
        coordinates = get_coordinates(user_input)
        # Check if address received is valid
        if(coordinates is None):
            print("Please re-enter a valid destination location! Address received is invalid.")
        else:
            # Set starting values
            end_coordinates = coordinates
            end = user_input
            end_bus_stop = get_nearest_bus_stop(*end_coordinates)
            # Break out of loop
            break

print("Starting Points:")
print("Address:", start)
print("Coordinates:", start_coordinates)
print("Nearest Bus Stop:", start_bus_stop)

print("\nEnding Points:")
print("Address:", end)
print("Coordinates:", end_coordinates)
print("Nearest Bus Stop:", end_bus_stop)
