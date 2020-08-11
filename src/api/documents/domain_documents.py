"""Domain documents."""
# Third-Party Libraries
from utils.db_utils import Document, db

# cisagov Libraries
from bson.objectid import ObjectId


class Domain(Document):
    """Document model for domains."""

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
