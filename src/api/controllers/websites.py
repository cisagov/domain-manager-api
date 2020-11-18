"""Websites controller."""
# Third-Party Libraries
from models.website import Website
from api.schemas.website_schema import WebsiteSchema
from utils.aws.site_handler import delete_site, launch_site, setup_dns, delete_dns


def website_manager(request, live_site_id=None):
    """Manage websites."""
    if not live_site_id:
        if request.method == "POST":
            post_data = request.json
            domain = post_data.get("domain_id")
            application_id = post_data.get("application_id")
            website = Website.create(post_data.get("website_id"))
            ip_address = post_data.get("ip_address")

            if ip_address:
                # set dns
                setup_dns(domain=domain, ip_address=ip_address)
                # save to database
                active_site = Website.create(
                    description=post_data.get("description"),
                    domain_id=post_data.get("domain_id"),
                    ip_address=ip_address,
                    application_id=application_id,
                )
            else:
                # launch s3 bucket and set dns
                metadata = launch_site(website, domain)
                # save to database
                active_site = Website.create(
                    metadata=metadata,
                    description=post_data.get("description"),
                    domain_id=post_data.get("domain_id"),
                    website_id=post_data.get("website_id"),
                    application_id=application_id,
                )
            domain_name = domain.get("Name")
            response = {
                "message": f"Your website has been launched. Visit: https://{domain_name}"
            }
        else:
            active_sites_schema = Website(many=True)
            response = active_sites_schema.dump(Website.get_all())
        return response

    if request.method == "DELETE":
        active_site = Website(_id=live_site_id).get()
        domain = active_site.get("domain").get("_id")
        ip_address = active_site.get("ip_address")
        if ip_address:
            # delete A record from dns
            delete_dns(domain=domain, ip_address=ip_address)
        else:
            # delete s3 bucket and remove dns from domain
            delete_site(active_site, domain)
        # delete from database
        Website.delete(live_site_id)
        response = {"message": "Active site is now inactive and deleted."}
    elif request.method == "PUT":
        put_data = request.json
        Website.update(
            live_site_id=live_site_id,
            application_id=put_data.get("application_id"),
        )
        response = {"message": "Active site has been updated."}
    else:
        active_site_schema = WebsiteSchema()
        response = active_site_schema.dump(Website(_id=live_site_id))

    return response
