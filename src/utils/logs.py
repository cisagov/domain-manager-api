"""Logging utils."""
# cisagov Libraries

# Third-Party Libraries
from bson.objectid import ObjectId

# cisagov Libraries
from api.manager import LogManager

log_manager = LogManager()


def cleanup_logs(username):
    """Cleanup log collection."""
    to_keep = log_manager.all(
        params={"username": username},
        sortby={"created": "DESC"},
        limit=100,  # Only keeping 100 for now. Change when a new number is determined.
        fields=["_id"],
    )
    ids = [ObjectId(x.get("_id")) for x in to_keep]
    return log_manager.delete(params={"_id": {"$nin": ids}, "username": username})
