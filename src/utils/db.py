"""Database utilities."""
# Standard Python Libraries
import os

# Third-Party Libraries
from pymongo import MongoClient

if os.environ.get("MONGO_TYPE", "MONGO") == "DOCUMENTDB":
    CONN_STR = "mongodb://{}:{}@{}:{}/?ssl=true&ssl_ca_certs=/var/www/rds-combined-ca-bundle.pem&retryWrites=false".format(
        os.environ.get("DB_USER"),
        os.environ.get("DB_PW"),
        os.environ.get("DB_HOST"),
        os.environ.get("DB_PORT"),
    )

else:
    CONN_STR = "mongodb://{}:{}@{}:{}/".format(
        os.environ.get("DB_USER"),
        os.environ.get("DB_PW"),
        os.environ.get("DB_HOST"),
        os.environ.get("DB_PORT"),
    )

client = MongoClient(CONN_STR)

# Set database
db = client.domain_management


class Document:
    """Database Document structure."""

    def __init__(self):
        """Initialize arguements."""
        self.keys = []
        self.document = {}

    def to_json(self):
        """Get json."""
        return self.document

    def __getitem__(self, key):
        """Get item."""
        return self.document.get(key)

    def __setitem__(self, key, value):
        """Set item."""
        self.document[key] = value
