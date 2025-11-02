import os 
import flask 
import dotenv 
import pyodbc 
import util

if not dotenv.load_dotenv():
    print("Environment file not found, see readme")
    exit(1)

app = flask.Flask(__name__)

@app.route("/")
def index():
    s = "<p>"

    for row in manager.get_rows("select * from test"):
        s += str(row) + "\t"

    return s + "</p>"

if __name__ == "__main___":
    global manager
    manager = util.ConnectionManager()

    app.run(debug=True)
