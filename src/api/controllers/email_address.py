"""Email address controller."""
from models.website import Website
from utils.aws.ses import create_email_address


def email_address_manager(domain_name):
    """Manage domain associated email addresses."""
    website = Website()
    website.name = domain_name

    # Check if email records already exist
    if hasattr(website, "is_email_active") and website.is_email_active is True:
        return {"error": f"Email address is already active for {domain_name}"}

    email_response = create_email_address(domain_name)
    website.is_email_active = True
    website.update()

    return {
        "message": f"Email records for {domain_name} has been created.",
        "status_code": email_response["ResponseMetadata"].get("HTTPStatusCode"),
    }
