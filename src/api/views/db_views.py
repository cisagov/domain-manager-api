"""Database Management Views."""
# Standard Python Libraries
import io

# Third-Party Libraries
from bson.json_util import dumps, loads
from flask import jsonify, request, send_file
from flask.views import MethodView

# cisagov Libraries
from api.config import DB

database = DB


class DatabaseManagementView(MethodView):
    """Dump and restore mongo data."""

    def get(self):
        """Dump mongo data."""
        data_dump = {}
        for coll in database.collection_names():
            data_dump[coll] = [d for d in database[coll].find({})]

        mem = io.BytesIO()
        mem.write(dumps(data_dump).encode("utf-8"))
        mem.seek(0)

        return send_file(mem, mimetype="application/json")

    def post(self):
        """Restore mongo data."""
        collections = loads(request.data)

        if not isinstance(collections, dict):
            return jsonify({"error": "Invalid data format."}), 400

        for coll in collections.keys():
            coll_values = []
            for d in collections[coll]:
                coll_values.append(d)

            database[coll].insert_many(coll_values) if coll_values else None

        return jsonify({"message": "Mongo data successfully restored."})
