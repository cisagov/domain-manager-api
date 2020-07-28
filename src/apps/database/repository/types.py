"""
This is the type file.

Here we define types to be imported into models and used for validation.
This is using schematics.type as a base
"""
# Standard Python Libraries
import uuid

# Third-Party Libraries
# These imports are so models.py can import all its types from this file.
from schematics.types import BooleanType as BaseBooleanType
from schematics.types import DateTimeType as BaseDateTimeType
from schematics.types import DictType as BaseDictType
from schematics.types import FloatType as BaseFloatType
from schematics.types import IntType as BaseIntType
from schematics.types import ListType as BaseListType
from schematics.types import ModelType as BaseModelType
from schematics.types import StringType as BaseStringType


class UUIDType(BaseStringType):
    """
    UUIDType.

    Base class for UUIDType.
    """

    def __init__(self, *args, **kwargs):
        """
        Init.

        Adding regex, required, _mock and max_length checking.
        """
        self.regex = r"^[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}$"
        self.required = kwargs.get("required", True)
        self._mock = lambda self_instance, context=None: str(uuid.uuid4())
        self.max_length = self.min_length = 36
        super().__init__(
            required=self.required,
            min_length=self.min_length,
            max_length=self.max_length,
            regex=self.regex,
        )


class StringType(BaseStringType):
    """
    StringType.

    Base class for StringType.
    """

    def __init__(self, **kwargs):
        """
        Init.

        Adding required checking.
        """
        try:
            self.example = kwargs.pop("example")
        except KeyError:
            # raise TypeError("Example is a required parameter.")
            pass
        super().__init__(**kwargs)


class IntType(BaseIntType):
    """
    IntType.

    Base class for IntType.
    """

    def __init__(self, *arg, **kwargs):
        """
        Init.

        Adding required checking.
        """
        try:
            self.example = kwargs.pop("example")
        except KeyError:
            # raise TypeError("Example is a required parameter.")
            pass
        super().__init__(**kwargs)


class FloatType(BaseFloatType):
    """
    FloatType.

    Base class for FloatType.
    """

    def __init__(self, *arg, **kwargs):
        """
        Init.

        Adding required checking.
        """
        try:
            self.example = kwargs.pop("example")
        except KeyError:
            # raise TypeError("Example is a required parameter.")
            pass
        super().__init__(**kwargs)


class EmailType(BaseStringType):
    """
    EmailType.

    Base class for EmailType.
    Adding regex for email validation.
    """

    def __init__(self, *arg, **kwargs):
        """
        Init.

        Adding required and regex checking.
        """
        self._mock = lambda self_instance, context=None: "Mr.Example@example.com"
        if "regex" in kwargs:
            self.regex = kwargs.pop("regex")
        else:
            self.regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        super().__init__(regex=self.regex)


class DateTimeType(BaseDateTimeType):
    """
    DateTimeType.

    Base class for DateTimeType.
    """


class BooleanType(BaseBooleanType):
    """
    BooleanType.

    Base class for BooleanType.
    """

    def __init__(self, *arg, **kwargs):
        """
        Init.

        Adding required checking.
        """
        try:
            self.example = kwargs.pop("example")
        except KeyError:
            # raise TypeError("Example is a required parameter.")
            pass
        super().__init__(**kwargs)


class ModelType(BaseModelType):
    """
    ModelType.

    Base class for ModelType.
    """


class DictType(BaseDictType):
    """
    DictType.

    Base class for DictType.
    """


class ListType(BaseListType):
    """
    ListType.

    Base class for ListType.
    """
