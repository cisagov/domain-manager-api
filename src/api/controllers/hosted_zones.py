"""Route53 DNS record manager."""
from utils.aws.dns_record_handler import generate_hosted_zone, delete_hosted_zone


def hosted_zones_manager(request):
    """Manage Route53 hosted zones for DNS records."""
    post_data = request.json
    domains = post_data.get("domains")
    response = {}
    if request.method == "POST":
        for domain in domains:
            response[domain] = generate_hosted_zone(domain)
    else:
        for domain in domains:
            response[domain] = delete_hosted_zone(domain)
    return response
