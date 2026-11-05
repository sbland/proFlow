"""Serve compiled process-network assets and graph data with Flask."""

import json
import os
from pathlib import Path

import flask

WEBVIEW_STATIC_FOLDER = Path(__file__).resolve().parent / "static"
DEFAULT_DATA_LOCATION = WEBVIEW_STATIC_FOLDER / "force" / "data.json"


def create_app(datalocation: str | Path = DEFAULT_DATA_LOCATION) -> flask.Flask:
    """Create the Flask app that hosts compiled assets and graph JSON.

    Args:
        datalocation: JSON file containing the exported process graph.

    Returns:
        The configured Flask app.
    """
    app = flask.Flask(__name__, static_folder=str(WEBVIEW_STATIC_FOLDER))

    @app.route("/")
    def root() -> flask.Response:
        """Serve the Vite-built webview entry point."""
        return app.send_static_file("force/frontend-dist/index.html")

    @app.route("/force/<path:filename>")
    def static_force_assets(filename: str) -> flask.Response:
        """Serve compiled JavaScript, CSS, and other webview assets."""
        return app.send_static_file("force/" + filename)

    @app.route("/data")
    def data_file() -> tuple[flask.Response, int] | flask.Response:
        """Read and return the configured graph JSON document."""
        try:
            with Path(datalocation).open(encoding="utf-8") as data_file_handle:
                data = json.load(data_file_handle)
        except FileNotFoundError:
            app.logger.error("Graph data file not found: %s", datalocation)
            return flask.jsonify({"error": "Graph data file not found"}), 404
        except json.JSONDecodeError:
            app.logger.exception("Graph data file contains invalid JSON: %s", datalocation)
            return flask.jsonify({"error": "Graph data file is invalid"}), 500
        except OSError:
            app.logger.exception("Unable to read graph data file: %s", datalocation)
            return flask.jsonify({"error": "Graph data file could not be read"}), 500
        return flask.jsonify(data)

    return app


def run(port: int = 8000, datalocation: str | Path = DEFAULT_DATA_LOCATION) -> None:
    """Start the local webview server on the requested port.

    Args:
        port: Local TCP port for the Flask development server.
        datalocation: JSON file containing the graph displayed by the webview.
    """
    app = create_app(datalocation)
    print(f"\nGo to http://localhost:{port} to see the example\n")
    app.run(port=port)


if __name__ == "__main__":
    run(port=int(os.environ.get("PROFLOW_WEBVIEW_PORT", "8000")))
