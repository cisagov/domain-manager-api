"""Application Fake Data."""
# Third-Party Libraries
from faker import Faker

fake = Faker()


def get_application():
    """Get single app."""
    return {
        "_id": fake.uuid4(),
        "name": fake.name(),
        "contact_name": fake.name(),
        "contact_email": fake.email(),
        "contact_phone": fake.phone_number(),
        "created": fake.date_time(),
        "updated": fake.date_time(),
    }


def get_applications(num=10):
    """Get multiple apps."""
    return [get_application() for i in range(0, num)]
