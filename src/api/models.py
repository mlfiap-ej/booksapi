from dataclasses import dataclass
from typing import List

from model.book import Book


@dataclass
class ListReturn:
    data: List[Book]
    length: int

@dataclass
class HealthReturn:
    status: str
    data_source: str