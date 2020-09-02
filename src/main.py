"""Domain manager."""
# Standard Python Libraries
import os

# Third-Party Libraries
from api import api
from flask import Flask, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# register apps
app.register_blueprint(api)


@app.route("/")
def get_docs():
    """Access swagger UI."""
    return render_template("swagger.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
