import locale
from typing import Annotated, List

from fastapi import FastAPI, Query, HTTPException
import pandas as pd
from sklearn.model_selection import train_test_split

import api.filters as filters
import api.models as models
from data.csvdatads import CsvAnalysisDataSource
from data.csvds import CsvDataSource
from model.book import Book

from api.security import check_jwt
from starlette.responses import JSONResponse
from starlette.requests import Request


description = """
API de acesso a dados de livros, baseada em arquivo csv, originado em scraping.

**Autores**:

- Erick Muller
- José Rubens Rodrigues
"""

csv_ds = CsvDataSource("mockdata/books.csv")
train_csv_ds = CsvDataSource("mockdata/books_train.csv")
test_csv_ds = CsvDataSource("mockdata/books_test.csv")
csv_analysis_ds = CsvAnalysisDataSource("mockdata/books.csv")

app = FastAPI(root_path="/api/v1", description=description)


@app.middleware("http")
async def middleware(request: Request, call_next):
    print(request.url.path)

    if (
        request.url.path.startswith("/api/v1/auth")
        or request.url.path.startswith("/docs")
        or request.url.path.startswith("/api/v1/openapi.json")
    ):
        response = await call_next(request)
        return response

    if request.headers.get("Authorization") is None:
        return JSONResponse({"message": "No authorization header"}, status_code=401)

    if not request.headers.get("Authorization").startswith("Bearer "):
        return JSONResponse(
            {"message": "Invalid authorization header (1)"}, status_code=401
        )

    auth_token = request.headers.get("Authorization").replace("Bearer ", "")
    if not check_jwt(auth_token):
        return JSONResponse(
            {"message": "Invalid authorization header (2)"}, status_code=401
        )

    response = await call_next(request)
    return response


@app.get("/books", description="Busca todos os livros")
async def all_books(
    filter_query: Annotated[filters.PageFilterParameters, Query()],
) -> models.ListReturn:
    r = csv_ds.get_all_books(page=filter_query.page)
    return models.ListReturn(data=r, length=len(r))


@app.get("/books/top-rated")
async def top_rated_books(
    filter_query: Annotated[filters.ItemQtyFilterParameters, Query()],
) -> List[Book]:
    books_ids = csv_analysis_ds.books_best_rated(filter_query.limit)
    if books_ids is None:
        return []
    books = [csv_ds.get_book(id) for id in books_ids]
    return books


@app.get("/books/price-range")
async def books_by_price_range(
    filter_query: Annotated[filters.BookPriceRangeParameters, Query()],
) -> List[Book]:
    books_ids = csv_analysis_ds.books_filtered_by_price(
        min=filter_query.min, max=filter_query.max, qty=filter_query.limit
    )

    if books_ids is None:
        return []
    books = [csv_ds.get_book(id) for id in books_ids]
    return books


@app.get("/books/search", description="Busca um livro passando categoria ou titulo")
async def search_book(
    filter_query: Annotated[filters.BookFilterParameters, Query()],
) -> models.ListReturn:
    if filter_query.title == "" and filter_query.category == "":
        raise HTTPException(status_code=400)
    r = csv_ds.search(
        title=filter_query.title, category=filter_query.category, page=filter_query.page
    )
    return models.ListReturn(data=r, length=len(r))


@app.get("/books/{book_id}", description="Busca um livro dado um id")
async def book(book_id: str) -> Book:
    r = csv_ds.get_book(book_id)
    if r is None:
        raise HTTPException(status_code=404)
    return r


@app.get("/categories/", description="Lista de categorias")
async def all_categories() -> dict:
    cx = csv_ds.get_all_categories()
    return {"data": cx}


@app.get("/health/", description="Teste de endpoint")
async def health() -> models.HealthReturn:
    return models.HealthReturn(
        status="ok", data_source="ok" if csv_ds.health() else "error"
    )


@app.get("/stats/overview")
async def overview() -> dict:
    locale.setlocale(locale.LC_MONETARY, "en_GB")
    preco_medio_formatado = locale.currency(
        csv_analysis_ds.prices_average(), grouping=True
    )
    return {
        "total_livros": csv_analysis_ds.books_count(),
        "preco_medio": preco_medio_formatado,
        "distribuicao_ratings": csv_analysis_ds.rating_distribution(),
    }


@app.get("/stats/categories")
async def categories_overview() -> dict:
    r = {}
    book_count = csv_analysis_ds.categories_books_count()
    prices_data = csv_analysis_ds.categories_prices_data()
    for category in book_count.keys():
        r[category] = {
            "quantidade_livros": book_count[category],
            "precos": prices_data[category],
        }
    return r

@app.get("/ml/features")
async def ml_features() -> models.ListReturn:
    r = test_csv_ds.get_all_test_books()
    return models.ListReturn(data=r, length=len(r))

@app.get("/ml/training-data")
async def ml_training_data() -> models.ListReturn:
    r = train_csv_ds.get_all_train_books()
    return models.ListReturn(data=r, length=len(r))

@app.post("/auth")
async def auth(userlogin: models.Userlogin):
    from api.security import check_password, emit_jwt

    try:
        j = emit_jwt(userlogin.username, userlogin.password)
        return j
    except Exception as e:
        raise HTTPException(status_code=401)


def get_app():
    return app
