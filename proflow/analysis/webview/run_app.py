import json
from pathlib import Path

import flask

WEBVIEW_STATIC_FOLDER = Path(__file__).resolve().parent / "static"


def run(port=8000, datalocation="force/data.json"):
    app = flask.Flask(__name__, static_folder=WEBVIEW_STATIC_FOLDER)

    @app.route("/")
    def root():
        return app.send_static_file("force/force.html")

    @app.route("/force/<path:filename>")
    def static_force_assets(filename):
        return app.send_static_file("force/" + filename)

    @app.route("/data")
    def data_file():
        with open(datalocation) as f:
            data = json.load(f)
        return flask.jsonify(data)

    print(f"\nGo to http://localhost:{port} to see the example\n")
    app.run(port=port)


if __name__ == "__main__":
    run()
