import os
from flask import Flask, request, jsonify
from pymongo import MongoClient

from datetime import datetime


app = Flask(__name__)

client = MongoClient("db", 27017)


@app.route("/")
def index():
    return jsonify(status=True, message="Congrats! Your API is now live")


if __name__ == "__main__":
    APP_DEBUG = int(os.environ.get("DEBUG", default=0))
    app.run(host="0.0.0.0", port=5000, debug=APP_DEBUG)
