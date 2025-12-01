import flask
from repository import Repository
from service import Service
from view import View

def create_app():
    app = flask.Flask(__name__)

    repo = Repository()
    service = Service(repo)
    view = View(service)

    app.register_blueprint(view.blueprint)
    return app

if __name__ == '__main__':
    create_app().run(debug=True)
