"""About Views."""
# Third-Party Libraries
from flask import jsonify
from flask.views import MethodView

# cisagov Libraries
from settings import API_COMMIT_ID, DEPLOYED_DATE, UI_COMMIT_ID


class AboutView(MethodView):
    """About View."""

    def get(self):
        """Get versioning and launch data."""
        return (
            jsonify(
                {
                    "api_commit_id": API_COMMIT_ID,
                    "ui_commit_id": UI_COMMIT_ID,
                    "deployed_date": DEPLOYED_DATE,
                },
            ),
            200,
        )
