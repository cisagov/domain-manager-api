"""Domain tags controller."""
# Third-Party Libraries
from api.documents.domain import Domain
from api.schemas.domain_schema import DomainSchema


def domains_manager(request, domain_id):
    """Manage domain tags."""
    if request.method == "PUT":
        put_data = request.json
        Domain.add_tag(domain_id=domain_id, tag_id=put_data.get("tag_id"))
        response = {"message": "Tag has been added to domain."}
    else:
        domain_schema = DomainSchema()
        response = domain_schema.dump(Domain.get_by_id(domain_id))

    return response
