"""Proxy views."""
# Third-Party Libraries
from flask import jsonify
from flask.views import MethodView

# cisagov Libraries
from utils.proxies import PROXIES


class ProxiesView(MethodView):
    """ProxiesView."""

    def get(self):
        """Get all proxies."""
        return jsonify(PROXIES)


class ProxyView(MethodView):
    """ProxyView."""

    def get(self, proxy_name):
        """Get proxy details by name."""
        return jsonify(
            [proxy for proxy in PROXIES if proxy["name"] == proxy_name.title()][0]
        )
