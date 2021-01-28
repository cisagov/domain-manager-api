"""User histroy tracking utils"""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from flask import jsonify, g

# cisagov Libraries
from settings import logger
from api.manager import (
    UserManager,
)
from api.schemas.user_shema import UserSchema

user_manager = UserManager()

def add_user_action(action):
    """Adds a action to a users history for record keeping"""
    try:
        user = user_manager.get(
            filter_data={"Username": g.username}
        )
        if "History" not in user:
            user["History"] = []
        user["History"].append(
            {
                "Action": action,
                "Time": datetime.utcnow()
            }
        )
        user_manager.update(
            document_id = user["_id"], 
            data = user
        )
        return True
    except Exception as e:
        logger.exception(e)
        return False

def get_user_groups():
    """Get the groups a user belongs to"""
    try:
        user = user_manager.get(
            filter_data={"Username": g.username}
        )
        if "Groups" in user:
            return user["Groups"]
        else :
            return []
    
    except Exception as e:
        logger.exception(e)
        return []

def get_users_group_ids():
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
    try:
        if g.is_admin:
            return True
        else:
            groups = get_users_group_ids()
            if 'application_id' in domain:
                if domain['application_id'] in groups:
                    return True
        return False
    except Exception as e:
        logger.exception(e)
        return False