"""Custom validators for marshmallow schemas."""
# Standard Python Libraries
import re

# Third-Party Libraries
from marshmallow import ValidationError
import validators


def validate_data(data, schema_class, many=False):
    """Validate data against schema class."""
    schema = schema_class(many=many)
    return schema.load(data)


def is_valid_domain(domain):
    """Check if domain is valid."""
    pattern = re.compile(
        r"^(?!:\/\/)([a-zA-Z0-9-_]+\.)*[a-zA-Z0-9][a-zA-Z0-9-_]+\.[a-zA-Z]{2,24}?$"
    )
    if pattern.match(domain) or domain == "localhost":
        return True
    raise ValidationError("Must be a valid domain.")


def is_valid_ipv4(address):
    """Check if ipv4 address is valid."""
    if not validators.ipv4(address):
        raise ValidationError("Must be a valid ipv4 address.")
    return True


def is_valid_ipv6(address):
    """Check if ipv6 address is valid."""
    if not validators.ipv6(address):
        raise ValidationError("Must be a valid ipv6 address.")
    return True


def is_valid_category(category):
    """Check if category is valid."""
    if " " in category:
        raise ValidationError("Category must not contain spaces.")
    return True


def is_valid_email(email: str):
    """Check if email address format is valid."""
    if not validators.email(email):
        raise ValidationError("Email address format is not valid.")
    return True


def is_valid_mx(value: str):
    """Check if mx record is valid."""
    for line in value.splitlines():
        try:
            priority, hostname = line.split(" ")
        except ValueError:
            raise ValidationError(
                "Each line must be in the following format: [priority] [hostname]"
            )
        if not priority.isdigit():
            raise ValidationError("Priority must be a digit.")
        is_valid_domain(hostname)
    return True


def is_valid_srv(value: str):
    """Check if srv record is valid."""
    for line in value.splitlines():
        try:
            priority, weight, port, hostname = line.split(" ")

            if not priority.isdigit():
                raise ValidationError("Priority must be a digit.")
            if not weight.isdigit():
                raise ValidationError("Weight must be a digit.")
            if not port.isdigit():
                raise ValidationError("Port must be a digit.")
            is_valid_domain(hostname)
        except ValueError:
            raise ValidationError(
                "Each line must be in the following format: [priority] [weight] [port] [hostname]"
            )
    return True


def is_valid_ns(value: str):
    """Check if NS record is valid."""
    for line in value.splitlines():
        is_valid_domain(line)
    return True
