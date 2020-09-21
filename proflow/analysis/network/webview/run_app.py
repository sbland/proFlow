import flask


def run(port=8000, datalocation="force/force.json"):

    app = flask.Flask(__name__, static_folder="force")

    @app.route("/")
    def static_proxy():
        return app.send_static_file("force.html")

    print(f"\nGo to http://localhost:{port} to see the example\n")
    app.run(port=port)
