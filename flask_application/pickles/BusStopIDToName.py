import mysql.connector
import pickle 

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


# establish a connection to the database
cnx = mysql.connector.connect(
    user = "root",
    password = "LKP_OOP_STRONG",
    host = "34.143.210.189",
    database = "DSA_JP"
)


# construct a query to retrieve the names of the bus stops that match the list of IDs
#query = "SELECT Name FROM BusStop WHERE BusStopID IN (" + ", ".join(str(id) for id in bus_stop_ids) + ")"


cursor = cnx.cursor()
query = "SELECT * FROM BusStop"
cursor.execute(query)

# Store the result set in a list
result_set = []
for row in cursor:
    result_set.append(row)

# close the cursor and the database connection
cursor.close()
cnx.close()

# Pickle the result set to a file
pickle_object(result_set, 'C:/Users/Jeffr/Desktop/CSC1108-JourneyPlanner/flask_application/utils/BusStopIDNamesLatLong.pk1')

