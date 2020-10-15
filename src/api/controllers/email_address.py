"""Email address controller."""
from api.documents.active_site import ActiveSite
from utils.aws.ses import create_email_address


def email_address_manager(domain_name):
    """Manage domain associated email addresses."""
    active_site = ActiveSite.get_by_name(domain_name)

    # Check if email records already exist
    if active_site.get("is_email_active") is True:
        return {"error": f"Email address is already active for {domain_name}"}

    email_response = create_email_address(domain_name)

    ActiveSite.update(live_site_id=active_site.get("_id"), is_email_active=True)
    return {
        "message": f"Email records for {domain_name} has been created.",
        "status_code": email_response["ResponseMetadata"].get("HTTPStatusCode"),
    }
