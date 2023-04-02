from flask import Flask, render_template, request,json, jsonify
import mapping
import planner
import folium
import random
from utils import send_email

app=Flask(__name__)

# Root
@app.route('/')
def root():
    return render_template('index.html')

# Webhook for processing user inputs
@app.route("/process-data", methods=["POST"])
def process_data():
    # Get the input data from the request
    start = request.form.get("Start")
    destination = request.form.get("Destination")
    option = request.form.get("Option")

    data = planner.process_data(start, destination, option)

    # Return the processed data as a string
    return data 

    # return render_template('index.html', path_names_coordinates=planner.path_names_coordinates)

# Webhook for sending email to user
@app.route("/email", methods=["POST"])
def email_user():
    # Get the input data from the request
    email = request.form.get("Email")
    subject = request.form.get("Subject")
    message = request.form.get("Message")
    if(send_email(email, subject, message)):
        return "Success"
    else:
        return "Failed"

#Updating the live map periodically
@app.route('/update_map', methods=["GET"])
def update_map():

    # Generate some random data
    data = mapping.update_markers()

    return json.dumps(data)

# Program entrypoint
if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)                                                                         