from typing import Optional, Annotated
from pydantic import BaseModel
from data.csvsrc import CsvDataSource
from decouple import config
from fastapi import FastAPI, Query
from fastapi.exceptions import HTTPException

csv_ds = CsvDataSource(config('DATABASE_PATH'))

class BookFilterParameters(BaseModel):
    title: str = ""
    category: str = ""
    page: int = 1

class PageFilterParameters(BaseModel):
    page: int = 1

app = FastAPI(root_path="/v1/books")
@app.get("/")
async def all_books(filter_query: Annotated[PageFilterParameters, Query()]):
    r = csv_ds.get_all_books(page=filter_query.page)
    return {"length": len(r) , "data" : r}

@app.get("/{book_id}")
async def book(book_id: str):
    r = csv_ds.get_book(book_id)
    if r is None:
        raise HTTPException(status_code=404)
    return {"data" : r}

@app.get("/search/")
async def search_book(filter_query: Annotated[BookFilterParameters,Query()]):
    if filter_query.title == "" and filter_query.category == "":
        raise HTTPException(status_code=400)
    r = csv_ds.search(title= filter_query.title,category= filter_query.category,page=filter_query.page)
    return {"length": len(r), "data" : r}

@app.get("/categories/")
async def all_categories():
    cx = csv_ds.get_all_categories()
    return {"data": cx}

@app.get("/health/")
async def health():
    return {"status": "ok", "data_source": "ok" if csv_ds.health() else "error"}