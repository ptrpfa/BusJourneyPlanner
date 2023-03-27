from cloud_config import *
from setup import *

import re
import mysql.connector
import datetime
import smtplib      
import pickle
from bs4 import BeautifulSoup as bs_4
from email.mime.text import MIMEText            
from email.mime.multipart import MIMEMultipart  
from email.header import Header                 
from email.utils import formataddr    

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
    
def get_nearest_bus_stop(latitude, longitude):
    """
    Function to get the nearest bus stop to a set of coordinates

    """

    # Get nearest bus stop
    nearest_bus_stop = None
    sql = "SELECT *, ST_Distance_Sphere(POINT(Longitude, Latitude), POINT(%s, %s)) / 1000 as Distance FROM BusStop ORDER BY Distance LIMIT 1;" % (longitude, latitude)
    results = sql_query(sql)

    for i in results:
        nearest_bus_stop = {'StopID': i[0], 'Name': i[1], 'Latitude': i[2], 'Longitude': i[3], 'Coordinates': [i[2], i[3]], 'Distance': i[4]}

    # Return nearest bus stop
    return nearest_bus_stop

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
            str_directions += "\n\nStep %s:\nInstruction: %s\nGuide: %s" % (i + 1, directions[i]['maneuver'].title().replace("-", " "), bs_4(directions[i]['html_instructions'], 'html.parser').get_text())
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

# Deprecated
def get_bus_schedule():
    """
    Function to get the bus schedules
    """
    # Load bus schedule from database
    if(LOAD_BUS_FROM_DB):
        # Initialise database connection
        mysql_db = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_schema)
        db_cursor = mysql_db.cursor(buffered=True)
        # Initialise bus schedule
        bus_schedule = {}
        # Ignore duplicate bus schedule timings for now (in practice, multiple buses for the same bus number are deployed at the same time at different bus stops)
        sql = "SELECT Bus.BusID, Bus.Name, Schedule.* FROM Schedule JOIN BusRoute ON Schedule.RouteID = BusRoute.RouteID JOIN Bus ON BusRoute.BusID = BusRoute.BusID ORDER BY BusID ASC, Time ASC;"
        db_cursor.execute(sql)
        for i in db_cursor:
            # Get BusID
            bus_id = i[0]
            # Convert schedule time obtained
            schedule_time = datetime.datetime.min + i[4]
            # schedule = {'BusID': i[0], 'Bus': i[1], 'ScheduleID': i[2], 'RouteID': i[3], 'Time': schedule_time}
            # Check if bus is already in dictionary
            if(bus_id in bus_schedule.keys()):
                bus_schedule[bus_id].append(schedule_time)
            else:
                bus_schedule[bus_id] = [schedule_time]
        # Remove duplicate bus schedule timings
        for k in bus_schedule.keys():
            bus_schedule[k] = sorted(list(set(bus_schedule[k])))
        # Pickle bus schedule
        pickle_object(bus_schedule, file_pickle_bus_schedule)
        # Close the cursor and connection
        db_cursor.close()
        mysql_db.close()
        # Return bus schedule
        return bus_schedule
    # Load bus schedule from pickled file
    else:
        # Return pickled bus schedule
        return load_pickle(file_pickle_bus_schedule)
    
# Function to get fastest bus stop, taking into account the duration from the starting bus stop to the next bus stop, as well as the next available bus
def get_fastest_bus_stop(start_bus_stop_id):
    # Initialise database connection
    mysql_db = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_schema)
    db_cursor = mysql_db.cursor(buffered=True)

    # Get list of nearest bus stops, in ascending order (fastest one in lower index)
    bus_stops = []
    sql = "SELECT Edge.*, Bus.BusID, Bus.Name, Schedule.Time AS Time, Weight.Weight As Duration, TIMESTAMPDIFF(SECOND, CURRENT_TIME(), Time) / 60 AS Waiting_Time, (Weight.Weight + (TIMESTAMPDIFF(SECOND, CURRENT_TIME(), Time) / 60)) AS Total_Time FROM Edge JOIN BusRoute ON Edge.RouteID = BusRoute.RouteID  JOIN Bus ON BusRoute.BusID = Bus.BusID JOIN Weight ON Edge.EdgeID = Weight.EdgeID  JOIN Schedule ON BusRoute.RouteID = Schedule.RouteID  WHERE Edge.FromBusStopID = %s AND Weight.Type = 2 AND Time >= CURRENT_TIME() ORDER BY Total_Time ASC;" % start_bus_stop_id
    db_cursor.execute(sql)
    for i in db_cursor:
        # Parse each row
        schedule_time = datetime.datetime.min + i[6]
        bus_stop = {'EdgeID': i[0], 'BusStopID': i[2], 'BusID': i[4], 'Bus': i[5], 'NextBus': schedule_time, 'Duration': i[7], 'Wait': i[8], 'Total': i[9]}
        # Get BusID
        bus_stops.append(bus_stop)

    # Close the cursor and connection
    db_cursor.close()
    mysql_db.close()

    # Return next fastest path
    return bus_stops