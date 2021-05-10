"""Apex records."""
# Standard Python Libraries
from functools import partial


def contains_apex_record(domain: dict):
    """Check if contains an apex record."""
    f = partial(is_apex_record, domain["name"])
    return bool(next(filter(f, domain.get("records", [])), False))


def is_apex_record(domain_name: str, record: dict):
    """Check if it is an apex record."""
    return record["name"] == domain_name and record["record_type"] == "A"
