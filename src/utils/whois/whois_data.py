"""Whois data."""
# Standard Python Libraries
import logging

# Third-Party Libraries
from whois import whois

# cisagov Libraries
from api.manager import WhoisManager

whois_manager = WhoisManager()


def get_whois_data(domain_id: str, domain_name: str) -> dict:
    """Get a domain's whois data."""
    whois_domain = whois_manager.get(
        filter_data={"domain_id": domain_id}, fields=["registrar", "expiration_date"]
    )

    if not whois_domain:
        try:
            resp_data = whois.whois(domain_name)
        except Exception as e:
            logging.error(e)
            return {"error": "Whois data not found."}

        if not resp_data["expiration_date"]:
            return resp_data

        expiration_date = resp_data["expiration_date"]
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0].isoformat()
        else:
            expiration_date = expiration_date.isoformat()

        resp_data = {
            "domain_id": domain_id,
            "registrar": resp_data["registrar"],
            "expiration_date": expiration_date,
            "raw_data": resp_data,
        }

        whois_manager.save(resp_data)

        whois_domain = {key: resp_data[key] for key in resp_data if key != "raw_data"}

    return whois_domain
