from cloud_config import *
from setup import *

from bs4 import BeautifulSoup as bs_4
from email.mime.text import MIMEText            
from email.mime.multipart import MIMEMultipart  
from email.header import Header                 
from email.utils import formataddr    
from queue import PriorityQueue
from pathlib import Path

import re
import mysql.connector
import datetime
import smtplib      
import pickle
import haversine as hs
import heapq
import requests
import math
import json

def save_file(text, file_name):
    """
    Function to write to a file
    """
    with open(file_name, 'w') as f:
        f.write(text)

def check_file_exists(file_path):
    """
    Function to check if a particular file exists
    """
    return Path(file_path).exists()

def pickle_object (pickle_object, filepath):
    """ 
    Function for pickling an object
    """
    # Create file object to store object to pickle
    file_pickle = open (filepath, 'wb') # w = write, b = bytes (overwrite pre-existing files if any)

    # Pickle (serialise) object [store object as a file]
    pickle.dump (pickle_object, file_pickle)

    # Close file object
    file_pickle.close ()

def load_pickle (filepath):
    """
    Function for de-pickling an object
    """
    # Create file object accessing the pickle file
    file_pickle = open (filepath, 'rb') # r = read, b = bytes

    # Get pickled object
    pickled_object = pickle.load (file_pickle)

    # Close file object
    file_pickle.close ()

    # Return pickle object
    return pickled_object

def validate_coordinates(latitude, longitude):
    """
    Function to validate a set of coordinates

    """

    if(latitude >= -90 and latitude <= 90 and longitude >= -180 and longitude <= 180):
        return True
    else:
        return False

def get_location(latitude, longitude):
    """
    Function to get a readable address from a set of coordinates

    """

    coordinates = (latitude, longitude)
    address = gmaps.reverse_geocode(coordinates)[0]['formatted_address']
    return address

def get_coordinates(location):
    """
    Function to get the approximate coordinates of a given address
    Note: inputs should be as unambiguous as possible for better accuracy

    """

    coordinates = gmaps.geocode(location)
    # Check if a result was received
    if(coordinates):
        coordinates = coordinates[0]
        coordinates = (coordinates['geometry']['location']['lat'], coordinates ['geometry']['location']['lng'])
        return coordinates
    else:
        return None
    
def get_nearest_bus_stop(latitude, longitude, limit=True): # Weight: Distance
    """
    Function to get the nearest bus stop to a set of coordinates

    """
    if(limit):
        # Get nearest bus stop
        nearest_bus_stop = None
        sql = "SELECT *, ST_Distance_Sphere(POINT(Longitude, Latitude), POINT(%s, %s)) / 1000 as Distance FROM BusStop ORDER BY Distance LIMIT 1;" % (longitude, latitude)
        results = sql_query(sql)

        for i in results:
            nearest_bus_stop = {'StopID': i[0], 'Name': i[1], 'Latitude': i[2], 'Longitude': i[3], 'Coordinates': [i[2], i[3]], 'Distance': i[4]}
    else:
        # Get nearest bus stop
        nearest_bus_stop = []
        sql = "SELECT *, ST_Distance_Sphere(POINT(Longitude, Latitude), POINT(%s, %s)) / 1000 as Distance FROM BusStop ORDER BY Distance;" % (longitude, latitude)
        results = sql_query(sql)

        for i in results:
            current_bus_stop = {'StopID': i[0], 'Name': i[1], 'Latitude': i[2], 'Longitude': i[3], 'Coordinates': [i[2], i[3]], 'Distance': i[4]}
            nearest_bus_stop.append(current_bus_stop)

    # Return nearest bus stop
    return nearest_bus_stop

def get_bearing(lat1, long1, lat2, long2):
    """
    Function to calculate the bearing between two given coordinates
    From: (lat1, long1)
    To: (lat2, long2)
    """
    # Convert latitude and longitude to radians
    lat1 = math.radians(lat1)
    long1 = math.radians(long1)
    lat2 = math.radians(lat2)
    long2 = math.radians(long2)

    # Calculate the bearing
    bearing = math.degrees(math.atan2(math.sin(long2 - long1) * math.cos(lat2), math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(long2 - long1)))

    # Ensure bearing is positive
    bearing = (bearing + 360) % 360

    # Return bearing
    return bearing

def get_live_bus():
    """ 
    Function to get live bus data from PAJ's API, function will add new bus arrival timings into the Schedule table 
    and return a list of the respective ScheduleIDs that have been added. These temporary rows will be required to be removed in later parts of the program.
    """
    # Initialise list of scheduleIDs that have been added by this function
    list_schedules = []

    # Initialise list of live buses
    list_buses = []

    # API endpoint and key
    headers = {'api-key': paj_api_key}

    # Check if live bus data JSON file exists
    if(not check_file_exists(file_live_bus)):
        # Make API request to get bus data only if the file does not exist (calling of PAJ API left to mapping functions)
        live_bus = requests.get(paj_api_live_bus, headers=headers, verify=True)
        # Save file
        save_file(live_bus.text, file_live_bus)
        live_bus = live_bus.json()['data']
    else:
        # Load bus data from JSON file directly
        live_bus = json.load(open(file_live_bus))
        live_bus = live_bus['data']

    # Parse API data
    for bus in live_bus:
        # Check bus service and moving buses
        if((bus['route'][0] in loop_buses + one_way_buses) and bus['speed'] > 0):
            current_bus = {'Bus': bus['route'][0], 'BusPlate': bus['bus'], 'Datetime': datetime.datetime.strptime(bus['timestamp'], '%Y-%m-%d %H:%M:%S'), 
                           'Latitude': bus['latitude'], 'Longitude': bus['longitude'], 'Coordinates': [bus['latitude'], bus['longitude']], 'Speed': bus['speed'], 'Bearing': bus['bearing']}
            list_buses.append(current_bus)

    # Initialise database connection
    mysql_db = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_schema)
    db_cursor = mysql_db.cursor(buffered=True)

    # Get max scheduleID from database
    max_sql = "SELECT MAX(ScheduleID) FROM Schedule;"
    db_cursor.execute(max_sql)
    schedule_id = db_cursor.fetchall()[0][0] + 1

    # Loop through each bus to determine the bus stop that the bus is heading towards
    for bus in list_buses:
        # Initialise target bus stop
        target_bus_stop = None
        # Initialise routeID
        route_id = None
        # Initialise list of potential bus stops that the bus is heading to
        list_bus_stops = []
        # Get the distance between the bus and all other bus stops in the database (list returned will be sorted in ascending order, according to the distance between the bus stop and the bus)
        bus_stops = get_nearest_bus_stop(bus['Latitude'], bus['Longitude'], False)

        # Loop through each bus stop
        for bus_stop in bus_stops:
            # Calculate the bearing between the bus to the current bus stop (order matters)
            bus_stop['Bearing'] = abs(bus['Bearing'] - get_bearing(bus['Latitude'], bus['Longitude'], bus_stop['Latitude'], bus_stop['Longitude']))
            # Add bus stop to list of potential bus stops if its bearing is within 45 degrees of the bus's current bearing 
            if(abs(bus_stop['Bearing']) <= bearing_threshhold):    # Bus is assumed to be headed towards the bus stop if its bearing is within the specified threshold
                list_bus_stops.append(bus_stop)

        # Loop through each potential bus stop
        for bus_stop in list_bus_stops:
            # Check if an edge exists between the bus to the bus stop
            # Limitation: We are unable to distinguish which one-way bus service is being used currently (direction 1 or 2), queries for one-way buses might be wrong
            sql = "SELECT Edge.*, BusRoute.BusID, Bus.Name FROM Edge JOIN BusRoute ON Edge.RouteID = BusRoute.RouteID JOIN Bus ON BusRoute.BusID = Bus.BusID WHERE Edge.ToBusStopID = %s AND Bus.Name LIKE \"%%%s%%\";" % (bus_stop['StopID'], bus['Bus'])
            db_cursor.execute(sql)
            # Get first matching bus stop to be the target bus stop (current list of bus stops is already implicitly sorted according to its distance from the bus, lower index = closer to bus)
            if(db_cursor.rowcount):
                # Set target bus stop to be the first match
                target_bus_stop = bus_stop
                # Get RouteID
                route_id = db_cursor.fetchall()[0][3]
                # Break out of loop
                break

        # Check for a matching bus stop
        if(target_bus_stop and route_id):
            # Calculate duration (in minutes)
            duration = (target_bus_stop['Distance'] / bus['Speed']) * 60
            # Get estimated time of bus arrival
            arrival_time = datetime.timedelta(minutes=duration) + datetime.datetime.now()
            # Add new bus schedule into the database
            insert_sql = "INSERT INTO Schedule VALUES (%s, %s, \"%s\");" % (schedule_id, route_id, arrival_time.time())
            db_cursor.execute(insert_sql)
            # Add scheduleID into list of temporarily created bus schedules
            list_schedules.append(schedule_id)
            # Update scheduleID
            schedule_id += 1

    # Effect changes
    mysql_db.commit()
                
    # Close connections
    db_cursor.close()
    mysql_db.close()

    # Return list of scheduleIDs that have been added
    return list_schedules

def get_fastest_bus_stop(start_bus_stop_id): # Weight: Duration (time)
    """
    Function to get fastest bus stop, taking into account the duration from the starting bus stop to the next bus stop, 
    as well as the next available bus
    """

    # Initialise database connection
    mysql_db = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_schema)
    db_cursor = mysql_db.cursor(buffered=True)

    # Check if live bus data is to be incorporated
    if(INTEGRATE_LIVE_BUS):
        # Get list of scheduleIDs for the arrival timings of live buses, if the program flag is set (limitation: function execution is slow due to the calculations required to determine the direction of each bus, and which bus stop that it is headed to)
        list_schedules = get_live_bus()

    # Get list of nearest bus stops, in ascending order (fastest one in lower index)
    bus_stops = []

    # Check if there are any scheduled buses for the day
    check_sql = "SELECT IF(CURRENT_TIME() <= (SELECT MAX(Time) FROM Schedule), \"Today\", \"Tomorrow\");"
    db_cursor.execute(check_sql)
    bus_day = db_cursor.fetchall()[0][0]

    # Boolean to check bus day
    today = None

    # Get bus stops
    if(bus_day == "Today"):
        # Get buses for the day
        today = True
        sql = "SELECT Edge.*, Bus.BusID, Bus.Name, Schedule.Time AS Time, Weight.Weight As Duration, TIMESTAMPDIFF(SECOND, CURRENT_TIME(), Time) / 60 AS Waiting_Time, (Weight.Weight + (TIMESTAMPDIFF(SECOND, CURRENT_TIME(), Time) / 60)) AS Total_Time FROM Edge JOIN BusRoute ON Edge.RouteID = BusRoute.RouteID  JOIN Bus ON BusRoute.BusID = Bus.BusID JOIN Weight ON Edge.EdgeID = Weight.EdgeID  JOIN Schedule ON BusRoute.RouteID = Schedule.RouteID  WHERE Edge.FromBusStopID = %s AND Weight.Type = 2 AND Time >= CURRENT_TIME() ORDER BY Total_Time ASC;" % start_bus_stop_id
    else:
        # Get buses for the next day
        today = False
        sql = "SELECT Edge.*, Bus.BusID, Bus.Name, Schedule.Time AS Time, Weight.Weight As Duration, TIMESTAMPDIFF(SECOND, CURRENT_TIME(), CONCAT(DATE(NOW() + INTERVAL 1 DAY), \' \', Time)) / 60 AS Waiting_Time, (Weight.Weight + (TIMESTAMPDIFF(SECOND, CURRENT_TIME(), CONCAT(DATE(NOW() + INTERVAL 1 DAY), \' \', Time)) / 60)) AS Total_Time FROM Edge JOIN BusRoute ON Edge.RouteID = BusRoute.RouteID  JOIN Bus ON BusRoute.BusID = Bus.BusID JOIN Weight ON Edge.EdgeID = Weight.EdgeID JOIN Schedule ON BusRoute.RouteID = Schedule.RouteID WHERE Edge.FromBusStopID = %s AND Weight.Type = 2 ORDER BY Total_Time ASC;" % start_bus_stop_id
    db_cursor.execute(sql)

    # Check for edge cases whereby the bus stop only has few buses (ie only one bus service), and there is no more scheduled buses for the day
    if(today and db_cursor.rowcount == 0):
        # Get buses for the next day instead in this case
        today = False
        sql = "SELECT Edge.*, Bus.BusID, Bus.Name, Schedule.Time AS Time, Weight.Weight As Duration, TIMESTAMPDIFF(SECOND, CURRENT_TIME(), CONCAT(DATE(NOW() + INTERVAL 1 DAY), \' \', Time)) / 60 AS Waiting_Time, (Weight.Weight + (TIMESTAMPDIFF(SECOND, CURRENT_TIME(), CONCAT(DATE(NOW() + INTERVAL 1 DAY), \' \', Time)) / 60)) AS Total_Time FROM Edge JOIN BusRoute ON Edge.RouteID = BusRoute.RouteID  JOIN Bus ON BusRoute.BusID = Bus.BusID JOIN Weight ON Edge.EdgeID = Weight.EdgeID JOIN Schedule ON BusRoute.RouteID = Schedule.RouteID WHERE Edge.FromBusStopID = %s AND Weight.Type = 2 ORDER BY Total_Time ASC;" % start_bus_stop_id
        db_cursor.execute(sql)

    # Loop through buses obtained
    for i in db_cursor:
        # Parse each row
        schedule_time = datetime.datetime.min + i[6]
        bus_stop = {'EdgeID': i[0], 'BusStopID': i[2], 'BusID': i[4], 'Bus': i[5], 'NextBus': schedule_time, 'Duration': i[7], 'Wait': float(i[8]), 'Total': i[9]}
        # Get BusID
        bus_stops.append(bus_stop)

    # Check if live bus data is to be incorporated
    if(INTEGRATE_LIVE_BUS):
        # Loop through each scheduleID that have been created for live bus
        for schedule_id in list_schedules:
            # Delete temporarily created schedule
            delete_sql = "DELETE FROM Schedule WHERE ScheduleID = %s;" % schedule_id
            db_cursor.execute(delete_sql)

    # Effect changes
    mysql_db.commit()
    
    # Close the cursor and connection
    db_cursor.close()
    mysql_db.close()

    # Return next fastest path
    return bus_stops

def get_directions(origin_coordinates, destination_coordinates):
    """
    Function to get directions from an origin to a destination point

    """

    # Set strings
    origin_string = "%s,%s" % (origin_coordinates[0], origin_coordinates[1])
    destination_string = "%s,%s" % (destination_coordinates[0], destination_coordinates[1])

    # Initialise direction string
    str_directions = None

    # Get directions
    directions = gmaps.directions(origin_string, destination_string, mode='walking', departure_time=datetime.datetime.now())[0]['legs'][0]
    
    # Prepare overall directions
    str_directions = "Total Distance: %s" % directions['distance']['text']
    str_directions += "\nEstimated Duration: %s" % directions['duration']['text']  

    # Parse instructions
    directions = directions['steps']
    for i in range(len(directions)):
        # Header
        if('maneuver' in directions[i].keys()):
            str_directions += "\n\nStep %s:\nInstruction: %s\nGuide: %s " % (i + 1, directions[i]['maneuver'].title().replace("-", " "), bs_4(directions[i]['html_instructions'], 'html.parser').get_text())
        else:
            str_directions += "\n\nStep %s:\nInstruction: %s" % (i + 1, bs_4(directions[i]['html_instructions'], 'html.parser').get_text())
        # Body
        str_directions += "\nDistance: %s m\nWalking Time: %s" % (directions[i]['distance']['value'], directions[i]['duration']['text'])
        str_directions += "\nStart Point: %s (%s, %s)" % (get_location(directions[i]['start_location']['lat'], directions[i]['start_location']['lng']), directions[i]['start_location']['lat'], directions[i]['start_location']['lng'])
        str_directions += "\nEnd Point: %s (%s, %s)" % (get_location(directions[i]['end_location']['lat'], directions[i]['end_location']['lng']), directions[i]['end_location']['lat'], directions[i]['end_location']['lng'])
    # Return directions
    return str_directions

def send_email(incoming_email, subject, message):
    """ 
    Function for sending email
    """
    # Set email header
    msg = MIMEMultipart ()
    msg ['From'] = formataddr ((str (Header (outgoing_email_name, 'utf-8')), outgoing_email))
    msg ['To'] = incoming_email
    msg ['Subject'] = subject
    # Set email message
    msg.attach (MIMEText(message + email_footer, 'html'))
    text = msg.as_string () 
    # Initialise send status
    email_sent = None
    try:
        # Start SMTP server
        server = smtplib.SMTP ('smtp.gmail.com', 587)
        server.starttls ()
        # Login to server
        server.login (outgoing_email, outgoing_email_password)
        # Send email notification
        server.sendmail (outgoing_email, incoming_email, text)
        email_sent = True
    except Exception as error:
        email_sent = False
    finally:
        # Close server regardless whether the email was sent successfully or not
        server.quit ()
        return email_sent

def getBusFromBusID(busID):
    """
    Function to get bus numbers given its busID
    """
    # Initialise database connection
    connection = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_schema)
    cursor = connection.cursor()

    # Get busName from busID from Bus table in DB
    query = "SELECT Name FROM Bus WHERE BusID = {}".format(busID)
    cursor.execute(query)
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    # Return next fastest path
    return result[0]

def convertBusIDListToNameList(busIDList):
    busNameList = []
    for busID in busIDList:
        busName = getBusFromBusID(busID)
        busNameList.append(busName)
    return busNameList

def getBusRouteDuration(total_distance):
    total_duration = total_distance / 70 * 60 * 60  # in seconds
    
    # Convert the total duration to hours, minutes, and seconds
    hours = int(total_duration // 3600)
    minutes = int((total_duration % 3600) // 60)
    seconds = int(total_duration % 60)

    duration = str(hours) + " hr " + str(minutes) + " min"
    # Print the total duration in the desired format
    print(f"Bus journey time is estimated to be about {hours} hours {minutes} minutes {seconds} seconds\n")
    return duration

def test_function():
    for start_bus_stop_id in range(1, 168):
        print("Bus Stop: %s (%s)" % (start_bus_stop_id, len(get_fastest_bus_stop(start_bus_stop_id))))

#------------------------------------------------------------------------------------------------------------------------------------------------------------

# def mainTest(start, end, option):

#     # user_input = input("Select route method:\n1) Shortest time\n2) Shortest path \n")

#     if option == '1':
#         #If Shortest time in BusStopID
#         busName,pathID = aStarAlgo(start, end)


#     elif option == '2':
#         #If Shortest path in BusStopID
#         pathID,total_distance= shortest_path_with_min_transfers(start, end)
#         print(total_distance)

#     #Get the list of busStopID , names, lat , long from sql
#     ID_Name_Coordinates = getBusStopNamesFromID()
        
    
#     # Create a dictionary that maps each numeric ID to its corresponding name and coordinates
#     id_to_name_coordinates = {id_: (name, lat, long) for id_, name, lat, long in ID_Name_Coordinates}

#     # Convert the pathID list to a list of names and coordinates using the id_to_name_coordinates dictionary
#     path_names_coordinates = [id_to_name_coordinates[id_] for id_ in pathID]

#     # Extract the coordinates from the list of names and coordinates
#     path_coordinates = [(lat, long) for _, lat, long in path_names_coordinates]

#     # Print out Bus stop names and coordinates 
#     for name, bus in zip(path_names_coordinates, busName):
#         print(name[0], bus)
#         print()

    # return path_names_coordinates, path_coordinates


# start = int(input("Enter starting busStopID: "))
# end = int(input("Enter ending busStopID: "))
# user_input = input("\n1) Shortest time\n2) Shortest path \nSelect route method: ")
# mainTest(start, end, user_input)
