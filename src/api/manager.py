"""Database Managers."""
# Third-Party Libraries
from bson.objectid import ObjectId

# cisagov Libraries
from api.schemas.application_schema import ApplicationSchema
from api.schemas.category_schema import CategorySchema
from api.schemas.proxy_schema import ProxySchema
from api.schemas.template_schema import TemplateSchema
from api.schemas.website_schema import WebsiteSchema
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

    def convert_data(self, data, many=False):
        """Serialize and deserialize data."""
        schema = self.schema(many=many)
        return schema.load(schema.dump(data))

    def create_indexes(self):
        """Create indexes for collection."""
        for index in self.indexes:
            self.db.create_index(index, unique=True)

    def get(self, document_id=None, filter_data=None):
        """Get item from collection by id or filter."""
        if document_id:
            return self.convert_data(self.db.find_one({"_id": ObjectId(document_id)}))
        else:
            return self.convert_data(self.db.find_one(filter_data))

    def all(self):
        """Get all items in a collection."""
        return self.convert_data(self.db.find(), many=True)

    def delete(self, document_id):
        """Delete item by object id."""
        return self.db.delete_one({"_id": ObjectId(document_id)}).raw_result

    def update(self, document_id, data):
        """Update item by id."""
        return self.db.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": self.convert_data(data)},
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
        result = self.db.insert_one(self.convert_data(data))
        return {"_id": str(result.inserted_id)}

    def save_many(self, data):
        """Save many items in collection."""
        self.create_indexes()
        result = self.db.insert_many(self.convert_data(data, many=True))
        return result.inserted_ids


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


class WebsiteManager(Manager):
    """WebsiteManager."""

    def __init__(self):
        """Initialize super for website."""
        return super().__init__(
            collection="websites",
            schema=WebsiteSchema,
            indexes=["name"],
        )
