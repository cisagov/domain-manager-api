"""
This is a models file.

Here we create create the Base Model class for creating db models to inserting into db.
This helps up control type and validation for json object.
"""
# Standard Python Libraries
import datetime

# Third-Party Libraries
from schematics.models import Model as BaseModel
import yaml

from .types import (
    BooleanType,
    DateTimeType,
    DictType,
    EmailType,
    FloatType,
    IntType,
    ListType,
    ModelType,
    StringType,
    UUIDType,
)


class Model(BaseModel):
    """Standard data validation model."""

    def document_model(self, render_to_yaml=False):
        """Document to Model."""
        model_name = str(self).split(" ")[0][1:]
        model_doc_json = {
            model_name: {"type": "object", "required": [], "properties": {}}
        }

        for name, field in self.fields.items():
            if field.required:
                model_doc_json[model_name]["required"].append(name)
            model_doc_json[model_name]["properties"][name] = Model.document_field(field)

        if render_to_yaml:
            return yaml.dump(model_doc_json, default_flow_style=False)

        return model_doc_json

    @staticmethod
    def document_field(field):
        """Generic method that can be used to validate a model."""
        if type(field) is UUIDType:
            return {"type": "string", "format": "UUID", "example": field._mock()}

        elif type(field) is StringType:
            field_doc = {"type": "string", "example": field.example}
            if field.max_length:
                field_doc["maximum"] = field.max_length
            if field.min_length is not None:
                field_doc["minumum"] = field.min_length
            return field_doc

        elif type(field) is IntType:
            field_doc = {"type": "integer", "format": "int32"}
            if field.min_value is not None:
                field_doc["minimium"] = field.min_value
            if field.max_value is not None:
                field_doc["maximum"] = field.max_value
            return field_doc

        elif type(field) is FloatType:
            field_doc = {"type": "number", "format": "float"}
            if field.min_value is not None:
                field_doc["minimium"] = field.min_value
            if field.max_value is not None:
                field_doc["maximum"] = field.max_value
            return field_doc

        elif type(field) is BooleanType:
            return {"type": "boolean"}

        elif type(field) is DateTimeType:
            return {
                "type": "string",
                "format": "date-time",
                "example": datetime.datetime.now().isoformat(),
            }

        elif type(field) is ModelType:
            field_doc = {}
            for name, sub_field in field.model_class().fields.items():
                field_doc[name] = Model.document_field(sub_field)
            return field_doc

        elif type(field) is ListType:
            field_doc = {"type": "array"}
            if field.min_size is not None:
                field_doc["minimum"] = field.min_size
            if field.max_size is not None:
                field_doc["maximum"] = field.max_size
            field_doc["items"] = Model.document_field(field.field)
            return field_doc

        elif type(field) is DictType:
            field_doc = {"type": "object", "additionalProperties": "true"}
            return field_doc

        elif type(field) is EmailType:
            return {"type": "string", "format": "email", "example": field._mock()}

        else:
            return {"ERROR": f"Unable to generate documentation for {field.name}"}

    def validate(self, *args, **kwargs):
        """Generic method that can be used to validate a model."""
        super(Model, self).validate(*args, **kwargs)
        return self.to_native()
