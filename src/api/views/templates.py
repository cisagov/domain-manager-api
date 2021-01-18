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
from settings import STATIC_GEN_URL, TEMPLATE_BUCKET

template_manager = TemplateManager()


class TemplatesView(MethodView):
    """TemplatesView."""

    def get(self):
        """Get all templates."""
        return jsonify(template_manager.all())

    def post(self):
        """Create new template."""
        overwrite = request.args.get("overwrite")
        bOverwrite = overwrite.lower().strip() == "true"

        def checkName(name):
            templates = template_manager.all()
            existing_names = [
                (template["name"], template["_id"])
                for template in templates
                if name == template["name"]
            ]
            return len(existing_names) > 0, existing_names

        def cleanup(name, document_id):
            resp = requests.delete(f"{STATIC_GEN_URL}/template/?category={name}")
            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as e:
                return {"name": name, "status": str(e)}
            template_manager.delete(document_id)
            return {"name": name, "status": "deleted"}

        rvalues = []
        for file in request.files.getlist("zip"):
            if file.filename.endswith(".zip"):
                name = file.filename[:-4]
            (exists, ids) = checkName(name)

            if bOverwrite and exists:
                cleanup(name, ids[0][1])
                exists = False

            if not exists:
                urlEscapedName = urllib.parse.quote_plus(name)
                resp = requests.post(
                    f"{STATIC_GEN_URL}/template/?category={urlEscapedName}",
                    files={"zip": (f"{file.filename}", file)},
                )
                try:
                    resp.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    return jsonify({"error": str(e)})

                # remove temp files
                shutil.rmtree("tmp/", ignore_errors=True)

                s3_url = f"{TEMPLATE_BUCKET}.s3.amazonaws.com/{name}/"
                result = template_manager.save(
                    {
                        "name": name,
                        "s3_url": s3_url,
                    }
                )
                rvalues.append({"_id": result["_id"], "name": name, "s3_url": s3_url})
            else:
                rvalues.append(
                    {"_id": "0", "name": name, "error": "template already exits"}
                )

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
        resp = requests.delete(
            f"{STATIC_GEN_URL}/template/?category={template['name']}"
        )

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
