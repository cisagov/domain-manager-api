"""
This is the main database service.

This is a top level service for connecting with mongodb.
This creates a Service class that is given:
    mongo_url, collection_name, model, model_validation
on init.
this will then handle all transacations for the given collection and model.
"""
# cisagov Libraries
from schematics.exceptions import DataError

from .repository.generics import GenericRepository, GenericRepositoryInterface


class Service:
    """This loads configuration from env."""

    def __init__(self, mongo_url, collection_name, model, model_validation):
        """Init for service creation."""
        self.model = model
        self.model_validation = model_validation
        self.service = GenericRepositoryInterface(
            GenericRepository(mongo_url, collection_name, model_cls=model)
        )

    async def count(self, parameters=None):
        """
        Count.

        Takes in parameters that are field names and values and
        filters all documents and returns a count of
        documents matching results.
        """
        return await self.service.count(parameters)

    async def filter_list(self, parameters=None, fields=None):
        """
        Filter_list.

        Takes in parameters that are field names and values and
        filters all documents and returns list of results.
        """
        return await self.service.filter(parameters, fields)

    async def get(self, uuid):
        """
        Get.

        Given a uuid of object, will return document with unique uuid.
        """
        return await self.service.get(uuid)

    async def create(self, to_create):
        """
        Create.

        Given a json object, it wil validate the fields and create a db entrie.
        This will return the objectID of the created object
        """
        try:
            to_create = self.model_validation(to_create)
        except DataError as e:
            return {"errors": {"validation_error": e.to_primitive()}}

        return await self.service.create(to_create)

    async def update(self, to_update):
        """
        Update.

        Given a json object, it wil validate the fields and update a db entrie.
        This will return the objectID of the updated object
        """
        try:
            to_update = self.model_validation(to_update)
        except DataError as e:
            return {"errors": {"validation_error": e.to_primitive()}}

        return await self.service.update(to_update)

    async def delete(self, uuid):
        """
        Delete.

        Given a uuid of object deleteted
        Returns bool of acknowledged of object being deleted.
        """
        return await self.service.delete(uuid)
