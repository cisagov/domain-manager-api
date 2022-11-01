"""Database Management Views."""
from bson import json_util
import json

# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

from api.config import DB


database = DB


class DatabaseManagementView(MethodView):
    """Dump and restore mongo data."""

    def get(self):
        """Dump mongo data."""
        dump = json.loads(
            json_util.dumps(
                [
                    document
                    for coll in database.collection_names()
                    for document in database[coll].find({})
                ]
            )
        )
        return jsonify(dump)

    def post(self):
        """Restore mongo data."""
        print(request.json)
        return jsonify({"message": "Restoring mongo data."})
