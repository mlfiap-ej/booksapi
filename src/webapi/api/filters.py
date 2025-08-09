import sys

from pydantic import BaseModel

"""Módulo de filtros para a API de livros."""

class BookFilterParameters(BaseModel):
    """Filtra livros por título, categoria e página."""
    title: str = ""
    category: str = ""
    page: int = 1

class PageFilterParameters(BaseModel):
    """Parâmetros de paginação para listas de livros."""
    page: int = 1

class ItemQtyFilterParameters(BaseModel):
    """Limita a quantidade de itens retornados."""
    limit: int = 10

class BookPriceRangeParameters(BaseModel):
    """Filtra livros por faixa de preço e quantidade."""
    max: int = sys.float_info.max
    min: int = 0
    limit: int = 0


class PredictRatingParameters(BaseModel):
    category: str = ""
    price: float = 0
