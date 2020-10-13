"""Active sites controller."""
# Third-Party Libraries
from api.documents.active_site import ActiveSite
from api.documents.domain import Domain
from api.documents.website import Website
from api.schemas.active_site_schema import ActiveSiteSchema
from utils.aws.site_handler import delete_site, launch_site, setup_dns, delete_dns


def active_site_manager(request, live_site_id=None):
    """Manage active sites."""
    if not live_site_id:
        if request.method == "POST":
            post_data = request.json
            domain = Domain.get_by_id(post_data.get("domain_id"))
            application_id = post_data.get("application_id")
            website = Website.get_by_id(post_data.get("website_id"))
            ip_address = post_data.get("ip_address")

            if ip_address:
                # set dns
                setup_dns(domain=domain, ip_address=ip_address)
                # save to database
                active_site = ActiveSite.create(
                    description=post_data.get("description"),
                    domain_id=post_data.get("domain_id"),
                    ip_address=ip_address,
                    application_id=application_id,
                )
            else:
                # launch s3 bucket and set dns
                live_site = launch_site(website, domain)
                # save to database
                active_site = ActiveSite.create(
                    description=post_data.get("description"),
                    s3_url=live_site,
                    domain_id=post_data.get("domain_id"),
                    website_id=post_data.get("website_id"),
                    application_id=application_id,
                )
            domain_name = domain.get("Name")[:-1]
            response = {
                "message": f"Active site with id {active_site.inserted_id} has been launched. Visit: http://{domain_name}"
            }
        else:
            active_sites_schema = ActiveSiteSchema(many=True)
            response = active_sites_schema.dump(ActiveSite.get_all())
        return response

    if request.method == "DELETE":
        active_site = ActiveSite.get_by_id(live_site_id)
        domain = Domain.get_by_id(active_site.get("domain").get("_id"))
        ip_address = active_site.get("ip_address")
        if ip_address:
            # delete A record from dns
            delete_dns(domain=domain, ip_address=ip_address)
        else:
            # delete s3 bucket and remove dns from domain
            delete_site(domain)
        # delete from database
        ActiveSite.delete(live_site_id)
        response = {"message": "Active site is now inactive and deleted."}
    elif request.method == "PUT":
        put_data = request.json
        ActiveSite.update(
            live_site_id=live_site_id,
            application_id=put_data.get("application_id"),
        )
        response = {"message": "Active site has been updated."}
    else:
        active_site_schema = ActiveSiteSchema()
        response = active_site_schema.dump(ActiveSite.get_by_id(live_site_id))

    return response
