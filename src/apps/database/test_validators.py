"""
This is an example validators file.

Here is an example to define the model using the lib, this would be called in
another service and passed over the service def.
"""
from .repository.models import Model
from .repository.types import DateTimeType, StringType, UUIDType


class DemoModel(Model):
    """
    This is an example Model.

    This shows basic types that we will use on each model.
    """

    demo_uuid = UUIDType()
    name = StringType()
    enum_type = StringType(required=True, choices=("initial", "post", "pre", "final"))
    record_tstamp = DateTimeType(required=True)
    method_of_record_creation = StringType()
    last_updated_by = StringType(required=False, max_length=255)
    lub_timestamp = DateTimeType(required=False)
    method_of_lu = StringType(required=False)


def validate_demo(demo):
    """
    This is an example validate_demo.

    This shows basic validation for the model.
    """
    return DemoModel(demo).validate()
