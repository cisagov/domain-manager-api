"""Apex records."""


def contains_apex_record(domain: dict):
    """Check if contains an apex record."""
    return bool(
        next(
            filter(
                lambda x: is_apex_record(x, domain["name"]), domain.get("records", [])
            ),
            False,
        )
    )


def is_apex_record(record: dict, domain_name: str):
    """Check if it is an apex record."""
    return record["name"] == domain_name and record["record_type"] == "A"
