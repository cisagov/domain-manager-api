"""Database types using typing standard library."""
from typing import Union, Dict, List, Any
from datetime import datetime


string_type = Union[str, None]
integer_type = Union[int, None]
datetime_type = Union[datetime, None]
dict_type = Union[Dict[Any, Any], None]
list_type = Union[List[Any], None]
