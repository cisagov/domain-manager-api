"""Custom Fields."""
# Standard Python Libraries
from datetime import datetime

# Third-Party Libraries
from marshmallow import fields


class DateTimeField(fields.DateTime):
    """DateTimeField."""

    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize data."""
        if isinstance(value, datetime):
            return value
        return super()._deserialize(value, attr, data, **kwargs)
