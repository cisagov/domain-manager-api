"""Database types using typing standard library."""
from typing import Union, Dict, List, Any
from datetime import datetime


Bytes = Union[bytes, None]
Datetime = Union[datetime, None]
Dicttype = Union[Dict[Any, Any], None]
Integertype = Union[int, None]
Listtype = Union[List[Any], None]
Stringtype = Union[str, None]
