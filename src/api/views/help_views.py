"""Category Views."""
# Third-Party Libraries
from flask import request
from flask.views import MethodView
from flask import send_file


class UserGuideView(MethodView):
    """User Guide View."""

    def get(self):
        """Download the User Guide."""
        path = "userGuide/DomainManager.pdf"
        return send_file(path, as_attachment=True)
