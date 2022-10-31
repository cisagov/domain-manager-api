"""Database Management Views."""
# Standard Python Libraries
# Third-Party Libraries
from flask import abort, g, jsonify, request
from flask.views import MethodView


class DatabaseManagementView(MethodView):
    """Dump and restore mongo data."""

    def get(self):
        """Dump mongo data."""
        return jsonify({"message": "Dumping mongo data."})

    def post(self):
        """Restore mongo data."""
        return jsonify({"message": "Restoring mongo data."})
