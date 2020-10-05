"""Active site documents."""
# Standard Python Libraries
import datetime

# Third-Party Libraries
from bson.objectid import ObjectId
from utils.db import Document, db


class ActiveSite(Document):
    """Document model for an active site."""

    def __init__(self, **kwargs):
        """Initialize arguments."""
        self.fields = [
            "name",
            "description",
            "s3_url",
            "domain",
            "website",
            "application",
            "is_submitted",
            "is_registered_on_mailgun",
            "launch_date",
        ]
        self.document = {k: kwargs.get(k) for k in self.fields}

    @staticmethod
    def get_by_id(live_site_id):
        """Get an active site by id."""
        return db.active_sites.find_one({"_id": ObjectId(live_site_id)})

    @staticmethod
    def get_all():
        """Get all active websites."""
        return [x for x in db.active_sites.find()]

    @staticmethod
    def create(
        description,
        domain_id,
        application_id,
        website_id=None,
        ip_address=None,
        s3_url=None,
    ):
        """Launch a live website."""
        # make names unique
        if "active_sites" not in db.list_collection_names():
            db.active_sites.create_index("name", unique=True)

        website = db.websites.find_one({"_id": ObjectId(website_id)})
        domain = db.domains.find_one({"_id": ObjectId(domain_id)})
        post_data = {
            "name": domain.get("Name")[:-1],
            "description": description,
            "domain": domain,
            "application": db.applications.find_one({"_id": ObjectId(application_id)}),
            "is_submitted": None,
            "is_registered_on_mailgun": False,
            "launch_date": datetime.datetime.utcnow(),
        }
        if ip_address:
            post_data["ip_address"] = ip_address
        else:
            post_data["s3_url"] = s3_url
            post_data["website"] = website

        return db.active_sites.insert_one(post_data)

    @staticmethod
    def update(live_site_id, **kwargs):
        """Update an existing active site."""
        put_data = {}
        if "application_id" in kwargs:
            put_data.update(
                {
                    "application": db.applications.find_one(
                        {"_id": ObjectId(kwargs.get("application_id"))}
                    ),
                }
            )
        if "description" in kwargs:
            put_data.update({"description": kwargs.get("description")})
        if "is_submitted" in kwargs:
            put_data.update({"is_submitted": kwargs.get("is_submitted")})

        db.active_sites.find_one_and_update(
            {"_id": ObjectId(live_site_id)},
            {"$set": put_data},
        )

    @staticmethod
    def delete(live_site_id):
        """Delete an active site by id."""
        return db.active_sites.delete_one({"_id": ObjectId(live_site_id)})
