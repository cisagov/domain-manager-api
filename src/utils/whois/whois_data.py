"""Whois data."""
# Standard Python Libraries
import logging

# Third-Party Libraries
from whois import whois

# cisagov Libraries
from api.manager import WhoisManager

whois_manager = WhoisManager()


def add_whois_data_to_domains(domains: list) -> list:
    """Get many domains' whois data."""
    whois_domain = whois_manager.all(
        fields=["domain_id", "registrar", "expiration_date"]
    )

    domains_without_whois_data = [
        d for d in domains if d["_id"] not in [w["domain_id"] for w in whois_domain]
    ]

    try:
        if domains_without_whois_data:
            whois_data = [
                {
                    "domain_id": d["_id"],
                    "registrar": who["registrar"],
                    "expiration_date": who["expiration_date"][0].isoformat()
                    if isinstance(who["expiration_date"], list)
                    else who["expiration_date"].isoformat(),
                    "raw_data": who,
                }
                for d in domains_without_whois_data
                if (who := whois(d["name"])) and who["expiration_date"]
            ]
            whois_manager.save_many(whois_data) if whois_data else None
    except Exception as e:
        logging.error(e)

    return [
        {
            **d,
            "whois": next((w for w in whois_domain if w["domain_id"] == d["_id"]), {}),
        }
        for d in domains
    ]


def get_whois_data(domain_id: str, domain_name: str) -> dict:
    """Get a domain's whois data."""
    whois_domain = whois_manager.get(
        filter_data={"domain_id": domain_id}, fields=["registrar", "expiration_date"]
    )

    if not whois_domain:
        try:
            resp_data = whois(domain_name)
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
