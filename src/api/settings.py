"""Interact with settings in the database."""
# cisagov Libraries
from api.manager import SettingsManager
from api.schemas.settings_schema import SettingsPostSchema
from utils.validator import validate_data


class Settings:
    """Settings."""

    SES_FORWARD_EMAIL = None

    def __init__(self) -> None:
        """Init."""
        self.settings_manager = SettingsManager()
        pass

    def load(self):
        """Load settings from database."""
        settings = self.settings_manager.all()
        for setting in settings:
            setattr(self, setting["key"], setting["value"])

    def update(self, data):
        """Update with new settings."""
        self.load()
        data = validate_data(data, SettingsPostSchema)
        for k, v in self.to_dict().items():
            if k in data:
                v = data[k]
                setattr(self, k, v)
            self.settings_manager.upsert(
                query={"key": k},
                data={"key": k, "value": v},
            )
        return self.to_dict()

    def to_dict(self):
        """Represent class as dict for responses."""
        return {"SES_FORWARD_EMAIL": self.SES_FORWARD_EMAIL}
