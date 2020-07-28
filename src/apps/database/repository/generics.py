"""
This is the generics file.

Here we create a GenericRepositoryInterface that wraps GenericRepository.
GenericRepositoryInterface controlles direct db transations
GenericRepository controlles db conectvivity and async transations
"""
# Standard Python Libraries
import asyncio
import logging

# Third-Party Libraries
from bson.codec_options import CodecOptions
from motor.motor_asyncio import AsyncIOMotorClient

from .tools import parse_datetime
from .types import BooleanType, DateTimeType, FloatType, IntType

logger = logging.getLogger(__name__)


def format_params(model_cls=None, params=None):
    """
    Format_params.

    A utility helper function that takes the filter params dict
    and inspects the key names for containing `__` (a double underscore)
    as we are using that to denote nested params. It also takes the model class
    of the type of model resource that we are applying this params on on it's
    ``model_cls`` kwarg and when provided converts params to their native types in python.

    :param dict params:
    :return params:
    :rtype: dict
    """
    if params is None:
        params = {}
    else:
        params = params.copy()
    for key, value in params.copy().items():
        first, *rest = key.split("__")
        if rest:
            # currently we only support one level of nestedness
            rest = rest[0]
            parent_value = params.get(first)
            if parent_value:
                if not isinstance(parent_value, dict):
                    params.update({first: {first: parent_value}})
            else:
                params[first] = {}
            if isinstance(value, str):
                try:
                    value = parse_datetime(value)
                except ValueError:
                    pass
            params[first][rest] = value
            params.pop(key)
        else:
            if model_cls:
                field = model_cls.fields.get(key)
                if field and isinstance(value, str):
                    if field.typeclass == IntType:
                        params[key] = int(value)
                    if field.typeclass == FloatType:
                        params[key] = float(value)
                    if field.typeclass == BooleanType:
                        if value.lower() in ["true", "yes", "1"]:
                            params[key] = True
                        elif value.lower() in ["false", "no", "0"]:
                            params[key] = False
                    if field.typeclass == DateTimeType:
                        params[key] = parse_datetime(value)
    return params


class GenericRepositoryInterface(object):
    """
    GenericRepositoryInterface.

    Basic interface for repositiory.
    """

    def __init__(self, repository):
        """
        Tnit.

        Assigns repository.
        """
        self.repository = repository

    def filter(self, parameters=None, fields=None):
        """
        Filter.

        Takes in parameters and send to repository with
        parameters or empty filter of None.
        Returns list of documents with applied filter.
        """
        return self.repository.filter(parameters or {}, fields or {})

    def count(self, parameters=None):
        """
        Count.

        Takes in parameters and send to repository with
        parameters or empty filter of None.
        Return int of total documents of given filter.
        """
        return self.repository.count(parameters or {})

    def get(self, uuid):
        """
        Get.

        Takes in uuid and send to repository.
        Returns exisiting object with given uuid.
        """
        return self.repository.get(uuid)

    def create(self, generic_object):
        """
        Create.

        Takes in generic_object and send to repository.
        Returns objectId of newly created document.
        """
        return self.repository.create(generic_object)

    def update(self, generic_object):
        """
        Update.

        Takes in generic_object and send to repository.
        Returns objectId of updated document.
        """
        return self.repository.update(generic_object)

    def delete(self, uuid):
        """
        Delete.

        Takes in uuid and send to repository.
        Returns bool result of object being deleted.
        """
        return self.repository.delete(uuid)


class GenericRepository(object):
    """
    Generic Base.

    Generic Base class that every other repository should then
    extend.
    The `collection_name` input parameter must be a string describing the table
    name i.e. 'experiment`. This string is also used for prefixing the uuid in `get`
    and such methods.

    The child class inheriting from this should set the `collection` parameter
    of the instance, in the `__init__` method.
    The `__init__` method shuold also super call this base class' `__init__`
    """

    def __init__(self, db_url, collection_name, model_cls=None, uuid_name=None):
        """
        Init.

        This is the primary init for creating a service of a db.
        Here we connect the AsyncIOMotorClient to a given db_url.
        Passing in a collection_name, we validate the collection
        Using model_cls as a valid moddel for collection with
        uuid_name if given as a primary key.

        """
        client = AsyncIOMotorClient(db_url, io_loop=asyncio.get_event_loop())
        self.db = client["domain_manager_dev"]
        self.collection_name = collection_name
        self.collection = self.db.get_collection(
            self.collection_name, codec_options=CodecOptions(tz_aware=True)
        )
        self.model_cls = model_cls
        self.uuid_name = uuid_name or f"{self.collection_name}_uuid"
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def document_to_object(document):
        """
        Document_to_object.

        Translate document to python object
        removes _id from document.
        """
        if document:
            document.pop("_id", None)
        else:
            document = None
        return document

    async def count(self, params=None):
        """
        Count.

        Method to only obtain the count of entries entailed in
        a specific db query.
        """
        if params is None:
            params = {}
        params = format_params(self.model_cls, params)
        return await self.collection.count_documents(params)

    async def filter(self, params=None, fields=None):
        """
        Filter.

        Generic method that can be used for either or
        filtering by specifying the optional `params` dictionary.
        """
        if params is None:
            params = {}
        params = format_params(self.model_cls, params)
        result = []
        if fields is not None:
            fields["_id"] = 0
        elif 0 in fields.values():
            fields = {"_id": 0}
        async for document in self.collection.find(params, fields):
            result.append(document)
        return result

    async def get(self, uuid):
        """
        Get.

        Generic method that can be used to get a
        single document by a given uuid.
        """
        fields = {"_id": 0}
        return await self.collection.find_one({self.uuid_name: uuid}, fields)

    async def create(self, object):
        """
        Create.

        Generic method that can be used to create a
        single document by a given object.
        """
        await self.collection.insert_one(object)
        return {self.uuid_name: object[self.uuid_name]}

    async def update(self, object):
        """
        Update.

        Generic method that can be used to update a
        single document by a given object.
        """
        await self.collection.update_one(
            {self.uuid_name: object[self.uuid_name]}, {"$set": object}
        )
        return {self.uuid_name: object[self.uuid_name]}

    async def delete(self, uuid):
        """
        Delete.

        Generic method that can be used to delete a
        single document by a given uuid.
        """
        await self.collection.delete_one({self.uuid_name: uuid})
        return {self.uuid_name: uuid}

