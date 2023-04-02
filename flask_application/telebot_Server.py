from cloud_config import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler    
from telegram import ChatAction
from time import sleep
import textwrap

from utils import *
from algorithms.aStarAlgo import *
from algorithms.dijkstraAlgo import *
import planner

print("Bot started...")
START, END, EMAIL = range(3)
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
        # Get the list of [busStopID , names, lat , long] 
        ID_Name_Coordinates = getBusStopNamesFromID()

        # Create a dictionary that maps each numeric ID to its corresponding name and coordinates
        id_to_name_coordinates = {id_: (name, lat, long) for id_, name, lat, long in ID_Name_Coordinates}

        # Convert the pathID list to a list of names and coordinates using the id_to_name_coordinates dictionary
        path_names_coordinates = [id_to_name_coordinates[id_] for id_ in pathID]
        path_names = [name for name, lat, long in path_names_coordinates]

        # Initialise instructions
        path_start_instructions = ""
        path_end_instructions = ""

        path_bus_str = ""

        for name, bus in zip(path_names_coordinates, busName):
            path_bus_str += (name[0] +  "\n" + bus + "\n\n")

        if path_names_coordinates: #For Checking 
            #Step 8: Guide user 
            # Get walking directions to starting bus stop
            if(start_bus_stop['Distance'] > 0 ):
                path_start_instructions = get_directions(start_coordinates, start_bus_stop['Coordinates'])
                path_start_instructions2 = path_start_instructions.replace("\n","<br>")
                
            # Get walking directions from last bus stop to destination
            if(end_bus_stop['Distance'] > 0):
                # footer = "\nDirections to %s\n" % destination
                path_end_instructions = get_directions(end_bus_stop['Coordinates'], end_coordinates)
                path_end_instructions2 = path_end_instructions.replace("\n","<br>")

            my_dict = {}
            my_dict['path_bus_str'] = path_bus_str
            my_dict['path_start_instructions'] = path_start_instructions
            my_dict['path_end_instructions'] = path_end_instructions
            my_dict['path_start_instructions2'] = path_start_instructions2
            my_dict['path_end_instructions2'] = path_end_instructions2

            return my_dict
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

    context.bot.sendChatAction(chat_id=update.callback_query.message.chat.id, action=ChatAction.TYPING)
    
    #Get the start location
    start = context.user_data['start']
    start_coordinates = context.user_data['start_coordinates']

    #Get the end location
    destination = context.user_data['destination']
    end_coordinates = context.user_data['end_coordinates'] 

    dict_routes = route_planner(start_coordinates, end_coordinates, option)


    # if end_instructions.startswith("ERROR:"):
    #     context.bot.send_message(chat_id=query.message.chat_id, text=end_instructions, reply_to_message_id=query.message.message_id)
    #     return restart(update, context)

    #Store the instructions
    context.user_data['dict_routes'] = dict_routes
    
    path_bus_str = dict_routes['path_bus_str'] 
    path_start_instructions = dict_routes['path_start_instructions'] 
    path_end_instructions = dict_routes['path_end_instructions'] 

    #Directions to first bus stop
    for chunk in [path_start_instructions[i:i+4096] for i in range(0, len(path_start_instructions), 4096)]:
        updater.bot.sendMessage(chat_id=update.callback_query.message.chat.id, text=chunk)

    updater.bot.sendMessage(chat_id=update.callback_query.message.chat.id, text="Bus and Bus Stop")

    #Buses and Bus Stops
    for chunk in textwrap.wrap(path_bus_str, width=4096, replace_whitespace=False):
        updater.bot.sendMessage(chat_id=update.callback_query.message.chat.id, text=chunk)

    #Direction to destination
    for chunk in [path_end_instructions[i:i+4096] for i in range(0, len(path_end_instructions), 4096)]:
        updater.bot.sendMessage(chat_id=update.callback_query.message.chat.id, text=chunk)

    updater.bot.sendMessage(chat_id=update.callback_query.message.chat.id, text="Aiya, send me your email. I send you details.")

    return EMAIL


def email_location(update, context):
    email = update.message.text
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    sleep(1)

    start = context.user_data['start']
    destination = context.user_data['destination']
    subject = "Directions from " + start + " to " + destination;

    dict_routes = context.user_data['dict_routes']
    
    path_bus_str = dict_routes['path_bus_str']
    path_bus_str2 = path_bus_str.replace("\n","<br>")
    
    message = dict_routes['path_start_instructions2']  + "<br>" + path_bus_str2 + "<br>" + dict_routes['path_end_instructions2'] 

    if(send_email(email, subject, message)):
        update.message.reply_text("Success, check your email!")
        print("Sucess")
    else:
        update.message.reply_text("Failed! Until next time...")
        print("Failed")

    return ConversationHandler.END


def send_popup_message(update, context):
    query = update.callback_query
    query.answer('This is a popup message!')

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
    global updater
    updater = Updater(TELEGRAM_KEY, use_context=True)
    dp = updater.dispatcher

    # Define conversation handler with the states START and END
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            START: [MessageHandler(Filters.text & (~ Filters.command), start_location)],
            END: [MessageHandler(Filters.text & (~ Filters.command), end_location), CallbackQueryHandler(callback_options)],
            EMAIL: [MessageHandler(Filters.text & (~ Filters.command), email_location)]
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('restart', restart)]
    )

    dp.add_handler(conv_handler)
    #dp.add_handler(MessageHandler(Filters.text, handle_message))
    
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

main()