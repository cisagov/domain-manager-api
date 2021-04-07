"""Category Views."""
# Third-Party Libraries
from flask import send_file
from flask.views import MethodView


class UserGuideView(MethodView):
    """User Guide View."""

    def get(self):
        """Download the User Guide."""
        path = "userGuide/DomainManager.pdf"
        return send_file(path, as_attachment=True)
