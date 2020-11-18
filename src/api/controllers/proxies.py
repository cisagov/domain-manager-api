"""Proxy controller."""
from models.proxy import Proxy
from api.schemas.proxy_schema import ProxySchema


def proxy_manager(request, proxy_id=None):
    """Manage proxies."""
    if not proxy_id:
        if request.method == "POST":
            post_data = request.json
            proxy = Proxy.create(
                name=post_data.get("name"),
                url=post_data.get("url"),
                script=post_data.get("script"),
                categories=post_data.get("categories"),
            )
            response = {
                "message": f"Proxy with id {proxy.inserted_id} has been created."
            }
        else:
            proxies_schema = ProxySchema(many=True)
            response = proxies_schema.dump(Proxy.get_all())
        return response

    if request.method == "DELETE":
        Proxy.delete(proxy_id)
        response = {"message": "Proxy has been deleted."}
    elif request.method == "PUT":
        put_data = request.json
        updates = dict()
        if "name" in put_data:
            updates["name"] = put_data.get("name")
        if "url" in put_data:
            updates["url"] = put_data.get("url")
        if "script" in put_data:
            updates["script"] = put_data.get("script")
        Proxy.update(proxy_id=proxy_id, **updates)
        response = {"message": "Application has been updated."}
    else:
        proxy_schema = ProxySchema()
        response = proxy_schema.dump(Proxy.get_by_id(proxy_id))
    return response
