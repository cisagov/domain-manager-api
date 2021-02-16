"""User utils."""
# Third-Party Libraries
from flask import g

# cisagov Libraries
from api.manager import LogManager, UserManager
from settings import logger

user_manager = UserManager()
log_manager = LogManager()


def get_user_groups():
    """Get the groups a user belongs to."""
    try:
        user = user_manager.get(filter_data={"Username": g.username})
        if "Groups" in user:
            return user["Groups"]
        else:
            return []

    except Exception as e:
        logger.exception(e)
        return []


def get_users_group_ids():
    """Get applications a user belongs to."""
    try:
        groups = get_user_groups()
        result = []
        for group in groups:
            result.append(group["Application_Id"])

        return result

    except Exception as e:
        logger.exception(e)
        return []


def user_can_access_domain(domain):
    """Check whether user can access domain."""
    try:
        if g.is_admin:
            return True
        else:
            groups = get_users_group_ids()
            if "application_id" in domain:
                if domain["application_id"] in groups:
                    return True
        return False
    except Exception as e:
        logger.exception(e)
        return False
