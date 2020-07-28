import os
from datetime import datetime

from flask import Flask, jsonify

from apps.api import api


app = Flask(__name__)


# register apps
app.register_blueprint(api)


@app.route("/")
def home():
    return jsonify(message="Congrats! Your API is now live", status=200)


def lambda_handler(event, context):
    return aws_lambda_wsgi.response(app, event, context)


if __name__ == "__main__":
    APP_DEBUG = int(os.environ.get("DEBUG", default=0))
    app.run(host="0.0.0.0", port=5000, debug=APP_DEBUG)
