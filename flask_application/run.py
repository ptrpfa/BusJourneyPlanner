from flask import Flask, render_template, request
import plotBus

app=Flask(__name__)

@app.route('/')
def root():
    map_html = plotBus.generate_map()
    # Refresh Map HTML
    return render_template('index.html',map=map_html)

if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)