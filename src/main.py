import os
from datetime import datetime

from flask import Flask, jsonify
from pymongo import MongoClient

from apps.api import api


app = Flask(__name__)


@app.route("/")
def home():
    return jsonify(status=True, message="Congrats! Your API is now live")


# register views
app.register_blueprint(api)


if __name__ == "__main__":
    APP_DEBUG = int(os.environ.get("DEBUG", default=0))
    app.run(host="0.0.0.0", port=5000, debug=APP_DEBUG)
