# Program for initial crawling of bus and bus stop information for population of the database
import json
from utils import *

# Program Entrypoint
if(CRAWL_API):
    crawl_api()
if(CRAWL_WEB):
    # crawl_web_list() # Update bus lists
    bus_schedule = crawl_web()
    save_file(str(bus_schedule).replace("'", "\""), file_bus_schedule)

""" Load data from excel dataset, bus website and PAJ API """
# Excel Dataset
dict_data = load_dataset()

# Webpage data 
bus_schedule = json.load(open(file_bus_schedule))

# API data 
routes = json.load(open(file_routes))                   # Bus Route data (used to get overall distance)
routes = routes['data']
geo_routes = json.load(open(file_geo_routes))           # Route Coordinates data (used for displaying of routes)
geo_routes = geo_routes['data']

# Dynamic API data 
# bus_live = json.load(open(file_bus_live))               # Live Bus data (used for live bus tracking; to call API)
# bus_live = bus_live['data']

# Unused API data 
# route_schedule = json.load(open(file_route_schedule))   # Route Schedule data (Unused, will be using website data)
# route_schedule = route_schedule['data']
# bus_stop = json.load(open(file_bus_stop))               # Bus Stop data (Unused, will be using dataset given)
# bus_stop = bus_stop['data']
# bus_list = json.load(open(file_bus_list))               # Bus license plates (Unused)
# bus_list = bus_list['data']
# operators = json.load(open(file_operators))             # Bus Operators (Unused)
# operators = operators['data']

""" Insert data into MySQL database """
if(UPDATE_DB):
    # Initialise database connection
    mysql_db = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_schema)
    db_cursor = mysql_db.cursor(buffered=True)

    # Add Bus Stop data into the database
    # check_sql = "SELECT * FROM BusStop WHERE Name LIKE \"%%%s%%\";"
    check_sql = "SELECT * FROM BusStop WHERE Name = \"%s\";"
    insert_sql = "INSERT INTO BusStop (Name, Latitude, Longitude) VALUES (\"%s\", %s, %s);"
    # Loop through each bus route
    for route, df in dict_data.items():
        # Loop through each row of the current dataframe
        for index in df.index:
            # Check if the bus stop is already stored in the database
            updated_sql = check_sql % df.loc[index]['Bus Stop']
            db_cursor.execute(updated_sql)
            # Ensure that the bus stop is not already in the database
            if(not db_cursor.rowcount):
                updated_sql = insert_sql % (df.loc[index]['Bus Stop'], df.loc[index]['Latitude'], df.loc[index]['Longitude'])
                db_cursor.execute(updated_sql)

    # Add Bus data into the database
    # check_sql = "SELECT BusStopID FROM BusStop WHERE Name LIKE \"%%%s%%\";"
    check_sql = "SELECT BusStopID FROM BusStop WHERE Name = \"%s\";"
    insert_sql = "INSERT INTO Bus (Name, Type, StartBusStopID, EndBusStopID) VALUES (\"%s\", %s, %s, %s);"
    # Loop through each bus route
    for route, df in dict_data.items():
        # Initialise BusStopID
        start_bus_stop_id = None
        end_bus_stop_id = None
        # Set bus type
        if("-" in route):
            # One way bus
            bus_type = 1    
            # Get BusStopID from the database
            updated_sql = check_sql % df.iloc[0]['Bus Stop']
            db_cursor.execute(updated_sql)
            for i in db_cursor:
                start_bus_stop_id = i[0]
            updated_sql = check_sql % df.iloc[-1]['Bus Stop']
            db_cursor.execute(updated_sql)
            for i in db_cursor:
                end_bus_stop_id = i[0]
        else:
            # Looping bus
            bus_type = 2    
            # Get BusStopID from the database
            updated_sql = check_sql % df.iloc[0]['Bus Stop']
            db_cursor.execute(updated_sql)
            for i in db_cursor:
                start_bus_stop_id = i[0]
            end_bus_stop_id = start_bus_stop_id
        # Add bus into database
        updated_sql = insert_sql % (route, bus_type, start_bus_stop_id, end_bus_stop_id)
        db_cursor.execute(updated_sql)

    # Add Bus Route data into the database
    # check_sql = "SELECT BusStopID FROM BusStop WHERE Name LIKE \"%%%s%%\";"
    check_sql = "SELECT BusStopID FROM BusStop WHERE Name = \"%s\";"
    # check_bus_sql = "SELECT BusID FROM Bus WHERE Name LIKE \"%%%s%%\";"
    check_bus_sql = "SELECT BusID FROM Bus WHERE Name = \"%s\";"
    insert_sql = "INSERT INTO BusRoute (BusID, BusStopID, StopOrder) VALUES (%s, %s, %s);"
    # Loop through each bus route
    for route, df in dict_data.items():
        # Loop through each row of the current dataframe
        for index in df.index:
            # Initialise bus stop, bus ID and stop order
            bus_stop_id = None
            bus_id = None
            stop_order = df.loc[index]['StopOrder']
            # Get BusStopID from the database
            updated_sql = check_sql % df.loc[index]['Bus Stop']
            db_cursor.execute(updated_sql)
            for i in db_cursor:
                bus_stop_id = i[0]
            # Get BusID from the database
            updated_sql = check_bus_sql % route
            db_cursor.execute(updated_sql)
            for i in db_cursor:
                bus_id = i[0]
            # Add bus route into database
            updated_sql = insert_sql % (bus_id, bus_stop_id, stop_order)
            db_cursor.execute(updated_sql)

    # Add Bus Schedule data into the database
    # check_bus_sql = "SELECT BusID FROM Bus WHERE Name LIKE \"%%%s%%\";"
    check_bus_sql = "SELECT BusID FROM Bus WHERE Name = \"%s\";"
    check_sql = "SELECT RouteID FROM BusRoute WHERE BusID = %s AND StopOrder = %s;"
    insert_sql = "INSERT INTO Schedule (RouteID, Time) VALUES (%s, \"%s\");"
    # Loop through each bus schedule
    for route, timings in bus_schedule.items():
        # Initialise bus and route ID
        bus_id = None
        route_id = None
        # Get BusID from the database
        updated_sql = check_bus_sql % route
        db_cursor.execute(updated_sql)
        for i in db_cursor:
            bus_id = i[0]
        # Check if bus is a looping bus or a one-way bus
        if("-" in route):
            updated_sql = check_sql % (bus_id, 1) # One-way bus (get schedule of starting bus stop)
        else:
            updated_sql = check_sql % (bus_id, -1) # Looping bus (get schedule of starting bus stop)
        db_cursor.execute(updated_sql)
        for i in db_cursor:
            route_id = i[0]
        # Loop through each timing
        for timing in timings:
            # Update time
            time = "%s:%s:00" % (re.search('(\d{2})(\d{2})', timing).group(1), re.search('(\d{2})(\d{2})', timing).group(2))
            # Add bus schedule into the database
            updated_sql = insert_sql % (route_id, time)
            db_cursor.execute(updated_sql)

    # Effect changes
    mysql_db.commit()

    # Close connections
    db_cursor.close()
    mysql_db.close()

""" Create edges/links between bus stops """
if(UPDATE_EDGES):
    create_route_edges()

""" Create weights """
if(UPDATE_WEIGHTS):
    create_weights(1)