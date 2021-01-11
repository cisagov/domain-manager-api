"""Website Views."""
# Standard Python Libraries
from datetime import datetime
import io
import logging
import os
import shutil
from uuid import uuid4

# Third-Party Libraries
import boto3
from flask import current_app, jsonify, request, send_file
from flask.views import MethodView
import requests
from selenium import webdriver

# cisagov Libraries
from api.manager import (
    ApplicationManager,
    CategoryManager,
    ProxyManager,
    WebsiteManager,
)
from settings import STATIC_GEN_URL, WEBSITE_BUCKET
from utils.aws.redirect_handler import delete_redirect, modify_redirect, setup_redirect
from utils.aws.site_handler import delete_site, launch_site
from utils.two_captcha import two_captcha_api_key

category_manager = CategoryManager()
proxy_manager = ProxyManager()
website_manager = WebsiteManager()
application_manager = ApplicationManager()
route53 = boto3.client("route53")


class WebsitesView(MethodView):
    """WebsitesView."""

    def get(self):
        """Get all websites."""
        return jsonify(website_manager.all(params=request.args))

    def post(self):
        """Create a new website."""
        caller_ref = str(uuid4)
        resp = route53.create_hosted_zone(
            Name=request.json["name"], CallerReference=caller_ref
        )
        website_manager.save(
            {
                "name": request.json["name"],
                "is_active": False,
                "route53": {"id": resp["HostedZone"]["Id"]},
            }
        )
        return jsonify(resp["DelegationSet"]["NameServers"])


class WebsiteView(MethodView):
    """WebsiteView."""

    def get(self, website_id):
        """Get Website details."""
        website = website_manager.get(document_id=website_id)
        return jsonify(website)

    def put(self, website_id):
        """Update website."""
        website = website_manager.get(document_id=website_id)
        if request.json.get("application"):
            application = application_manager.get(
                filter_data={"name": request.json["application"]}
            )
            website["application_id"] = application["_id"]
            # Save application to history
            website["history"] = website.get("history", [])
            website["history"].append(
                {
                    "application": application,
                    "launch_date": datetime.utcnow(),
                }
            )

        return jsonify(website_manager.update(document_id=website_id, data=website))

    def delete(self, website_id):
        """Delete website and hosted zone."""
        website = website_manager.get(document_id=website_id)
        if not website.get("is_active", False) and not website.get("redirects", []):
            route53.delete_hosted_zone(Id=website["route53"]["id"])
            return jsonify(website_manager.delete(website["_id"]))
        return jsonify(
            {"message": "Website cannot be active and redirects must be removed."}
        )


class WebsiteContentView(MethodView):
    """WebsiteContentView."""

    def get(self, website_id):
        """Download Website."""
        website = website_manager.get(document_id=website_id)

        resp = requests.get(
            f"{STATIC_GEN_URL}/website/?category={website['category']}&domain={website['name']}",
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return {"error": str(e)}

        buffer = io.BytesIO()
        buffer.write(resp.content)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            attachment_filename=f"{website['name']}.zip",
            mimetype="application/zip",
        )

    def post(self, website_id):
        """Upload files and serve s3 site."""
        website = website_manager.get(document_id=website_id)

        domain = website["name"]
        category = "uncategorized"

        resp = requests.post(
            f"{STATIC_GEN_URL}/website/?category={category}&website={domain}",
            files={"zip": (f"{category}.zip", request.files["zip"])},
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return jsonify({"error": str(e)})

        # remove temp files
        shutil.rmtree("tmp/", ignore_errors=True)

        return jsonify(
            website_manager.save(
                {
                    "category": category,
                    "s3_url": f"https://{WEBSITE_BUCKET}.s3.amazonaws.com/{domain}/",
                }
            )
        )

    def delete(self, website_id):
        """Delete website content."""
        website = website_manager.get(document_id=website_id)

        resp = requests.delete(
            f"{STATIC_GEN_URL}/website/?category={website['category']}&domain={website['name']}",
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return {"error": str(e)}

        return jsonify(
            website_manager.remove(
                document_id=website_id, data={"category": "", "s3_url": ""}
            )
        )


class WebsiteGenerateView(MethodView):
    """WebsiteGenerateView."""

    def post(self, website_id):
        """Create website."""
        category = request.args.get("category")
        website = website_manager.get(document_id=website_id)
        domain = website["name"]
        resp = requests.post(
            f"{STATIC_GEN_URL}/generate/?category={category}&domain={domain}",
            json=request.json,
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return jsonify({"error": str(e)})

        # remove temp files
        shutil.rmtree("tmp/", ignore_errors=True)

        website_manager.update(
            document_id=website_id,
            data={
                "s3_url": f"https://{WEBSITE_BUCKET}.s3.amazonaws.com/{domain}/",
                "category": category,
            },
        )

        return jsonify(
            {
                "message": f"{domain} static site has been created from the {category} template."
            }
        )


class WebsiteRedirectView(MethodView):
    """WebsiteRedirectView."""

    def get(self, website_id):
        """Get all redirects for a website."""
        return jsonify(
            website_manager.get(document_id=website_id, fields=["redirects"])
        )

    def post(self, website_id):
        """Create a website redirect."""
        data = {
            "subdomain": request.json["subdomain"],
            "redirect_url": request.json["redirect_url"],
        }
        redirects = website_manager.get(document_id=website_id, fields=["redirects"])
        if data["subdomain"] in [
            r["subdomain"] for r in redirects.get("redirects", [])
        ]:
            return "Subdomain already utilized."

        setup_redirect(
            website_id=website_id,
            subdomain=data["subdomain"],
            redirect_url=data["redirect_url"],
        )

        return jsonify(
            website_manager.add_to_list(
                document_id=website_id, field="redirects", data=data
            )
        )

    def put(self, website_id):
        """Update a subdomain redirect value."""
        data = {
            "subdomain": request.json["subdomain"],
            "redirect_url": request.json["redirect_url"],
        }
        modify_redirect(
            website_id=website_id,
            subdomain=data["subdomain"],
            redirect_url=data["redirect_url"],
        )
        return jsonify(
            website_manager.update_in_list(
                document_id=website_id,
                field="redirects.$.redirect_url",
                data=data["redirect_url"],
                params={"redirects.subdomain": data["subdomain"]},
            )
        )

    def delete(self, website_id):
        """Delete a subdomain redirect."""
        subdomain = request.json["subdomain"]
        delete_redirect(website_id=website_id, subdomain=subdomain)
        return jsonify(
            website_manager.delete_from_list(
                document_id=website_id,
                field="redirects",
                data={"subdomain": subdomain},
            )
        )


class WebsiteLaunchView(MethodView):
    """Launch or stop an existing static site by adding dns records to its domain."""

    def get(self, website_id):
        """Launch a static site."""
        website = website_manager.get(document_id=website_id)
        metadata = launch_site(website)
        data = {
            "is_active": True,
        }
        data.update(metadata)
        website_manager.update(
            document_id=website_id,
            data=data,
        )
        name = website["name"]
        return jsonify({"success": f"{name} has been launched"})

    def delete(self, website_id):
        """Stop a static site."""
        website = website_manager.get(document_id=website_id)
        resp = delete_site(website)
        website_manager.update(
            document_id=website_id,
            data={
                "is_active": False,
            },
        )
        return jsonify(resp)


class WebsiteRecordView(MethodView):
    """View for interacting with website hosted zone records."""

    def get(self, website_id):
        """Get the hosted zone records for a website."""
        hosted_zone_id = website_manager.get(
            document_id=website_id, fields=["route53"]
        )["route53"]["id"]
        resp = route53.list_resource_record_sets(HostedZoneId=hosted_zone_id)
        return jsonify(resp["ResourceRecordSets"])


class WebsiteCategorizeView(MethodView):
    """WebsiteCategorizeView."""

    def get(self, website_id):
        """Manage categorization of active sites."""
        browserless_endpoint = os.environ.get("BROWSERLESS_ENDPOINT")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        active_site = website_manager.get(document_id=website_id)
        domain = active_site.get("domain").get("Name")
        domain_url = domain[:-1]
        if active_site.get("is_categorized"):
            return {"error": f"{domain} has already been categorized."}

        category = category_manager.get(
            filter_data={"name": request.args.get("category")}
        )

        if not category:
            return {"error": "Category does not exist"}

        is_submitted = []
        # Submit domain to proxy
        if not current_app.config["TESTING"]:
            proxies = proxy_manager.all()
            for proxy in proxies:
                proxy_name = proxy["name"]

                # Get unique category name for each proxy
                proxy_category = "".join(
                    detail.get(proxy_name)
                    for detail in category.get("proxies")
                    if proxy_name in detail
                )

                try:
                    driver = webdriver.Remote(
                        command_executor=f"http://{browserless_endpoint}/webdriver",
                        desired_capabilities=chrome_options.to_capabilities(),
                    )
                    driver.set_page_load_timeout(60)
                    exec(
                        proxy.get("script").decode(),
                        {
                            "driver": driver,
                            "url": proxy.get("url"),
                            "domain": domain_url,
                            "api_key": two_captcha_api_key,
                            "category": proxy_category,
                        },
                    )
                    driver.quit()
                    is_submitted.append(
                        {
                            "_id": proxy["_id"],
                            "name": proxy_name,
                            "is_categorized": False,
                        }
                    )
                    logging.info(f"Categorized with {proxy_name}")
                except Exception as err:
                    driver.quit()
                    logging.error(f"{proxy_name} has failed")
                    return {"error": str(err)}

        # Quit WebDriver
        driver.quit()

        # Update database
        website_manager.update(
            document_id=website_id, data={"is_submitted": is_submitted}
        )
        return jsonify({"message": f"{domain} has been successfully categorized"})
