"""Database types using typing standard library."""
# Standard Python Libraries
from datetime import datetime
from typing import Any, Dict, List, Union

BytesType = Union[bytes, None]
BooleanType = bool
DatetimeType = Union[datetime, None]
DictType = Union[Dict[Any, Any], None]
IntegerType = Union[int, None]
ListType = Union[List[Any], None]
StringType = Union[str, None]
