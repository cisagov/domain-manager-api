"""Domain manager."""
# Standard Python Libraries
import os

# Third-Party Libraries
from apps.api import api
import aws_lambda_wsgi

# cisagov Libraries
from flask import Flask, jsonify

app = Flask(__name__)


# register apps
app.register_blueprint(api)


@app.route("/")
def home():
    """Homepage view."""
    return jsonify(message="Congrats! Your API is now live", status=200)


def lambda_handler(event, context):
    """Lambda handler."""
    return aws_lambda_wsgi.response(app, event, context)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
