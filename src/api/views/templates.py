"""Template Views."""
# Standard Python Libraries
import io
import shutil
import urllib

# Third-Party Libraries
from flask import jsonify, request, send_file
from flask.views import MethodView
import requests

# cisagov Libraries
from api.manager import TemplateManager
from settings import STATIC_GEN_URL, TEMPLATE_BUCKET, logger

template_manager = TemplateManager()


class TemplatesView(MethodView):
    """TemplatesView."""

    def get(self):
        """Get all templates."""
        return jsonify(template_manager.all())

    def post(self):
        """Create new template."""
        rvalues = []
        for f in request.files.getlist("zip"):
            if not f.filename.endswith(".zip"):
                continue
            name = f.filename[:-4]
            url_escaped_name = urllib.parse.quote_plus(name)
            resp = requests.post(
                f"{STATIC_GEN_URL}/template/?category={url_escaped_name}",
                files={"zip": (f"{f.filename}", f)},
            )
            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as e:
                return jsonify({"error": str(e)})

            # remove temp files
            shutil.rmtree(f"tmp/{url_escaped_name}/", ignore_errors=True)

            s3_url = f"{TEMPLATE_BUCKET}.s3.amazonaws.com/{name}/"
            try:
                template_manager.save(
                    {
                        "name": name,
                        "s3_url": s3_url,
                    }
                )
            except Exception as e:
                logger.exception(e)
            rvalues.append({"name": name, "s3_url": s3_url})

        return jsonify(rvalues, 200)


class TemplateView(MethodView):
    """TemplateView."""

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

    def delete(self, template_id):
        """Delete template."""
        template = template_manager.get(document_id=template_id)

        template_name = template["name"]
        resp = requests.delete(f"{STATIC_GEN_URL}/template/?category={template_name}")

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return jsonify({"error": str(e)})

        return jsonify(template_manager.delete(document_id=template_id))


class TemplateKeysView(MethodView):
    """TemplateKeysView."""

    def get(self):
        """Get list of keys for template context."""
        return jsonify(
            [
                "description",
                "domain",
                "email",
                "name",
                "phone",
            ]
        )
