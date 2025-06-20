from dataclasses import dataclass
from decimal import Decimal, getcontext, setcontext

@dataclass
class Book:
    id: str
    author: str
    year: int
    title: str
    category: str
    stock: int
    price: Decimal
    
    def __init__(self, id: str, author: str, year: int, title: str, category: str, stock: int, price: Decimal | float):
        self.id = id
        self.author = author
        self.year = year
        self.title = title
        self.category = category
        self.stock = stock
        if isinstance(price, float):
            self.price = Decimal(str(price))
        else:
            self.price = price