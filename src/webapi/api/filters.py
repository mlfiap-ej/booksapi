import sys
from pydantic import BaseModel

class BookFilterParameters(BaseModel):
    title: str = ""
    category: str = ""
    page: int = 1

class PageFilterParameters(BaseModel):
    page: int = 1

class ItemQtyFilterParameters(BaseModel):
    limit: int = 10

class BookPriceRangeParameters(BaseModel):
    max: int = sys.float_info.max
    min: int = 0
    limit: int = 0