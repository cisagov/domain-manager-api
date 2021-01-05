"""Template Views."""
# Standard Python Libraries
import io
import shutil

# Third-Party Libraries
from flask import jsonify, request, send_file
from flask.views import MethodView
import requests

# cisagov Libraries
from api.manager import TemplateManager
from settings import STATIC_GEN_URL, TEMPLATE_BUCKET

template_manager = TemplateManager()


class TemplatesView(MethodView):
    """TemplatesView."""

    def get(self):
        """Get all templates."""
        return jsonify(template_manager.all())

    def post(self):
        """Create new template."""
        category = request.args.get("category")

        resp = requests.post(
            f"{STATIC_GEN_URL}/template/?category={category}",
            files={"zip": (f"{category}.zip", request.files["zip"])},
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return jsonify({"error": str(e)})

        # remove temp files
        shutil.rmtree("tmp/", ignore_errors=True)

        return jsonify(
            template_manager.save(
                {
                    "name": category,
                    "s3_url": f"https://{TEMPLATE_BUCKET}.s3.amazonaws.com/{category}/template/",
                }
            )
        )


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
        resp = requests.delete(
            f"{STATIC_GEN_URL}/template/?category={template['name']}"
        )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return jsonify({"error": str(e)})

        return jsonify(template_manager.delete(document_id=template_id))
