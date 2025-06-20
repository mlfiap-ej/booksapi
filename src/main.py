from dataclasses import dataclass
from typing import Optional, Annotated, List
from pydantic import BaseModel
from data.csvsrc import CsvDataSource
from decouple import config
from fastapi import FastAPI, Query
from fastapi.exceptions import HTTPException

from model.book import Book

csv_ds = CsvDataSource(config('DATABASE_PATH'))

class BookFilterParameters(BaseModel):
    title: str = ""
    category: str = ""
    page: int = 1

class PageFilterParameters(BaseModel):
    page: int = 1

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

app = FastAPI(root_path="/v1/books", description=description)
@app.get("/", description="Busca todos os livros")
async def all_books(filter_query: Annotated[PageFilterParameters, Query()]) -> ListReturn:
    r = csv_ds.get_all_books(page=filter_query.page)
    return ListReturn(data=r, length=len(r))

@app.get("/{book_id}", description="Busca um livro dado um id")
async def book(book_id: str) -> Book:
    r = csv_ds.get_book(book_id)
    if r is None:
        raise HTTPException(status_code=404)
    return r

@app.get("/search/", description="Busca um livro passando categoria ou titulo")
async def search_book(filter_query: Annotated[BookFilterParameters,Query()]) -> ListReturn:
    if filter_query.title == "" and filter_query.category == "":
        raise HTTPException(status_code=400)
    r = csv_ds.search(title= filter_query.title,category= filter_query.category,page=filter_query.page)
    return ListReturn(data=r, length=len(r))

@app.get("/categories/", description="Lista de categorias")
async def all_categories() -> List:
    cx = csv_ds.get_all_categories()
    return {"data": cx}

@app.get("/health/", description="Teste de endpoint")
async def health() -> HealthReturn:
    return HealthReturn(status="ok", data_source="ok" if csv_ds.health() else "error")