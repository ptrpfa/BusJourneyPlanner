from flask import Flask, render_template, request
import plotBus

app=Flask(__name__)

@app.route('/')
def root():
    #Get Live traffic data
    map_html = plotBus.generate_map()
    
    return render_template('index.html',map=map_html)

@app.route("/process-data", methods=["POST"])
def process_data():
    # Get the input data from the request
    start = request.form.get("Start")
    destination = request.form.get("Destination")
    option = request.form.get("Option")

    # Process the data
    map_html = plotBus.generate_map2()

    # Return the processed data as a string
    return map_html 

if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)                                                                         