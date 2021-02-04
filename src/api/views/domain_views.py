"""Domain Views."""
# Standard Python Libraries
from datetime import datetime
import io
import os
import shutil
from uuid import uuid4

# Third-Party Libraries
import boto3
from flask import current_app, g, jsonify, request, send_file
from flask.views import MethodView
import requests
from selenium import webdriver

# cisagov Libraries
from api.manager import ApplicationManager, CategoryManager, DomainManager, ProxyManager
from api.schemas.domain_schema import DomainSchema, Record
from settings import STATIC_GEN_URL, WEBSITE_BUCKET, logger
from utils.aws import record_handler
from utils.aws.site_handler import delete_site, launch_site
from utils.categorization import (
    bluecoat,
    ciscotalos,
    fortiguard,
    ibmxforce,
    trustedsource,
    websense,
)
from utils.decorators.auth import can_access_domain
from utils.two_captcha import two_captcha_api_key
from utils.user_profile import add_user_action, get_users_group_ids
from utils.validator import validate_data

category_manager = CategoryManager()
proxy_manager = ProxyManager()
domain_manager = DomainManager()
application_manager = ApplicationManager()
route53 = boto3.client("route53")
cloudfront = boto3.client("cloudfront")


class DomainsView(MethodView):
    """DomainsView."""

    def get(self):
        """Get all domains."""
        add_user_action("Get Domains")

        if g.is_admin:
            response = domain_manager.all(params=request.args)
        else:
            groups = get_users_group_ids()
            response = domain_manager.all(params={"application_id": {"$in": groups}})

        return jsonify(response)

    def post(self):
        """Create a new domain."""
        if not g.is_admin:
            return (
                jsonify(
                    {
                        "error": "User does not have admin rights, can not create a new domain"
                    }
                ),
                400,
            )

        data = validate_data(request.json, DomainSchema)
        if domain_manager.get(filter_data={"name": data["name"]}):
            return jsonify({"error": "Domain already exists."}), 400
        caller_ref = str(uuid4())
        resp = route53.create_hosted_zone(Name=data["name"], CallerReference=caller_ref)
        domain_manager.save(
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
        add_user_action(f"Created New Domain - {data['name']}")
        return jsonify(resp["DelegationSet"]["NameServers"])


class DomainView(MethodView):
    """DomainView."""

    decorators = [can_access_domain]

    def get(self, domain_id):
        """Get Domain details."""
        domain = domain_manager.get(document_id=domain_id)
        add_user_action(f"View Domain - {domain['name']}")
        if "application_id" in domain:
            application = application_manager.get(document_id=domain["application_id"])
            domain["application_name"] = application["name"]
        return jsonify(domain)

    def put(self, domain_id):
        """Update domain."""
        data = validate_data(request.json, DomainSchema)
        domain = domain_manager.get(document_id=domain_id)

        if data.get("application"):
            application = application_manager.get(
                filter_data={"name": data["application"]}
            )
            data["application_id"] = application["_id"]
            # Save application to history
            data["history"] = domain.get("history", [])
            data["history"].append(
                {
                    "application": application,
                    "launch_date": datetime.utcnow(),
                }
            )

        add_user_action(f"Update Domain - {domain['name']}")
        return jsonify(domain_manager.update(document_id=domain_id, data=data))

    def delete(self, domain_id):
        """Delete domain and hosted zone."""
        domain = domain_manager.get(document_id=domain_id)

        if domain.get("is_active") and domain.get("records"):
            return jsonify(
                {"message": "Domain cannot be active and redirects must be removed."}
            )

        if domain.get("category"):
            category = domain["category"]
            name = domain["name"]
            requests.delete(
                f"{STATIC_GEN_URL}/website/?category={category}&domain={name}",
            )

        route53.delete_hosted_zone(Id=domain["route53"]["id"])
        add_user_action(f"Delete Domain - {domain['name']}")
        return jsonify(domain_manager.delete(domain["_id"]))


class DomainContentView(MethodView):
    """DomainContentView."""

    decorators = [can_access_domain]

    def get(self, domain_id):
        """Download Domain."""
        domain = domain_manager.get(document_id=domain_id)

        resp = requests.get(
            f"{STATIC_GEN_URL}/website/?category={domain['category']}&domain={domain['name']}",
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return {"error": str(e)}, 400

        buffer = io.BytesIO()
        buffer.write(resp.content)
        buffer.seek(0)

        add_user_action(f"Download Domain - {domain['name']}")

        return send_file(
            buffer,
            as_attachment=True,
            attachment_filename=f"{domain['name']}.zip",
            mimetype="application/zip",
        )

    def post(self, domain_id):
        """Upload files and serve s3 site."""
        # Get domain data
        domain = domain_manager.get(document_id=domain_id)

        domain_name = domain["name"]
        category = request.args.get("category")

        # Delete existing website files
        resp = requests.delete(
            f"{STATIC_GEN_URL}/website/?category={category}&domain={domain_name}",
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            return jsonify({"error": resp.text}), 400

        # Post new website files
        resp = requests.post(
            f"{STATIC_GEN_URL}/website/?category={category}&domain={domain_name}",
            files={"zip": (f"{category}.zip", request.files["zip"])},
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            return jsonify({"error": resp.text}), 400

        # Remove temp files
        shutil.rmtree(f"tmp/{category}/", ignore_errors=True)

        add_user_action(f"Upload Domain - {domain['name']}")

        return (
            jsonify(
                domain_manager.update(
                    document_id=domain_id,
                    data={
                        "category": category,
                        "s3_url": f"https://{WEBSITE_BUCKET}.s3.amazonaws.com/{domain_name}/",
                    },
                )
            ),
            200,
        )

    def delete(self, domain_id):
        """Delete domain content."""
        domain = domain_manager.get(document_id=domain_id)

        name = domain["name"]
        category = domain["category"]
        resp = requests.delete(
            f"{STATIC_GEN_URL}/website/?category={category}&domain={name}",
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return {"error": str(e)}, 400

        add_user_action(f"Delete Domain Content - {domain['name']}")
        return jsonify(
            domain_manager.remove(
                document_id=domain_id, data={"category": "", "s3_url": ""}
            )
        )


class DomainGenerateView(MethodView):
    """DomainGenerateView."""

    decorators = [can_access_domain]

    def post(self, domain_id):
        """Create website."""
        category = request.args.get("category")
        domain = domain_manager.get(document_id=domain_id)

        # Switch instance to unavailable to prevent user actions
        domain_manager.update(
            document_id=domain_id,
            data={
                "is_available": False,
                "is_generating_template": True,
            },
        )

        try:
            domain_name = domain["name"]

            # Generate website content from a template
            resp = requests.post(
                f"{STATIC_GEN_URL}/generate/?category={category}&domain={domain_name}",
                json=request.json,
            )

            # remove temp files
            shutil.rmtree("tmp/", ignore_errors=True)

            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as e:
                return jsonify({"error": str(e)}), 400

            domain_manager.update(
                document_id=domain_id,
                data={
                    "s3_url": f"https://{WEBSITE_BUCKET}.s3.amazonaws.com/{domain_name}/",
                    "category": category,
                    "is_available": True,
                    "is_generating_template": False,
                },
            )

            add_user_action(
                f"Generate domain content from template - Template: {category} - Website {domain['name']}"
            )
            return jsonify(
                {
                    "message": f"{domain_name} static site has been created from the {category} template."
                }
            )
        except Exception as e:
            logger.exception(e)
            return jsonify({"error": "Error generating from template."}), 400
            domain_manager.update(
                document_id=domain_id,
                data={
                    "is_available": True,
                    "is_generating_template": False,
                },
            )


class DomainLaunchView(MethodView):
    """Launch or stop an existing static site by adding dns records to its domain."""

    decorators = [can_access_domain]

    def get(self, domain_id):
        """Launch a static site."""
        domain = domain_manager.get(document_id=domain_id)

        # Switch instance to unavailable to prevent user actions
        domain_manager.update(
            document_id=domain_id,
            data={
                "is_available": False,
                "is_launching": True,
            },
        )
        try:
            # Create distribution, certificates, and dns records
            metadata = launch_site(domain)

            data = {
                "is_active": True,
                "is_available": True,
                "is_launching": False,
            }
            data.update(metadata)
            domain_manager.update(
                document_id=domain_id,
                data=data,
            )
            name = domain["name"]
            add_user_action(f"Launch Domain - {name}")
            return jsonify({"success": f"{name} has been launched"})
        except Exception as e:
            add_user_action(f"Launch Domain - FAILED {domain['name']}")
            logger.exception(e)
            # Switch instance to unavailable to prevent user actions
            domain_manager.update(
                document_id=domain_id,
                data={
                    "is_available": True,
                    "is_launching": False,
                },
            )

    def delete(self, domain_id):
        """Stop a static site."""
        domain = domain_manager.get(document_id=domain_id)

        # Switch instance to unavailable to prevent user actions
        domain_manager.update(
            document_id=domain_id,
            data={
                "is_available": False,
                "is_delaunching": True,
            },
        )
        try:
            # Delete distribution, certificates, and dns records
            resp = delete_site(domain)

            domain_manager.update(
                document_id=domain_id,
                data={
                    "is_active": False,
                    "is_available": True,
                    "is_delaunching": False,
                },
            )

            domain_manager.remove(
                document_id=domain_id,
                data={"acm": "", "cloudfront": ""},
            )
            add_user_action(f"Take down a Domain site - {domain['name']}")
            return jsonify(resp)
        except Exception as e:
            logger.exception(e)
            # Switch instance to unavailable to prevent user actions
            domain_manager.update(
                document_id=domain_id,
                data={
                    "is_available": True,
                    "is_delaunching": False,
                },
            )


class DomainRecordView(MethodView):
    """View for interacting with website hosted zone records."""

    decorators = [can_access_domain]

    def get(self, domain_id):
        """Get the hosted zone records for a domain."""
        hosted_zone_id = domain_manager.get(document_id=domain_id, fields=["route53"])[
            "route53"
        ]["id"]
        resp = route53.list_resource_record_sets(HostedZoneId=hosted_zone_id)
        return jsonify(resp["ResourceRecordSets"])

    def post(self, domain_id):
        """Create a new record in the hosted zone."""
        data = validate_data(request.json, Record)
        data["record_id"] = str(uuid4())
        domain = domain_manager.get(document_id=domain_id)
        record_handler.add_record(domain["route53"]["id"], data)
        resp = domain_manager.add_to_list(
            document_id=domain_id, field="records", data=data
        )
        return jsonify(resp)

    def delete(self, domain_id):
        """Delete the hosted zone record."""
        record_id = request.args.get("record_id")
        if not record_id:
            return jsonify({"error": "Must supply record id in request args."}), 400
        domain = domain_manager.get(document_id=domain_id)
        record = next(
            filter(lambda x: x["record_id"] == record_id, domain.get("records", []))
        )
        if not record:
            return jsonify({"error": "No record with matching id found."}), 400
        record_handler.delete_record(domain["route53"]["id"], record)
        resp = domain_manager.delete_from_list(
            document_id=domain_id, field="records", data={"record_id": record_id}
        )
        return jsonify(resp)


class DomainCategorizeView(MethodView):
    """DomainCategorizeView."""

    decorators = [can_access_domain]

    def get(self, domain_id):
        """Manage categorization of active sites."""
        browserless_endpoint = os.environ.get("BROWSERLESS_ENDPOINT")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        domain = domain_manager.get(document_id=domain_id)
        domain_name = domain["name"]

        category = category_manager.get(
            filter_data={"name": request.args.get("category", "").capitalize()}
        )

        if domain.get("is_categorized", None):
            return {"error": f"{domain_name} has already been categorized."}

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
                            "domain": domain_name,
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
        domain_manager.update(
            document_id=domain_id,
            data={"is_category_submitted": is_category_submitted},
        )
        add_user_action(
            f"Categorize domain - domain: {domain['name']} - category: {category}"
        )
        return jsonify(
            {
                "message": f"{domain_name} has been successfully submitted for categorization"
            }
        )


class DomainCategoryCheckView(MethodView):
    """DomainCategoryCheckView."""

    decorators = [can_access_domain]

    def update_submission(self, query, dicts):
        """Search through existing submissions and check as categorized."""
        next(
            item.update({"is_categorized": True})
            for item in dicts
            if item["name"] == query
        )
        if not any(item["name"] == query for item in dicts):
            dicts.append({"name": query, "is_categorized": True})

    def get(self, domain_id):
        """Check category for a domain."""
        domain = domain_manager.get(document_id=domain_id)

        if not domain.get("is_category_submitted", None):
            return jsonify(
                {"error": "website has not yet been submitted for categorization"}
            )

        domain_name = domain["name"]

        # Trusted source
        ts = trustedsource.check_category(domain_name)
        if ts is not None:
            self.update_submission("Trusted Source", domain["is_category_submitted"])

        # Bluecoat
        bc = bluecoat.check_category(domain_name)
        if bc is not None:
            self.update_submission("Blue Coat", domain["is_category_submitted"])

        # Cisco Talos
        ct = ciscotalos.check_category(domain_name)
        if ct is not None:
            self.update_submission("Cisco Talos", domain["is_category_submitted"])

        # IBM X Force
        ixf = ibmxforce.check_category(domain_name)
        if ixf is not None:
            self.update_submission("IBM X Force", domain["is_category_submitted"])

        # Fortiguard
        fg = fortiguard.check_category(domain_name)
        if fg is not None:
            self.update_submission("Fortiguard", domain["is_category_submitted"])

        # Websense
        ws = websense.check_category(domain_name)
        if ws is not None:
            self.update_submission("Websense", domain["is_category_submitted"])

        # Update database
        domain_manager.update(
            document_id=domain_id,
            data={"is_category_submitted": domain["is_category_submitted"]},
        )
        return jsonify(
            {
                "Trusted Source": ts,
                "Bluecoat": bc,
                "Cisco Talos": ct,
                "IBM X-Force": ixf,
                "Fortiguard": fg,
                "Websense": ws,
            }
        )


class DomainDeployedCheckView(MethodView):
    """DomainCategoryCheckView."""

    decorators = [can_access_domain]

    def get(self, domain_id):
        """Check the cloudfront deployment status of the domain."""
        domain = domain_manager.get(document_id=domain_id)
        if domain.get("cloudfront", {}).get("id"):
            results = cloudfront.get_distribution(Id=domain["cloudfront"]["id"])
            return jsonify(results["Distribution"])
        else:
            return (
                jsonify(
                    {
                        "error": "Error getting cloudfront status of domain, cloudfront data not assigned"
                    }
                ),
                400,
            )
