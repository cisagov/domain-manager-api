"""Database types using typing standard library."""
from typing import Union, Dict, List, Any
from datetime import datetime


Bytes = Union[bytes, None]
Datetime = Union[datetime, None]
DictType = Union[Dict[Any, Any], None]
IntegerType = Union[int, None]
ListType = Union[List[Any], None]
StringType = Union[str, None]
