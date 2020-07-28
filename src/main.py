import os
from datetime import datetime

from flask import Flask
from pymongo import MongoClient

from apps.api import api


app = Flask(__name__)

client = MongoClient("db", 27017)

# register views
app.register_blueprint(api)


if __name__ == "__main__":
    APP_DEBUG = int(os.environ.get("DEBUG", default=0))
    app.run(host="0.0.0.0", port=5000, debug=APP_DEBUG)
