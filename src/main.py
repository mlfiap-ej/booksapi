import sys
from dataclasses import dataclass
from typing import Optional, Annotated, List
from pydantic import BaseModel
from data.csvsrc import CsvDataSource
from data.csvdatasrc import CsvAnalysisDataSource
from decouple import config
from fastapi import FastAPI, Query
from fastapi.exceptions import HTTPException

from model.book import Book

import locale
locale.setlocale(locale.LC_ALL, 'en_GB')


csv_ds = CsvDataSource(config('DATABASE_PATH'))
csv_analysis_ds = CsvAnalysisDataSource(config('DATABASE_PATH'))

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

@dataclass
class ListReturn:
    data: List[Book]
    length: int

@dataclass
class HealthReturn:
    status: str
    data_source: str

description = """
API de acesso a dados de livros, baseada em arquivo csv, originado em scraping.

**Autores**:
 
- Erick Muller
- José Rubens Rodrigues
"""

app = FastAPI(root_path="/api/v1", description=description)
@app.get("/books", description="Busca todos os livros")
async def all_books(filter_query: Annotated[PageFilterParameters, Query()]) -> ListReturn:
    r = csv_ds.get_all_books(page=filter_query.page)
    return ListReturn(data=r, length=len(r))


@app.get("/books/top-rated")
async def top_rated_books(filter_query: Annotated[ItemQtyFilterParameters, Query()]) -> List[Book]:
    books_ids = csv_analysis_ds.books_best_rated(filter_query.limit)
    if books_ids is None:
        return []
    books = [csv_ds.get_book(id) for id in books_ids]
    return books


@app.get("/books/price-range")
async def books_by_price_range(filter_query: Annotated[BookPriceRangeParameters, Query()]) -> List[Book]:
    books_ids = csv_analysis_ds.books_filtered_by_price(
        min=filter_query.min,
        max=filter_query.max,
        qty=filter_query.limit)

    if books_ids is None:
        return []
    books = [csv_ds.get_book(id) for id in books_ids]
    return books

@app.get("/books/search", description="Busca um livro passando categoria ou titulo")
async def search_book(filter_query: Annotated[BookFilterParameters,Query()]) -> ListReturn:
    if filter_query.title == "" and filter_query.category == "":
        raise HTTPException(status_code=400)
    r = csv_ds.search(title= filter_query.title,category= filter_query.category,page=filter_query.page)
    return ListReturn(data=r, length=len(r))

@app.get("/books/{book_id}", description="Busca um livro dado um id")
async def book(book_id: str) -> Book:
    r = csv_ds.get_book(book_id)
    if r is None:
        raise HTTPException(status_code=404)
    return r

@app.get("/categories/", description="Lista de categorias")
async def all_categories() -> List:
    cx = csv_ds.get_all_categories()
    return {"data": cx}

@app.get("/health/", description="Teste de endpoint")
async def health() -> HealthReturn:
    return HealthReturn(status="ok", data_source="ok" if csv_ds.health() else "error")

@app.get("/stats/overview")
async def overview() -> dict:
    preco_medio_formatado = locale.currency( csv_analysis_ds.prices_average(), grouping=True, )
    return {
        "total_livros": csv_analysis_ds.books_count(),
        "preco_medio": preco_medio_formatado,
        "distribuicao_ratings": csv_analysis_ds.rating_distribution()
    }

@app.get("/stats/categories")
async def categories_overview() -> dict:
    r = {}
    book_count = csv_analysis_ds.categories_books_count()
    prices_data = csv_analysis_ds.categories_prices_data()
    for category in book_count.keys():
        r[category] = {
            'quantidade_livros': book_count[category],
            'precos': prices_data[category]
        }
    return r



