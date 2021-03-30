"""Domain Data."""
# Third-Party Libraries
from faker import Faker

fake = Faker()


def get_domain():
    """Get single domain."""
    return {
        "_id": fake.uuid4(),
        "name": fake.domain_name(),
    }


def get_domains(num=10):
    """Get multiple domains."""
    return [get_domain() for i in range(0, num)]
