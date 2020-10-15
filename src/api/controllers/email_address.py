"""Email address controller."""
from utils.aws.ses import create_email_address


def email_address_manager(domain):
    """Manage domain associated email addresses."""
    response = create_email_address(domain)
    return response
