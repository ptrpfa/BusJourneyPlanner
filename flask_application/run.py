from flask import Flask, render_template, request
import plotBus

app=Flask(__name__)

@app.route('/')
def root():
    map_html = plotBus.generate_map()
    # Refresh Map HTML
    return render_template('index.html',map=map_html)

@app.route("/process-data", methods=["POST"])
def process_data():
    # Get the input data from the request
    input_data = request.form.get("input_data")

    # Process the data
    print(input_data)
    

    # Return the processed data as a string
    # return str(processed_data)

if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)                                                                         