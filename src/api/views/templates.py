"""Template Views."""
# Standard Python Libraries
import io

# Third-Party Libraries
from flask import jsonify, send_file
from flask.views import MethodView
import requests

# cisagov Libraries
from api.manager import TemplateManager
from settings import STATIC_GEN_URL

template_manager = TemplateManager()


class TemplatesView(MethodView):
    """TemplatesView."""

    def get(self):
        """Get all templates."""
        return jsonify(template_manager.all())

    def post(self):
        """Create new template."""
        return "Not yet implemented"


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
