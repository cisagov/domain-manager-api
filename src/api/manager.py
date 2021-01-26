"""Database Managers."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from bson.objectid import ObjectId

# cisagov Libraries
from api.schemas.application_schema import ApplicationSchema
from api.schemas.category_schema import CategorySchema
from api.schemas.domain_schema import DomainSchema
from api.schemas.proxy_schema import ProxySchema
from api.schemas.template_schema import TemplateSchema
from api.schemas.user_shema import UserSchema
from settings import DB


class Manager:
    """Manager."""

    def __init__(self, collection, schema, indexes):
        """Initialize Manager."""
        self.collection = collection
        self.schema = schema
        self.indexes = indexes
        self.db = getattr(DB, collection)
        return

    def convert_fields(self, fields):
        """Convert list of fields into mongo syntax."""
        if not fields:
            return None
        result = {}
        for field in fields:
            result[field] = 1
        return result

    def format_params(self, params):
        """Format params."""
        if not params:
            return {}
        return params

    def read_data(self, data, many=False):
        """Read data from database."""
        schema = self.schema(many=many)
        return schema.load(schema.dump(data))

    def load_data(self, data, many=False):
        """Load data into database."""
        schema = self.schema(many=many)
        return schema.load(data)

    def create_indexes(self):
        """Create indexes for collection."""
        for index in self.indexes:
            self.db.create_index(index, unique=True)

    def add_created(self, data):
        """Add created attribute to data on save."""
        if type(data) is dict:
            data["created"] = datetime.utcnow().isoformat()
        elif type(data) is list:
            for item in data:
                item["created"] = datetime.utcnow().isoformat()
        return data

    def add_updated(self, data):
        """Update updated data on update."""
        if type(data) is dict:
            data["updated"] = datetime.utcnow().isoformat()
        elif type(data) is list:
            for item in data:
                item["updated"] = datetime.utcnow().isoformat()
        return data

    def clean_data(self, data):
        """Clean data for saves to the database."""
        invalid_fields = ["_id", "created", "updated"]
        if type(data) is dict:
            for field in invalid_fields:
                if data.get(field):
                    data.pop(field)
        elif type(data) is list:
            for item in data:
                for field in invalid_fields:
                    if item.get(field):
                        item.pop(field)
        return data

    def get(self, document_id=None, filter_data=None, fields=None):
        """Get item from collection by id or filter."""
        if document_id:
            return self.read_data(
                self.db.find_one(
                    {"_id": ObjectId(document_id)},
                    self.convert_fields(fields),
                )
            )
        else:
            return self.read_data(
                self.db.find_one(
                    filter_data,
                    self.convert_fields(fields),
                )
            )

    def all(self, params=None, fields=None):
        """Get all items in a collection."""
        return self.read_data(
            self.db.find(self.format_params(params), self.convert_fields(fields)),
            many=True,
        )

    def delete(self, document_id):
        """Delete item by object id."""
        return self.db.delete_one({"_id": ObjectId(document_id)}).raw_result

    def update(self, document_id, data):
        """Update item by id."""
        data = self.clean_data(data)
        data = self.add_updated(data)
        return self.db.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": self.load_data(data)},
        ).raw_result

    def remove(self, document_id, data):
        """Remove document fields by id."""
        return self.db.update_one(
            {"_id": ObjectId(document_id)},
            {"$unset": data},
        ).raw_result

    def save(self, data):
        """Save new item to collection."""
        self.create_indexes()
        data = self.clean_data(data)
        data = self.add_created(data)
        result = self.db.insert_one(self.load_data(data))
        return {"_id": str(result.inserted_id)}

    def save_many(self, data):
        """Save many items in collection."""
        self.create_indexes()
        data = self.clean_data(data)
        data = self.add_created(data)
        result = self.db.insert_many(self.load_data(data, many=True))
        return result.inserted_ids

    def add_to_list(self, document_id, field, data):
        """Add item to list in document."""
        return self.db.update_one(
            {"_id": ObjectId(document_id)}, {"$push": {field: data}}
        ).raw_result

    def delete_from_list(self, document_id, field, data):
        """Delete item from list in document."""
        return self.db.update_one(
            {"_id": ObjectId(document_id)}, {"$pull": {field: data}}
        ).raw_result

    def update_in_list(self, document_id, field, data, params):
        """Update item in list from document."""
        return self.db.update_one(
            {"_id": ObjectId(document_id), **params}, {"$set": {field: data}}
        ).raw_result


class ApplicationManager(Manager):
    """Application Manager."""

    def __init__(self):
        """Initialize super for application."""
        return super().__init__(
            collection="applications",
            schema=ApplicationSchema,
            indexes=["name"],
        )


class CategoryManager(Manager):
    """CategoryManager."""

    def __init__(self):
        """Initialize super for category."""
        return super().__init__(
            collection="categories",
            schema=CategorySchema,
            indexes=["name"],
        )


class ProxyManager(Manager):
    """ProxyManager."""

    def __init__(self):
        """Initialize super for proxy."""
        return super().__init__(
            collection="proxies",
            schema=ProxySchema,
            indexes=["name"],
        )


class TemplateManager(Manager):
    """TemplateManager."""

    def __init__(self):
        """Initialize super for template."""
        return super().__init__(
            collection="templates",
            schema=TemplateSchema,
            indexes=["name"],
        )

class UserManager(Manager):
    """UserManager."""

    def __init__(self):
        """Initialize super for website."""
        return super().__init__(
            collection="users",
            schema=UserSchema,
            indexes=["Username"],
        )

class DomainManager(Manager):
    """DomainManager."""

    def __init__(self):
        """Initialize super for domain."""
        return super().__init__(
            collection="domains",
            schema=DomainSchema,
            indexes=["name"],
        )
