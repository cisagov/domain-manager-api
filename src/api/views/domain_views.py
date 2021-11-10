"""Domain Views."""
# Standard Python Libraries
from datetime import datetime
from http import HTTPStatus
import io
from multiprocessing import Process
import shutil
from uuid import uuid4

# Third-Party Libraries
import botocore
from botocore.exceptions import ClientError
from flask import abort, g, jsonify, request, send_file
from flask.views import MethodView
from marshmallow.exceptions import ValidationError
import requests  # type: ignore

# cisagov Libraries
from api.config import STATIC_GEN_URL, WEBSITE_BUCKET, logger
from api.manager import (
    ApplicationManager,
    CategorizationManager,
    DomainManager,
    EmailManager,
    TemplateManager,
)
from api.schemas.domain_schema import DomainSchema, Record
from utils.apex_records import contains_apex_record, is_apex_record
from utils.aws import record_handler
from utils.aws.clients import Cloudfront, Route53
from utils.aws.ses import disable_email_receiving, enable_email_receiving
from utils.aws.site_handler import (
    launch_domain,
    unlaunch_domain,
    verify_hosted_zone,
    verify_launch_records,
)
from utils.categorization.categorize import (
    delete_domain_proxies,
    get_domain_proxies,
    post_categorize_request,
    put_proxy_status,
)
from utils.decorators.auth import can_access_domain
from utils.users import get_users_group_ids
from utils.validator import validate_data

categorization_manager = CategorizationManager()
domain_manager = DomainManager()
template_manager = TemplateManager()
email_manager = EmailManager()

application_manager = ApplicationManager()
route53 = Route53()
cloudfront = Cloudfront()


class DomainsView(MethodView):
    """DomainsView."""

    def get(self):
        """Get all domains."""
        params = dict(request.args)
        if g.is_admin:
            response = domain_manager.all(params=params)
        else:
            groups = get_users_group_ids()
            params.update({"application_id": {"$in": groups}})
            response = domain_manager.all(params=params)

        applications = application_manager.all()

        for domain in response:
            if domain.get("application_id"):
                domain["application_name"] = next(
                    filter(lambda x: x["_id"] == domain["application_id"], applications)
                )["name"]

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
        response = {}
        for domain_name in request.json:
            # Catch errors validation domain name
            try:
                data = validate_data({"name": domain_name}, DomainSchema)
            except ValidationError as e:
                logger.exception(e)
                response[domain_name] = "Error: Invalid Domain"
                continue

            # Catch error if domain already exists.
            if domain_manager.get(filter_data={"name": data["name"]}):
                logger.error(f"{domain_name} already exists.")
                response[domain_name] = "Error: Domain already exists."
                continue

            try:
                resp = route53.create_hosted_zone(data["name"])
            except ClientError as e:
                logger.exception(e)
                response[domain_name] = f"Error: {e.response['Error']['Message']}"
                continue

            # save to db
            domain_manager.save(
                {
                    "name": domain_name,
                    "is_active": False,
                    "is_approved": False,
                    "is_available": True,
                    "is_launching": False,
                    "is_delaunching": False,
                    "is_generating_template": False,
                    "route53": {"id": resp["HostedZone"]["Id"]},
                }
            )
            response[domain_name] = resp["DelegationSet"]["NameServers"]
        return jsonify(response)


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
        if not g.is_admin:
            abort(HTTPStatus.FORBIDDEN.value)

        domain = domain_manager.get(document_id=domain_id)

        if domain.get("is_active") and domain.get("records"):
            return jsonify(
                {"message": "Domain cannot be active and redirects must be removed."}
            )

        name = domain["name"]
        requests.delete(
            f"{STATIC_GEN_URL}/website/?domain={name}",
        )

        try:
            route53.delete_hosted_zone(domain["route53"]["id"])
        except ClientError as e:
            logger.error(e.response)
            if e.response["Error"]["Code"] == "NoSuchHostedZone":
                logger.info("Hosted zone doesn't exist.")
            else:
                raise e

        categorization_manager.delete(params={"domain_id": domain["_id"]})

        return jsonify(domain_manager.delete(domain["_id"]))


class DomainContentView(MethodView):
    """DomainContentView."""

    decorators = [can_access_domain]

    def get(self, domain_id):
        """Download website content."""
        domain = domain_manager.get(document_id=domain_id)

        resp = requests.get(
            f"{STATIC_GEN_URL}/website/?template_name={domain['template_name']}&domain={domain['name']}",
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
        template_name = request.args.get("template_name")

        post_data = {
            "template_name": template_name,
            "s3_url": f"https://{WEBSITE_BUCKET}.s3.amazonaws.com/{domain_name}/",
        }

        # Content automatically approved if uploaded by admins
        if g.is_admin:
            post_data["is_approved"] = True

        # Delete existing website files
        resp = requests.delete(
            f"{STATIC_GEN_URL}/website/?domain={domain_name}",
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            return jsonify({"error": resp.text}), 400

        # Post new website files
        resp = requests.post(
            f"{STATIC_GEN_URL}/website/?template_name={template_name}&domain={domain_name}",
            files={"zip": (f"{template_name}.zip", request.files["zip"])},
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            return jsonify({"error": resp.text}), 400

        # Remove temp files
        shutil.rmtree(f"tmp/{template_name}/", ignore_errors=True)

        return (
            jsonify(
                domain_manager.update(
                    document_id=domain_id,
                    data=post_data,
                )
            ),
            200,
        )

    def delete(self, domain_id):
        """Delete domain content."""
        domain = domain_manager.get(document_id=domain_id)

        name = domain["name"]
        resp = requests.delete(
            f"{STATIC_GEN_URL}/website/?domain={name}",
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return {"error": str(e)}, 400

        return jsonify(
            domain_manager.remove(
                document_id=domain_id,
                data={
                    "template_name": "",
                    "is_approved": False,
                    "s3_url": "",
                },
            )
        )


class DomainGenerateView(MethodView):
    """Generate static content from a template."""

    decorators = [can_access_domain]

    def post(self, domain_id):
        """Create website."""
        template_name = request.args.get("template_name")

        template = template_manager.get(filter_data={"name": template_name})

        if not template.get("is_approved", False):
            return jsonify({"error": "Template is not authorized for use."}), 401

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

            is_go_template = "true" if template.get("is_go_template", True) else "false"

            # Generate website content from a template
            resp = requests.post(
                f"{STATIC_GEN_URL}/generate/?template_name={template_name}&domain={domain_name}&is_template={is_go_template}",
                json=post_data,
            )

            # remove temp files
            shutil.rmtree("tmp/", ignore_errors=True)

            resp.raise_for_status()

            post_data = {
                "s3_url": f"https://{WEBSITE_BUCKET}.s3.amazonaws.com/{domain_name}/",
                "template_name": template_name,
                "is_approved": True,
                "is_available": True,
                "is_generating_template": False,
            }

            domain_manager.update(
                document_id=domain_id,
                data=post_data,
            )
            return jsonify(
                {
                    "message": f"{domain_name} static site has been created from the {template_name} template."
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

        if not domain.get("is_approved", False):
            return (
                "Website content is not approved. Please reach out to an admin for approval.",
                400,
            )

        try:
            verify_hosted_zone(domain)
            verify_launch_records(domain)
        except Exception as e:
            return str(e), 400

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
        resp = route53.list_resource_record_sets(hosted_zone_id)
        return jsonify(resp["ResourceRecordSets"])

    def post(self, domain_id):
        """Create a new record in the hosted zone."""
        try:
            data = validate_data(request.json, Record)
        except ValidationError as e:
            logger.exception(e)
            return str(e), 400
        data["record_id"] = str(uuid4())

        domain = domain_manager.get(document_id=domain_id)
        try:
            record_handler.manage_record("CREATE", domain["route53"]["id"], data)
        except botocore.exceptions.ClientError as error:
            logger.exception(error)
            if error.response["Error"]["Code"] == "InvalidChangeBatch":
                return error.response["Error"]["Message"], 400
            else:
                raise error
        resp = domain_manager.add_to_list(
            document_id=domain_id, field="records", data=data
        )

        if is_apex_record(record=data, domain_name=domain["name"]):
            domain_manager.update(
                document_id=domain_id,
                data={
                    "is_active": True,
                },
            )
        return jsonify(resp)

    def delete(self, domain_id):
        """Delete the hosted zone record."""
        record_id = request.args.get("record_id")
        if not record_id:
            return jsonify({"error": "Must supply record_id in request args."}), 400
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

        if record["record_type"] == "A" and record["name"] == domain["name"]:
            domain_manager.update(
                document_id=domain_id,
                data={
                    "is_active": False,
                },
            )
        return jsonify(resp)

    def put(self, domain_id):
        """Modify the hosted zone record."""
        record_id = request.args.get("record_id")
        if not record_id:
            return jsonify({"error": "Must supply record_id in request args."}), 400
        domain = domain_manager.get(document_id=domain_id)
        record = next(
            filter(lambda x: x["record_id"] == record_id, domain.get("records", []))
        )
        if not record:
            return jsonify({"error": "No record with matching id found."}), 400

        try:
            data = validate_data(request.json, Record)
        except ValidationError as e:
            logger.exception(e)
            return str(e), 400
        record["config"] = data["config"]
        record_handler.manage_record("UPSERT", domain["route53"]["id"], record)
        domain_manager.update_in_list(
            document_id=domain["_id"],
            field="records.$.config",
            data=record["config"],
            params={"records.record_id": record_id},
        )
        return jsonify({"success": "Record has been updated."})


class DomainCategorizeView(MethodView):
    """DomainCategorizeView."""

    decorators = [can_access_domain]

    def get(self, domain_id):
        """Get categories on domains."""
        resp, status_code = get_domain_proxies(domain_id)
        return jsonify(resp), status_code

    def post(self, domain_id):
        """Submit a Domain for Categorization."""
        category = request.json.get("category")

        if not category:
            return jsonify({"error": "Please specify a requested category."}), 406

        domain = domain_manager.get(document_id=domain_id)

        if domain.get("rejected_msg"):
            domain_manager.update(document_id=domain_id, data={"rejected_msg": None})

        resp, status_code = post_categorize_request(
            domain_id=domain_id, domain_name=domain["name"], requested_category=category
        )

        return jsonify(resp), status_code

    def put(self, domain_id):
        """Verify a domain has been categorized."""
        status = request.json.get("status")

        if not status:
            return jsonify({"error": "Please specify a proxy status"}), 406

        category = request.json.get("category")

        if not category:
            return jsonify({"error": "Please specify a category"}), 406

        resp, status_code = put_proxy_status(
            domain_id=domain_id, status=status, category=category
        )

        return jsonify(resp), status_code

    def delete(self, domain_id):
        """Delete proxies for a domain."""
        resp, status_code = delete_domain_proxies(domain_id)
        domain_manager.update(
            document_id=domain_id, data={"rejected_msg": request.json.get("message")}
        )
        return jsonify(resp), status_code


class DomainDeployedCheckView(MethodView):
    """DomainDeployedCheckView."""

    decorators = [can_access_domain]

    def get(self, domain_id):
        """Check the cloudfront deployment status of the domain."""
        domain = domain_manager.get(document_id=domain_id)
        if domain.get("cloudfront", {}).get("id"):
            results = cloudfront.get_distribution(domain["cloudfront"]["id"])
            return jsonify(results["Distribution"])
        elif contains_apex_record(domain):
            return jsonify({"Status": "Externally Deployed"})
        else:
            return (
                jsonify(
                    {
                        "error": "Error getting cloudfront status of domain, cloudfront data not assigned"
                    }
                ),
                400,
            )


class DomainApprovalView(MethodView):
    """Domain approval view."""

    def get(self, domain_id):
        """Approve uploaded content pending for review."""
        domain = domain_manager.get(document_id=domain_id)

        if domain.get("is_approved", False):
            return jsonify({"error": "This content is already approved"}), 400

        return jsonify(
            domain_manager.update(document_id=domain_id, data={"is_approved": True})
        )

    def delete(self, domain_id):
        """Disapprove previously approved content."""
        domain = domain_manager.get(document_id=domain_id)

        if not domain.get("is_approved", True):
            return jsonify({"error": "This content is not yet approved"}), 400

        return jsonify(
            domain_manager.update(document_id=domain_id, data={"is_approved": False})
        )


class DomainReceiveEmailsView(MethodView):
    """Enable or disable the ability to receive emails via SES."""

    decorators = [can_access_domain]

    def get(self, domain_id):
        """Enable ability to receive emails."""
        domain = domain_manager.get(document_id=domain_id)

        if domain.get("is_email_active"):
            return jsonify({"message": "Email receiving is already active."}), 400

        resp = enable_email_receiving(domain["name"])
        domain_manager.update(document_id=domain_id, data={"is_email_active": True})
        return (
            jsonify({"success": resp}),
            200,
        )

    def delete(self, domain_id):
        """Disable ability to receive emails."""
        domain = domain_manager.get(document_id=domain_id)
        resp = disable_email_receiving(domain["name"])
        domain_manager.update(document_id=domain_id, data={"is_email_active": False})
        return (
            jsonify({"success": resp}),
            200,
        )


class DomainEmailsView(MethodView):
    """Domain Emails List View."""

    def get(self, domain_id):
        """Get all emails for a domain."""
        return (
            jsonify(
                email_manager.all(
                    params={"domain_id": domain_id},
                    fields=["_id", "from_address", "subject", "is_read", "timestamp"],
                )
            ),
            200,
        )


class DomainEmailView(MethodView):
    """Domain Email Detail View."""

    def get(self, email_id):
        """Get an email's details for a domain."""
        email_manager.update(
            document_id=email_id,
            data={"is_read": True},
        )
        return jsonify(email_manager.get(document_id=email_id)), 200

    def delete(self, email_id):
        """Delete an email for a domain."""
        return jsonify(email_manager.delete(email_id)), 200
