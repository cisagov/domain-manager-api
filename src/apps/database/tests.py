"""
This is an example stript.

Here is an example on how to run and call the db.
This shows the create, filter, and use of filter of
demo objects in a demo collelction.

TODO: Setup Mocks and not rely on db conneciton.

"""
# Standard Python Libraries
import asyncio
from datetime import datetime
import json
import logging
import os
import unittest
import uuid

# Third-Party Libraries
from service import Service
from test_validators import DemoModel, validate_demo

logger = logging.getLogger(__name__)


def load_config():
    """This loads configuration from env."""
    configs = {
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PW": os.getenv("DB_PW"),
        "DB_PORT": os.getenv("DB_PORT"),
    }

    return configs


class TestStringMethods(unittest.TestCase):
    """Unittest TestCase Class."""

    @classmethod
    def setUpClass(cls):
        """
        SetUpClass.

        Taking in env from local json and setting up database connection.
        This should be mocked.
        """
        cls.service_config = load_config()
        cls.mongo_uri = "mongodb://{}:{}@{}:{}/".format(
            cls.service_config["DB_USER"],
            cls.service_config["DB_PW"],
            cls.service_config["DB_HOST"],
            cls.service_config["DB_PORT"],
        )

        logger.info("service_config {}".format(cls.service_config))

        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)

        cls.demo_service = Service(
            cls.mongo_uri,
            collection_name="demo",
            model=DemoModel,
            model_validation=validate_demo,
        )

    @classmethod
    def tearDownClass(cls):
        """
        TearDownClass.

        This is run at the very end of the tests for cleanup.
        This will query the test DB and remove all documents found from testing.
        """
        results = cls.loop.run_until_complete(
            cls.demo_service.filter_list(parameters={})
        )
        for doc in results:
            cls.loop.run_until_complete(cls.demo_service.delete(uuid=doc["demo_uuid"]))

    def test_create(self):
        """
        Test Case: Create.

        This is to test the creation method on service.
        """
        demo_id = str(uuid.uuid4())
        self.to_create = {
            "demo_uuid": demo_id,
            "name": "demo 1",
            "enum_type": "initial",
            "record_tstamp": datetime.utcnow(),
            "method_of_record_creation": "CLI",
            "last_updated_by": "test user 1",
        }

        self.loop.run_until_complete(self.demo_service.create(to_create=self.to_create))
        created = self.loop.run_until_complete(self.demo_service.get(uuid=demo_id))

        self.assertEqual(created["demo_uuid"], demo_id)

        logger.info("created {}".format(created))
        delteted = self.loop.run_until_complete(self.demo_service.delete(uuid=demo_id))
        logger.info("delteted {}".format(delteted))

    def test_filter_empty(self):
        """
        Test Case: Filter.

        This is to test the filter method on service.
        """
        to_create_data = [
            {
                "demo_uuid": str(uuid.uuid4()),
                "name": "demo 1",
                "enum_type": "initial",
                "record_tstamp": datetime.utcnow(),
                "method_of_record_creation": "CLI",
                "last_updated_by": "test user 1",
            },
            {
                "demo_uuid": str(uuid.uuid4()),
                "name": "demo 2",
                "enum_type": "initial",
                "record_tstamp": datetime.utcnow(),
                "method_of_record_creation": "CLI",
                "last_updated_by": "test user 2",
            },
            {
                "demo_uuid": str(uuid.uuid4()),
                "name": "demo 3",
                "enum_type": "initial",
                "record_tstamp": datetime.utcnow(),
                "method_of_record_creation": "CLI",
                "last_updated_by": "test user 1",
            },
        ]

        for item in to_create_data:
            self.loop.run_until_complete(self.demo_service.create(to_create=item))

        filter_params = {"last_updated_by": "test user 1"}

        results = self.loop.run_until_complete(
            self.demo_service.filter_list(parameters=filter_params)
        )

        self.assertEqual(len(results), 2)

        for item in to_create_data:
            self.loop.run_until_complete(
                self.demo_service.delete(uuid=item["demo_uuid"])
            )

    def test_get(self):
        """
        Test Case: Get.

        This is to test the get method on service.
        """
        demo_id = str(uuid.uuid4())
        create_object = {
            "demo_uuid": demo_id,
            "name": "demo 1",
            "enum_type": "initial",
            "record_tstamp": datetime.utcnow(),
            "method_of_record_creation": "CLI",
            "last_updated_by": "test user 1",
        }

        self.loop.run_until_complete(self.demo_service.create(to_create=create_object))
        get_object = self.loop.run_until_complete(self.demo_service.get(uuid=demo_id))

        self.assertEqual(get_object["demo_uuid"], demo_id)

        self.loop.run_until_complete(self.demo_service.delete(uuid=demo_id))

    def test_count(self):
        """
        Test Case: Count.

        This is to test the count method on service.
        """
        self.assertEqual("foo".upper(), "FOO")

    def test_update(self):
        """
        Test Case: Update.

        This is to test the update method on service.
        """
        demo_id = str(uuid.uuid4())
        create_object = {
            "demo_uuid": demo_id,
            "name": "demo 1",
            "enum_type": "initial",
            "record_tstamp": datetime.utcnow(),
            "method_of_record_creation": "CLI",
            "last_updated_by": "test user 1",
        }

        self.loop.run_until_complete(self.demo_service.create(to_create=create_object))

        updated_object = {
            "demo_uuid": demo_id,
            "name": "updated demo now",
            "enum_type": "initial",
            "record_tstamp": datetime.utcnow(),
        }

        self.loop.run_until_complete(self.demo_service.update(to_update=updated_object))

        get_object = self.loop.run_until_complete(self.demo_service.get(uuid=demo_id))

        self.assertEqual(get_object["name"], updated_object["name"])

        self.loop.run_until_complete(self.demo_service.delete(uuid=demo_id))

    def test_delete(self):
        """
        Test Case: Delete.

        This is to test the delete method on service.
        """
        demo_id = str(uuid.uuid4())
        create_object = {
            "demo_uuid": demo_id,
            "name": "demo 1",
            "enum_type": "initial",
            "record_tstamp": datetime.utcnow(),
            "method_of_record_creation": "CLI",
            "last_updated_by": "test user 1",
        }

        self.loop.run_until_complete(self.demo_service.create(to_create=create_object))

        delete_result = self.loop.run_until_complete(
            self.demo_service.delete(uuid=demo_id)
        )

        self.assertEqual(delete_result, True)


if __name__ == "__main__":
    unittest.main()
