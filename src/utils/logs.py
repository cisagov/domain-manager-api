"""Logging utils."""
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
    all_users_logs = log_manager.all(
        params={"username": username},
        fields=["_id"],
    )

    to_keep_array = []
    all_user_logs_array = []
    for i in to_keep:
        to_keep_array.append(i["_id"])
    for i in all_users_logs:
        all_user_logs_array.append(i["_id"])
    set_a = set(to_keep_array)
    set_b = set(all_user_logs_array)

    to_remove = set_b - set_a

    ids = []
    for i in to_remove:
        log_manager.delete(document_id=i)
        ids.append(i)

    # This is the better way to do this but requires an update to our manager system
    # reponse = log_manager.delete(params={'_id': {'$in': ids}})
    return
