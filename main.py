import flask 
import utils 

global manager
manager = utils.ConnectionManager()

app = flask.Flask(__name__)

@app.route("/")
def index():
    return flask.render_template('base.html')

@app.route("/test")
def test():
    return flask.render_template('test_template.html', name="sam g")

app.run(debug=True)

manager.dispose()
