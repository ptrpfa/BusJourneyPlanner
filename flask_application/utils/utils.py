from cloud_config import *
from setup.py import *

import re
import mysql.connector
import datetime
from bs4 import BeautifulSoup as bs_4
import pickle


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
    results = sql_query.execute(sql)

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
        str_directions += "\n\nStep %s:\nDistance: %s m\nWalking Time: %s" % (i + 1, directions[i]['distance']['value'], directions[i]['duration']['text'])
        str_directions += "\nStart Point: %s (%s, %s)" % (get_location(directions[i]['start_location']['lat'], directions[i]['start_location']['lng']), directions[i]['start_location']['lat'], directions[i]['start_location']['lng'])
        str_directions += "\nEnd Point: %s (%s, %s)" % (get_location(directions[i]['end_location']['lat'], directions[i]['end_location']['lng']), directions[i]['end_location']['lat'], directions[i]['end_location']['lng'])
        # Body
        if('maneuver' in directions[i].keys()):
            str_directions += "\nInstruction: %s\nGuide: %s" % (directions[i]['maneuver'].title().replace("-", " "), bs_4(directions[i]['html_instructions'], 'html.parser').get_text())
        else:
            str_directions += "\nInstruction: %s" % bs_4(directions[i]['html_instructions'], 'html.parser').get_text()

    # Return directions
    return str_directions