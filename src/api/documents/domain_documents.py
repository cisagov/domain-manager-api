"""Domain documents."""
# Third-Party Libraries
from bson.objectid import ObjectId
from utils.db_utils import Document, db


class Domain(Document):
    """
    Document model for domains.

    Note: DO NOT MODIFY. Domain data is managed by the Namecheap API.
    """

    def __init__(self, **kwargs):
        """Initialize arguments."""
        self.fields = [
            "ID",
            "Name",
            "User",
            "Created",
            "Expires",
            "IsExpired",
            "IsLocked",
            "AutoRenew",
            "WhoisGuard",
            "IsPremium",
            "IsOurDNS",
        ]
        self.document = {k: kwargs.get(k) for k in self.fields}

    @staticmethod
    def get_by_id(domain_id):
        """Get domain by id."""
        return db.domains.find_one({"_id": ObjectId(domain_id)})

    @staticmethod
    def get_all():
        """Get all registered domains."""
        return [x for x in db.domains.find()]
