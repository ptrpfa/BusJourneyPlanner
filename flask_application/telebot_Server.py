from cloud_config import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler    
from telegram import ChatAction
from time import sleep

from utils import *
from algorithms.aStarAlgo import *
from algorithms.dijkstraAlgo import *
import planner

print("Bot started...")
START, END = range(2)
# Fixed string for errors
ERROR_HEADER = "ERROR: "

def sample_responses(input_text):
    user_message = str(input_text).lower()

    if user_message in ('hello', 'hi'):
        return "Hi!"

    return "Press /start lah..."

def handle_message(update, context):
    text = str(update.message.text).lower()
    response = sample_responses(text)

    update.message.reply_text(response)

def route_planner(start_coordinates, end_coordinates, option):
    """ Journey Planning """
   
    # Check if start and end locations are the same
    if(start_coordinates == end_coordinates): 
        return ERROR_HEADER + "Both starting and ending locations are the same! No bus journey planning will be provided."
    else:
        # Step 3: Get nearest bus stop to starting coordinates
        start_bus_stop = get_nearest_bus_stop(start_coordinates[0], start_coordinates[1])
        print("Starting Bus Stop: ", start_bus_stop['StopID'], start_bus_stop['Name'])

        # Step 4: Get nearest bus stop to ending coordinates
        #start_bus_stop = {StopID, Name, Coordinate}
        end_bus_stop = get_nearest_bus_stop(end_coordinates[0], end_coordinates[1])
        print("Ending Bus Stop: ", end_bus_stop['StopID'], end_bus_stop['Name'])

        #Step 5 Guide user to nearest bus stop => Error in Google AP
        
        #Step 6 Find Shortest Path for bus to travel to end bus stop
  
        if option == "1":  #Shortest-Distance
            pathID, total_distance, busName = shortest_path_with_min_transfers(start_bus_stop['StopID'],end_bus_stop['StopID'])
            busName = convertBusIDListToNameList(busName)
            path_time = getBusRouteDuration(total_distance)
        elif option == "2": #Fastest-time
            busName, pathID, path_time = aStarAlgo(start_bus_stop['StopID'],end_bus_stop['StopID'])

        #Step 7:
        #Get the list of [busStopID , names, lat , long] 
        ID_Name_Coordinates = getBusStopNamesFromID()

        # Create a dictionary that maps each numeric ID to its corresponding name and coordinates
        id_to_name_coordinates = {id_: (name, lat, long) for id_, name, lat, long in ID_Name_Coordinates}

        # Convert the pathID list to a list of names and coordinates using the id_to_name_coordinates dictionary [(name, lat, lng), (name, lat, lng)]
        path_names_coordinates = [id_to_name_coordinates[id_] for id_ in pathID]

        #Extract the coordinates from the list of names and coordinates
        path_coordinates = [(lat, long) for _, lat, long in path_names_coordinates]

        # Initialise instructions
        path_start_instructions = ""
        path_end_instructions = ""

        if path_names_coordinates: #For Checking 
            #Step 8: Guide user 
            # Get walking directions to starting bus stop
            if(start_bus_stop['Distance'] > 0 ):
                path_start_instructions = get_directions(start_coordinates, start_bus_stop['Coordinates'])
                path_start_instructions = path_start_instructions.replace("\n","<br>")

            # Get walking directions from last bus stop to destination
            if(end_bus_stop['Distance'] > 0):
                # footer = "\nDirections to %s\n" % destination
                end_instructions = get_directions(end_bus_stop['Coordinates'], end_coordinates)
                path_end_instructions = end_instructions.replace("\n","<br>")

            return path_start_instructions
        else: 
            return ERROR_HEADER + "Well directions not found..."

def start_command(update, context):
    update.message.reply_text('Tell me where you are?')
    return START

def start_location(update, context):    
    start = update.message.text

    context.bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    sleep(1)

    # Step 1: Get starting coordinates of user
    start_coordinates, invalid_input = planner.process_inputs(start)
    # Check for invalid inputs
    if(invalid_input):
        str_error = ERROR_HEADER + invalid_input
        print(str_error) #For Server
        update.message.reply_text(str_error)
        return restart(update, context)

    #Correct Input
    #Store the start coordinates
    context.user_data['start'] = start
    context.user_data['start_coordinates'] = start_coordinates
    
    update.message.reply_text(f"Great! Where do you want to go?")
    return END

def end_location(update, context):
    destination = update.message.text

    context.bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    sleep(1)

    # Step 2: Get ending coordinates of user 
    end_coordinates, invalid_input = planner.process_inputs(destination)
    # Check for invalid inputs
    if(invalid_input):
        str_error = ERROR_HEADER + invalid_input
        print(str_error) #For Server
        update.message.reply_text(str_error)
        return restart(update, context)

    #Correct Input
    #Store the Destination coordinates
    context.user_data['destination'] = destination
    context.user_data['end_coordinates'] = end_coordinates

    reply, keyboard = Options_Keyboard()

    update.message.reply_text(reply, reply_markup=keyboard)

    return END

def Options_Keyboard():

    reply = "Select your prefered choice: "
    keyBoard = {
        "inline_keyboard": [
            [{
                "text": "Shortest Distance",
                "callback_data": "1",
                "one_time_keyboard": True
            },
            {
                "text": "Fastest Time",
                "callback_data": "2",
                "one_time_keyboard": True
            }
            ]
        ]
    }

    return reply, keyBoard

def callback_options(update, context):
    
    query = update.callback_query
    # Get the VehNum
    option = query.data

    #Get the start location
    start = context.user_data['start']
    start_coordinates = context.user_data['start_coordinates']

    #Get the end location
    destination = context.user_data['destination']
    end_coordinates = context.user_data['end_coordinates'] 

    end_instructions = route_planner(start_coordinates, end_coordinates, option)

    if end_instructions.startswith("ERROR:"):
        update.message.reply_text(end_instructions)
        return restart(update, context)
    else:
        update.message.reply_text(f"Alright! From {start} heading to {destination}...")
        update.message.reply_text(end_instructions)

    return ConversationHandler.END

def cancel(update, context):    
    update.message.reply_text("Thank you for using Johor Planner")
    return ConversationHandler.END

def restart(update, context):
    """Restart the conversation and return to the start command."""
    context.user_data.clear()
    return start_command(update, context)

def error(update, context):
    print(f"Update {update} caused error {context.error}")

def main():
    updater = Updater(TELEGRAM_KEY, use_context=True)
    dp = updater.dispatcher

    # Define conversation handler with the states START and END
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            START: [MessageHandler(Filters.text & (~ Filters.command), start_location)],
            END: [MessageHandler(Filters.text & (~ Filters.command), end_location), CallbackQueryHandler(callback_options)],
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('restart', restart)],
        per_message=False
    )

    dp.add_handler(conv_handler)
    #dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

main()