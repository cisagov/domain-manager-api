"""Proxy views."""
# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import ProxyManager

proxy_manager = ProxyManager()


class ProxiesView(MethodView):
    """ProxiesView."""

    def get(self):
        """Get all proxies."""
        return jsonify(proxy_manager.all())

    def post(self):
        """Save proxy."""
        return jsonify(proxy_manager.save(request.json))


class ProxyView(MethodView):
    """ProxyView."""

    def get(self, proxy_id):
        """Get proxy by id."""
        return jsonify(proxy_manager.get(document_id=proxy_id))

    def put(self, proxy_id):
        """Update proxy by id."""
        return jsonify(proxy_manager.update(document_id=proxy_id, data=request.json))

    def delete(self, proxy_id):
        """Delete proxy by id."""
        return jsonify(proxy_manager.delete(document_id=proxy_id))
