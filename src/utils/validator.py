"""Custom validators for marshmallow schemas."""
# Third-Party Libraries
from marshmallow import ValidationError
import validators


def is_valid_domain(domain):
    """Check if domain is valid."""
    if validators.domain(domain):
        return True
    raise ValidationError("Must be a valid domain.")


def is_valid_category(category):
    """Check if category is valid."""
    if " " in category:
        raise ValidationError("Category must not contain spaces.")
    return True
