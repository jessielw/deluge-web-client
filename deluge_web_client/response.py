from dataclasses import dataclass
from typing import Union


@dataclass
class Response:
    """Object that is filled on each request"""

    __slots__ = ("result", "error", "id")
    result: Union[bool, str, list, None]
    error: Union[None, str]
    id: int | None
