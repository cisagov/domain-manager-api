"""Template Views."""
# Standard Python Libraries
import io
import shutil
import urllib

# Third-Party Libraries
from flask import g, jsonify, request, send_file
from flask.views import MethodView
from marshmallow import ValidationError
import requests

# cisagov Libraries
from api.manager import TemplateManager
from api.schemas.template_schema import TemplateSchema
from settings import STATIC_GEN_URL, TEMPLATE_BUCKET, logger
from utils.validator import validate_data

template_manager = TemplateManager()


class TemplatesView(MethodView):
    """TemplatesView."""

    def get(self):
        """Get all templates."""
        return jsonify(template_manager.all())

    def post(self):
        """Create new template."""
        rvalues = []
        name = ""
        for f in request.files.getlist("zip"):
            if not f.filename.endswith(".zip") or " " in f.filename:
                continue
            name = f.filename[:-4]
            try:
                validate_data({"name": name}, TemplateSchema)
            except ValidationError:
                continue
            url_escaped_name = urllib.parse.quote_plus(name)
            resp = requests.post(
                f"{STATIC_GEN_URL}/template/?category={url_escaped_name}",
                files={"zip": (f"{f.filename}", f)},
            )

            # remove temp files
            shutil.rmtree(f"tmp/{url_escaped_name}/", ignore_errors=True)

            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError:
                logger.error(resp.text)
                return jsonify({"error": resp.text}), 400

            post_data = {
                "name": name,
                "s3_url": f"{TEMPLATE_BUCKET}.s3.amazonaws.com/{name}/",
                "is_approved": False,
                "is_go_template": True,
            }

            if g.is_admin:
                post_data["is_approved"] = True

            try:
                template_manager.save(post_data)
            except Exception as e:
                logger.exception(e)
            rvalues.append(post_data)

        return jsonify(rvalues, 200)


class TemplateView(MethodView):
    """TemplateView."""

    def get(self, template_id):
        """Get template details."""
        template = template_manager.get(document_id=template_id)
        return jsonify(template)

    def delete(self, template_id):
        """Delete template."""
        if not g.is_admin:
            return jsonify({"error": "Only admins may delete templates."}), 400

        template = template_manager.get(document_id=template_id)

        template_name = template["name"]
        resp = requests.delete(f"{STATIC_GEN_URL}/template/?category={template_name}")

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return jsonify({"error": str(e)})

        return jsonify(template_manager.delete(document_id=template_id))


class TemplateContentView(MethodView):
    """TemplateContentView."""

    def get(self, template_id):
        """Download template."""
        template = template_manager.get(document_id=template_id)
        resp = requests.get(f"{STATIC_GEN_URL}/template/?category={template['name']}")

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return jsonify({"error": str(e)})

        # Create buffer
        buffer = io.BytesIO()
        buffer.write(resp.content)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            attachment_filename=f"{template['name']}.zip",
            mimetype="application/zip",
        )


class TemplateAttributesView(MethodView):
    """TemplateKeysView."""

    def get(self):
        """Get list of keys for template context."""
        return jsonify(
            [
                "address",
                "city",
                "description",
                "email",
                "name",
                "phone",
                "state",
            ]
        )


class TemplateApprovalView(MethodView):
    """Template approval view."""

    def get(self, template_id):
        """Approve a template pending for review."""
        template = template_manager.get(document_id=template_id)

        if template.get("is_approved", False):
            return jsonify({"error": "This template is already approved"}), 400

        return jsonify(
            template_manager.update(document_id=template_id, data={"is_approved": True})
        )

    def delete(self, template_id):
        """Disapprove a previously approved template."""
        template = template_manager.get(document_id=template_id)

        if not template.get("is_approved", True):
            return jsonify({"error": "This template is not yet approved"}), 400

        return jsonify(
            template_manager.update(
                document_id=template_id, data={"is_approved": False}
            )
        )
