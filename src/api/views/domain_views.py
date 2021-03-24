"""Domain Views."""
# Standard Python Libraries
from datetime import datetime
import io
from multiprocessing import Process
import shutil
from uuid import uuid4

# Third-Party Libraries
import boto3
from flask import g, jsonify, request, send_file
from flask.views import MethodView
import requests

# cisagov Libraries
from api.manager import ApplicationManager, DomainManager
from api.schemas.domain_schema import DomainSchema, Record
from settings import STATIC_GEN_URL, TAGS, WEBSITE_BUCKET, logger
from utils.aws import record_handler
from utils.aws.site_handler import launch_domain, unlaunch_domain
from utils.categorization.categorize import categorize
from utils.categorization.check import check_category
from utils.decorators.auth import can_access_domain
from utils.user_profile import get_users_group_ids
from utils.validator import validate_data

domain_manager = DomainManager()
application_manager = ApplicationManager()
route53 = boto3.client("route53")
sqs = boto3.client("sqs")
cloudfront = boto3.client("cloudfront")


class DomainsView(MethodView):
    """DomainsView."""

    def get(self):
        """Get all domains."""
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

        # tag resource
        hosted_zone_id = resp["HostedZone"]["Id"].strip("/hostedzone/")

        route53.change_tags_for_resource(
            ResourceType="hostedzone",
            ResourceId=hosted_zone_id,
            AddTags=TAGS,
        )

        # save to db
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
        return jsonify(resp["DelegationSet"]["NameServers"])


class DomainView(MethodView):
    """DomainView."""

    decorators = [can_access_domain]

    def get(self, domain_id):
        """Get Domain details."""
        domain = domain_manager.get(document_id=domain_id)
        if "application_id" in domain:
            application = application_manager.get(document_id=domain["application_id"])
            domain["application_name"] = application["name"]
        return jsonify(domain)

    def put(self, domain_id):
        """Update domain."""
        data = validate_data(request.json, DomainSchema)
        domain = domain_manager.get(document_id=domain_id)

        if not g.is_admin:
            data.pop("application_id", None)
            data.pop("history", None)

        if "application_id" in data:
            if not data["application_id"]:
                data["history"] = domain.get("history", [])
                for history in data["history"]:
                    if not history.get("end_date"):
                        history["end_date"] = datetime.utcnow()
            elif data["application_id"] != domain.get("application_id", ""):
                application = application_manager.get(data["application_id"])
                data["history"] = domain.get("history", [])
                for history in data["history"]:
                    if not history.get("end_date"):
                        history["end_date"] = datetime.utcnow()
                data["history"].append(
                    {
                        "application": application,
                        "start_date": datetime.utcnow(),
                    }
                )

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

            post_data = request.json
            post_data["domain"] = domain_name

            # Generate website content from a template
            resp = requests.post(
                f"{STATIC_GEN_URL}/generate/?category={category}&domain={domain_name}",
                json=post_data,
            )

            # remove temp files
            shutil.rmtree("tmp/", ignore_errors=True)

            resp.raise_for_status()

            domain_manager.update(
                document_id=domain_id,
                data={
                    "s3_url": f"https://{WEBSITE_BUCKET}.s3.amazonaws.com/{domain_name}/",
                    "category": category,
                    "is_available": True,
                    "is_generating_template": False,
                },
            )
            return jsonify(
                {
                    "message": f"{domain_name} static site has been created from the {category} template."
                }
            )
        except Exception as e:
            logger.exception(e)
            domain_manager.update(
                document_id=domain_id,
                data={
                    "is_available": True,
                    "is_generating_template": False,
                },
            )
            return jsonify({"error": "Error generating from template."}), 400


class DomainLaunchView(MethodView):
    """Launch or stop an existing static site by adding dns records to its domain."""

    decorators = [can_access_domain]

    def get(self, domain_id):
        """Launch a static site."""
        domain = domain_manager.get(document_id=domain_id)

        if not domain["is_available"]:
            return "Domain is not available for launching at the moment.", 400

        task = Process(target=launch_domain, args=(domain,))
        task.start()
        return jsonify({"success": "Site is launching in the background."})

    def delete(self, domain_id):
        """Stop a static site."""
        domain = domain_manager.get(document_id=domain_id)

        if not domain["is_available"]:
            return "Domain is not available for unlaunching at the moment.", 400

        task = Process(target=unlaunch_domain, args=(domain,))
        task.start()
        return jsonify({"success": "Site is unlaunching in the background."})


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
        record_handler.manage_record("CREATE", domain["route53"]["id"], data)
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
        record_handler.manage_record("DELETE", domain["route53"]["id"], record)
        resp = domain_manager.delete_from_list(
            document_id=domain_id, field="records", data={"record_id": record_id}
        )
        return jsonify(resp)


class DomainCategorizeView(MethodView):
    """DomainCategorizeView."""

    decorators = [can_access_domain]

    def get(self, domain_id):
        """Categorize Domain."""
        domain = domain_manager.get(document_id=domain_id, fields=["name"])

        task = Process(target=check_category, args=(domain["name"],))
        task.start()
        return jsonify(
            {
                "success": "Site is being checked in the background. Check back later for results and failures."
            }
        )

    def post(self, domain_id):
        """Categorize Domain."""
        domain = domain_manager.get(document_id=domain_id, fields=["name"])
        category = request.json["category"]

        if domain.get("submitted_category"):
            return "Domain has already had a category submitted.", 400

        task = Process(target=categorize, args=(category, domain["name"]))
        task.start()

        domain_manager.update(
            document_id=domain["_id"], data={"submitted_category": category}
        )

        return jsonify(
            {
                "success": "Site is being categorized in the background. Check back later for any failures in the categorization process."
            }
        )

    def put(self, domain_id):
        """Manually categorize a domain."""
        domain = domain_manager.get(document_id=domain_id)
        proxy = request.json["proxy"]

        domain_manager.update_in_list(
            document_id=domain["_id"],
            field="category_results.$.is_submitted",
            data=True,
            params={"category_results.proxy": proxy},
        )

        domain_manager.update_in_list(
            document_id=domain["_id"],
            field="category_results.$.manually_submitted",
            data=True,
            params={"category_results.proxy": proxy},
        )

        return jsonify({"success": "Site has been manually categorized."})


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
