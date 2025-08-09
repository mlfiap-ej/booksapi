from dataclasses import dataclass
from typing import List

from pydantic import BaseModel

from model.book import Book


@dataclass
class ListReturn:
    data: List[Book]
    length: int

@dataclass
class HealthReturn:
    status: str
    data_source: str


class Userlogin(BaseModel):
    username: str = ""
    password: str = ""

@dataclass
class PredictionReturn:
    status: str
    category: str
    price: float
    rating: int
