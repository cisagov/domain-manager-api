"""Decorator utils."""
# Standard Python Libraries
from functools import wraps
import os

# Third-Party Libraries
from flask import abort, request


def auth_required(view):
    """Authorization required decorator."""

    @wraps(view)
    def decorated(*args, **kwargs):
        """Returns a decorated function."""
        if os.environ.get("API_KEY") == request.headers.get("api_key"):
            return view(*args, **kwargs)
        else:
            abort(401)

    return decorated
