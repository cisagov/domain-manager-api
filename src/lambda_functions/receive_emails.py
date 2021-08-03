"""Receive Emails Lambda Function."""
# cisagov Libraries
from api.manager import DomainManager


def lambda_handler(event, context):
    """Lambda Handler."""
    print(event)
    domain_manager = DomainManager()
    domains = domain_manager.all()
    print(len(domains))


if __name__ == "__main__":
    lambda_handler(None, None)
