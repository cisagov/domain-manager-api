"""Templates controller."""
# Third Party Libraries
# Third-Party Libraries
import requests

# cisagov Libraries
from api.schemas.template_schema import TemplateSchema
from models.template import Template
from settings import STATIC_GEN_URL


def template_manager(template_id=None):
    """Manage templates."""
    if not template_id:
        template_schema = TemplateSchema(many=True)
        templates = template_schema.dump(Template().all())
        return templates

    template = Template(_id=template_id)
    template.get()
    category = template.name

    # Post request to go templates static gen
    resp = requests.get(f"{STATIC_GEN_URL}/template/?category={category}")

    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return {"error": str(e)}
    return resp.content, category
