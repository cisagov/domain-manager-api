"""Settings views."""
# Third-Party Libraries
from flask import request
from flask.json import jsonify
from flask.views import MethodView
from marshmallow.exceptions import ValidationError

# cisagov Libraries
from api.config import logger
from api.settings import Settings

settings = Settings()


class SettingsView(MethodView):
    """SettingsView."""

    def get(self):
        """Get settings from database."""
        return jsonify(settings.to_dict())

    def put(self):
        """Modify the setting."""
        try:
            return jsonify(settings.update(request.json))
        except ValidationError as e:
            logger.exception(e)
            return str(e), 400
