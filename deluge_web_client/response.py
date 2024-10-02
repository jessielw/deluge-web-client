from dataclasses import dataclass
from typing import Union


@dataclass
class Response:
    __slots__ = ("result", "error", "id")
    result: Union[bool, str, list]
    error: Union[None, str]
    id: int
