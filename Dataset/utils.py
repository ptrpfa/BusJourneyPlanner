import requests
import re
import pickle
import pandas as pd
from bs4 import BeautifulSoup as bs_4
from config import *

# Function to write to a file
def save_file(text, file_name):
    with open(file_name, 'w') as f:
        f.write(text)

# Function to pickle object (accepts object to pickle and its filename to save as)
def pickle_object (pickle_object, filepath):
    # Create file object to store object to pickle
    file_pickle = open (filepath, 'wb') # w = write, b = bytes (overwrite pre-existing files if any)

    # Pickle (serialise) object [store object as a file]
    pickle.dump (pickle_object, file_pickle)

    # Close file object
    file_pickle.close ()

# Function to load pickle object (accepts filename of pickle to load and returns the de-pickled object)
def load_pickle (filepath):
    # Create file object accessing the pickle file
    file_pickle = open (filepath, 'rb') # r = read, b = bytes

    # Get pickled object
    pickled_object = pickle.load (file_pickle)

    # Close file object
    file_pickle.close ()

    # Return pickle object
    return pickled_object

# Function to crawl PAJ's API (limited to 6 API calls per minute)
def crawl_api():
    # Set HTTP header
    headers = {'api-key': api_key}

    # Get bus route data
    routes = requests.get(api_endpoint + '/route', headers=headers, verify=False).text
    save_file(routes, file_routes)

    # Get route coordinates
    geo_routes = requests.get(api_endpoint + '/route-geojson', headers=headers, verify=False).text
    save_file(geo_routes, file_geo_routes)

    # Get route schedule
    route_schedule = requests.get(api_endpoint + '/route-schedule', headers=headers, verify=False).text
    save_file(route_schedule, file_route_schedule)

    # Get bus operators
    operators = requests.get(api_endpoint + '/operators', headers=headers, verify=False).text
    save_file(operators, file_operators)

    # Get live bus data
    bus_live = requests.get(api_endpoint + '/bus-live', headers=headers, verify=False).text
    save_file(bus_live, file_bus_live)

    # Get bus stop data
    bus_stops = requests.get(api_endpoint + '/bus-stop', headers=headers, verify=False).text
    save_file(bus_stops, file_bus_stop)

    # Get bus list data (bus license plates)
    bus_list = requests.get(api_endpoint + '/bus-list', headers=headers, verify=False).text
    save_file(bus_list, file_bus_list)

# Function to crawl webpages for bus schedule information
def crawl_web():
    # Initialise bus schedule
    bus_schedule = {}

    # Loop through each bus (loop)
    for bus in loop_buses:
        list_timings = []
        response = requests.get(schedule_link + bus)
        response = bs_4(response.text, "lxml")
        response = response.find_all('table', attrs={'border':'1'})[1] # Get table
        response = response.find_all('div') # Get rows
        # Loop through each row to get the bus timings
        for row in response:
            list_timings.append(re.search("^<div.*>(\d*)<\/div>$", str(row)).group(1))
        bus_schedule[bus] = list_timings

    # Loop through each one way bus
    for bus in one_way_buses:
        list_timings = []
        response = requests.get(schedule_link + bus)
        response = bs_4(response.text, "lxml")
        response = response.find_all('table', attrs={'border':'1'})[1] # Get table
        
        # Get first direction
        first = response.find_all('tr')[4]
        first = first.find_all('div') # Get rows
        # Loop through each row to get the bus timings
        for row in first:
            list_timings.append(re.search("^<div.*>(\d*)<\/div>$", str(row)).group(1))
        bus_schedule[bus + '-01'] = list_timings
        
        # Get second direction
        list_timings = []
        second = response.find_all('tr')[7]
        second = second.find_all('div') # Get rows
        # Loop through each row to get the bus timings
        for row in second:
            list_timings.append(re.search("^<div.*>(\d*)<\/div>$", str(row)).group(1))
        bus_schedule[bus + '-02'] = list_timings

    # Return bus schedule obtained
    return bus_schedule

# Function to crawl webpage for a list of all buses
def crawl_web_list():
    loop_buses = []
    one_way_buses = []
    response = requests.get(route_link)
    response = bs_4(response.text, "lxml")
    response = response.find_all('table')[1]    # Get table
    response = response.find_all('tr')[1:]      # Get rows
    # Loop through each row to get the buses
    for row in response:
        bus, route = re.search("<a.*>(.*)<\/a>.*<b>(.*)<\/b>", str(row)).group(1), re.search("<a.*>(.*)<\/a>.*<b>(.*)<\/b>", str(row)).group(2)
        if(loop_char in route):
            loop_buses.append(bus)
        elif(one_way_char in route):
            one_way_buses.append(bus)
    return loop_buses, one_way_buses

# Function to load bus dataset
def load_dataset():
    # Load excel file
    excel = pd.ExcelFile(file_excel_bus)
    # Initialise empty dictionary
    data = {}
    # Loop through each sheet
    for sheet in excel.sheet_names:
        # Get dataframe
        df = excel.parse(sheet)
        # Create empty longitude column
        df['Longitude'] = 0
        # Rename column
        df.rename(columns = {'Stop ID': 'StopOrder', 'Bus stop': 'Bus Stop', 'GPS Location': 'Latitude'}, inplace = True)
        # Loop through each row of the current dataframe
        for index in df.index:
            # Get coordinates
            coordinates = df.loc[index]['Latitude']
            df.at[index, 'Latitude'], df.at[index, 'Longitude'] = [i.strip() for i in coordinates.split(",")]
        # Set dataframe to be value of key in dictionary
        data[sheet] = df
    # Return data dictionary
    return data