from utils import *

""" Program Entrypoint """
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

# Display starting and end points
print("\n", "-" * 20)
print("Starting Points:")
print("Address:", start)
print("Coordinates:", start_coordinates)
print("Nearest Bus Stop:", start_bus_stop)

print("\nEnding Points:")
print("Address:", end)
print("Coordinates:", end_coordinates)
print("Nearest Bus Stop:", end_bus_stop)
print("\n", "-" * 20)

""" Journey Planning """
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

    # Guide user to destination from end bus stop
    if(end_bus_stop['Distance'] > 0):
        footer = "\nDirections to %s\n" % end
        end_instructions = get_directions(end_bus_stop['Coordinates'], end_coordinates)
        # Print guiding instructions
        print(footer) 
        print(end_instructions)

    # Check for email notification
    user_input = input("\nDo you want a copy of these directions sent to your email? (Yes or No): ")
    if(user_input.lower() == "yes"):
        user_email = input("Enter your email address: ")
        # Send email
        email_subject = "Directions from %s to %s" % (start, end)
        email_message = header + start_instructions + footer + end_instructions
        email_message = email_message.replace("\n", "<br>")
        if(send_email(user_email, email_subject, email_message)):
            print("Email sent to", user_email, "!")