"""Active site documents."""
# Standard Python Libraries
import datetime

# Third-Party Libraries
from bson.objectid import ObjectId
from utils.db_utils import Document, db


class ActiveSite(Document):
    """Document model for an active site."""

    def __init__(self, **kwargs):
        """Initialize arguments."""
        self.fields = [
            "name",
            "s3_url",
            "domain",
            "website",
            "application",
            "is_available",
            "is_registered_on_mailgun",
            "launch_date",
        ]
        self.document = {k: kwargs.get(k) for k in self.fields}

    @staticmethod
    def get_by_id(active_site_id):
        """Get an active site by id."""
        return db.active_sites.find_one({"_id": ObjectId(active_site_id)})

    @staticmethod
    def get_all():
        """Get all active websites."""
        return [x for x in db.active_sites.find()]

    @staticmethod
    def create(s3_url, domain_id, website_id, application_id):
        """Launch an active site."""
        # make names unique
        if "active_sites" not in db.list_collection_names():
            db.active_sites.create_index("name", unique=True)

        website = db.websites.find_one({"_id": ObjectId(website_id)})
        post_data = {
            "name": website.get("name"),
            "s3_url": s3_url,
            "domain": db.domains.find_one({"_id": ObjectId(domain_id)}),
            "website": website,
            "application": db.applications.find_one({"_id": ObjectId(application_id)}),
            "is_available": True,
            "is_registered_on_mailgun": True,
            "launch_date": datetime.datetime.utcnow(),
        }
        return db.active_sites.insert_one(post_data)

    @staticmethod
    def update(active_site_id, domain_id, website_id, application_id):
        """Update an existing active site."""
        website = db.websites.find_one({"_id": ObjectId(website_id)})
        post_data = {
            "name": website.get("name"),
            "domain": db.domains.find_one({"_id": ObjectId(domain_id)}),
            "website": website,
            "application": db.applications.find_one({"_id": ObjectId(application_id)}),
        }

        db.active_sites.find_one_and_update(
            {"_id": ObjectId(active_site_id)}, {"$set": post_data},
        )

    @staticmethod
    def delete(active_site_id):
        """Delete an active site by id."""
        return db.active_sites.delete_one({"_id": ObjectId(active_site_id)})
