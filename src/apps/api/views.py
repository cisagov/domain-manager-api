from flask import Blueprint, jsonify


api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/")
def home():
    return jsonify(status=True, message="Congrats! Your API is now live")
