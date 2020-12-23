"""Website Views."""
# Standard Python Libraries
from datetime import datetime
import io

# Third-Party Libraries
from flask import jsonify, request, send_file
from flask.views import MethodView
import requests

# cisagov Libraries
from api.manager import ApplicationManager, WebsiteManager
from settings import STATIC_GEN_URL, TEMPLATE_BUCKET

website_manager = WebsiteManager()
application_manager = ApplicationManager()


class WebsitesView(MethodView):
    """WebsitesView."""

    def get(self):
        """Get all websites."""
        return jsonify(website_manager.all())


class WebsiteView(MethodView):
    """WebsiteView."""

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

    def put(self, website_id):
        """Update website."""
        website = website_manager.get(document_id=website_id)
        if request.json.get("application"):
            website["application"] = application_manager.get(
                filter_data={"name": request.json["application"]}
            )
            website["history"] = usage_history(website)

        return jsonify(website_manager.update(document_id=website_id, data=website))

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

        website_manager.update(
            document_id=website_id,
            data={
                "s3_url": f"https://{TEMPLATE_BUCKET}.s3.amazonaws.com/{category}/{domain}/",
                "category": category,
            },
        )

        return jsonify(
            {
                "message": f"{domain} static site has been created from the {category} template."
            }
        )


def usage_history(website):
    """Update website usage history on application change."""
    update = {"application": website["application"], "launch_date": datetime.utcnow()}
    response = website.get("history")
    if response:
        response.append(update)
    else:
        response = [update]
    return response
