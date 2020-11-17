"""Database types using typing standard library."""
from typing import Union, Dict, List, Any
from datetime import datetime


BytesType = Union[bytes, None]
BooleanType = bool
DatetimeType = Union[datetime, None]
DictType = Union[Dict[Any, Any], None]
IntegerType = Union[int, None]
ListType = Union[List[Any], None]
StringType = Union[str, None]
