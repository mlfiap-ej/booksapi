from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Book:
    id: str
    title: str
    category: str
    stock: int
    price: Decimal
    rating: int
    image: str

    def __init__(self, id_: str, title: str, category: str, stock: int, price: Decimal | float, rating: int, image: str = ""):
        self.id = id_
        self.title = title
        self.category = category
        self.stock = stock
        if isinstance(price, float):
            self.price = Decimal(str(price))
        else:
            self.price = price
        self.rating = rating
        self.image = image
