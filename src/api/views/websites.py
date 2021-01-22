"""Website Views."""
# Standard Python Libraries
from datetime import datetime
import io
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
from api.schemas.website_schema import Redirect, WebsiteSchema
from settings import STATIC_GEN_URL, WEBSITE_BUCKET, logger
from utils.aws.redirect_handler import delete_redirect, modify_redirect, setup_redirect
from utils.aws.site_handler import delete_site, launch_site
from utils.two_captcha import two_captcha_api_key
from utils.validator import validate_data

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
        data = validate_data(request.json, WebsiteSchema)
        if website_manager.get(filter_data={"name": data["name"]}):
            return jsonify({"error": "Website already exists."}), 400
        caller_ref = str(uuid4())
        resp = route53.create_hosted_zone(Name=data["name"], CallerReference=caller_ref)
        website_manager.save(
            {
                "name": data["name"],
                "is_active": False,
                "is_available": True,
                "is_launching": False,
                "is_delaunching": False,
                "is_generating_template": False,
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
        data = validate_data(request.json, WebsiteSchema)

        if data.get("application"):
            website = website_manager.get(document_id=website_id)
            application = application_manager.get(
                filter_data={"name": data["application"]}
            )
            data["application_id"] = application["_id"]
            # Save application to history
            data["history"] = website.get("history", [])
            data["history"].append(
                {
                    "application": application,
                    "launch_date": datetime.utcnow(),
                }
            )

        return jsonify(website_manager.update(document_id=website_id, data=data))

    def delete(self, website_id):
        """Delete website and hosted zone."""
        website = website_manager.get(document_id=website_id)

        if website.get("is_active") and website.get("redirects"):
            return jsonify(
                {"message": "Website cannot be active and redirects must be removed."}
            )

        if website.get("category"):
            category = website["category"]
            name = website["name"]
            requests.delete(
                f"{STATIC_GEN_URL}/website/?category={category}&domain={name}",
            )

        route53.delete_hosted_zone(Id=website["route53"]["id"])
        return jsonify(website_manager.delete(website["_id"]))


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
            return {"error": str(e)}, 400

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
        # Get website data
        website = website_manager.get(document_id=website_id)

        domain = website["name"]
        category = request.args.get("category")

        # Delete existing website files
        resp = requests.delete(
            f"{STATIC_GEN_URL}/website/?category={category}&domain={domain}",
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            return jsonify({"error": resp.text}), 400

        # Post new website files
        resp = requests.post(
            f"{STATIC_GEN_URL}/website/?category={category}&domain={domain}",
            files={"zip": (f"{category}.zip", request.files["zip"])},
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            return jsonify({"error": resp.text}), 400

        # Remove temp files
        shutil.rmtree(f"tmp/{category}/", ignore_errors=True)

        return (
            jsonify(
                website_manager.update(
                    document_id=website_id,
                    data={
                        "category": category,
                        "s3_url": f"https://{WEBSITE_BUCKET}.s3.amazonaws.com/{domain}/",
                    },
                )
            ),
            200,
        )

    def delete(self, website_id):
        """Delete website content."""
        website = website_manager.get(document_id=website_id)

        name = website["name"]
        category = website["category"]
        resp = requests.delete(
            f"{STATIC_GEN_URL}/website/?category={category}&domain={name}",
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return {"error": str(e)}, 400

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

        # Switch instance to unavailable to prevent user actions
        website_manager.update(
            document_id=website_id,
            data={
                "is_available": False,
                "is_generating_template": True,
            },
        )

        try:
            domain = website["name"]

            # Generate website content from a template
            resp = requests.post(
                f"{STATIC_GEN_URL}/generate/?category={category}&domain={domain}",
                json=request.json,
            )

            # remove temp files
            shutil.rmtree("tmp/", ignore_errors=True)

            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as e:
                return jsonify({"error": str(e)}), 400

            website_manager.update(
                document_id=website_id,
                data={
                    "s3_url": f"https://{WEBSITE_BUCKET}.s3.amazonaws.com/{domain}/",
                    "category": category,
                    "is_available": True,
                    "is_generating_template": False,
                },
            )

            return jsonify(
                {
                    "message": f"{domain} static site has been created from the {category} template."
                }
            )
        except Exception as e:
            logger.exception(e)
            website_manager.update(
                document_id=website_id,
                data={
                    "is_available": True,
                    "is_generating_template": False,
                },
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

        data = validate_data(data, Redirect)

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

        data = validate_data(data, Redirect)

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
        subdomain = request.args.get("subdomain")
        if not subdomain:
            return {"error": "must pass subdomain as a request arg to delete."}
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

        # Switch instance to unavailable to prevent user actions
        website_manager.update(
            document_id=website_id,
            data={
                "is_available": False,
                "is_launching": True,
            },
        )
        try:
            # Create distribution, certificates, and dns records
            metadata = launch_site(website)

            data = {
                "is_active": True,
                "is_available": True,
                "is_launching": False,
            }
            data.update(metadata)
            website_manager.update(
                document_id=website_id,
                data=data,
            )
            name = website["name"]
            return jsonify({"success": f"{name} has been launched"})
        except Exception as e:
            logger.exception(e)
            # Switch instance to unavailable to prevent user actions
            website_manager.update(
                document_id=website_id,
                data={
                    "is_available": True,
                    "is_launching": False,
                },
            )

    def delete(self, website_id):
        """Stop a static site."""
        website = website_manager.get(document_id=website_id)

        # Switch instance to unavailable to prevent user actions
        website_manager.update(
            document_id=website_id,
            data={
                "is_available": False,
                "is_delaunching": True,
            },
        )
        try:
            # Delete distribution, certificates, and dns records
            resp = delete_site(website)

            website_manager.update(
                document_id=website_id,
                data={
                    "is_active": False,
                    "is_available": True,
                    "is_delaunching": False,
                },
            )

            website_manager.remove(
                document_id=website_id,
                data={"acm": "", "cloudfront": ""},
            )
            return jsonify(resp)
        except Exception as e:
            logger.exception(e)
            # Switch instance to unavailable to prevent user actions
            website_manager.update(
                document_id=website_id,
                data={
                    "is_available": True,
                    "is_delaunching": False,
                },
            )


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
        website = website_manager.get(document_id=website_id)
        domain = website["name"]
        if website.get("is_categorized", None):
            return {"error": f"{domain} has already been categorized."}

        category = category_manager.get(
            filter_data={"name": request.args.get("category", "").capitalize()}
        )

        if not category:
            return {"error": "Category does not exist"}

        is_category_submitted = []
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
                        proxy.get("script"),
                        {
                            "driver": driver,
                            "url": proxy.get("url"),
                            "domain": domain,
                            "api_key": two_captcha_api_key,
                            "category": proxy_category,
                        },
                    )
                    driver.quit()
                    is_category_submitted.append(
                        {
                            "_id": proxy["_id"],
                            "name": proxy_name,
                            "is_categorized": False,
                        }
                    )
                    logger.info(f"Categorized with {proxy_name}")
                except Exception as e:
                    driver.quit()
                    logger.exception(e)

        # Quit WebDriver
        driver.quit()

        # Update database
        website_manager.update(
            document_id=website_id,
            data={"is_category_submitted": is_category_submitted},
        )
        return jsonify(
            {"message": f"{domain} has been successfully submitted for categorization"}
        )
