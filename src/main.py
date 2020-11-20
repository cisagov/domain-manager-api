"""Domain manager."""
# Standard Python Libraries
import os

# Third-Party Libraries
from api import api
from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# register apps
app.register_blueprint(api)


@app.route("/")
def api_map():
    """API map."""
    endpoints = {
        endpoint.rule: endpoint.methods
        for endpoint in app.url_map.__dict__["_rules"]
        if endpoint.rule not in ["/static/<path:filename>", "/"]
    }
    return render_template("index.html", endpoints=endpoints)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
