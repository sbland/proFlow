import flask


def run(port=8000, datalocation="force/data.json"):
    app = flask.Flask(__name__, static_folder='static')

    @app.route("/")
    def static_proxy():
        return app.send_static_file("force/force.html")

    @app.route("/force/<path:filename>")
    def static_proxy_b(filename):
        return app.send_static_file("force/" + filename)

    @app.route("/data/<path:text>")
    def static_proxy_c(text):
        return app.send_static_file(datalocation)

    print(f"\nGo to http://localhost:{port} to see the example\n")
    app.run(port=port)


run()
