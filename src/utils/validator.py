"""Custom validators for marshmallow schemas."""
# Third-Party Libraries
from marshmallow import ValidationError
import validators


def validate_data(data, schema_class, many=False):
    """Validate data against schema class."""
    schema = schema_class(many=many)
    validation_errors = schema.validate(schema.dump(data))
    if validation_errors:
        raise ValidationError(validation_errors)


def is_valid_domain(domain):
    """Check if domain is valid."""
    if validators.domain(domain) or domain == "localhost":
        return True
    raise ValidationError("Must be a valid domain.")


def is_valid_category(category):
    """Check if category is valid."""
    if " " in category:
        raise ValidationError("Category must not contain spaces.")
    return True
