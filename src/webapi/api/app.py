import locale
from typing import Annotated, List

from fastapi import FastAPI, HTTPException, Query
from starlette.requests import Request
from starlette.responses import JSONResponse

from data.csvdatads import CsvAnalysisDataSource
from data.csvds import CsvDataSource
from model.book import Book
from webapi.api import filters, models
from webapi.api.security import check_jwt

DESCRIPTION = """
API de acesso a dados de livros, baseada em arquivo csv, originado em scraping.

**Autores**:

- Erick Muller
- José Rubens Rodrigues
"""

csv_ds = CsvDataSource("mockdata/books.csv")
train_csv_ds = CsvDataSource("mockdata/books_train.csv")
test_csv_ds = CsvDataSource("mockdata/books_test.csv")
csv_analysis_ds = CsvAnalysisDataSource("mockdata/books.csv")

app = FastAPI(root_path="/api/v1", description=DESCRIPTION)


@app.middleware("http")
async def middleware(request: Request, call_next):
    """
    Middleware para autenticação JWT em endpoints protegidos.
    Permite acesso não autenticado aos endpoints de auth, docs e openapi.
    """
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
    """
    Retorna uma lista paginada de todos os livros.
    """
    r = csv_ds.get_all_books(page=filter_query.page)
    return models.ListReturn(data=r, length=len(r))


@app.get("/books/top-rated")
async def top_rated_books(
    filter_query: Annotated[filters.ItemQtyFilterParameters, Query()],
) -> List[Book]:
    """
    Retorna uma lista dos livros mais bem avaliados, limitada pela quantidade especificada.
    """
    books_ids = csv_analysis_ds.books_best_rated(filter_query.limit)
    if books_ids is None:
        return []



    if not filter_query or len(books_ids) > 10:
        books_ids = books_ids[:10]
    books = [csv_ds.get_book(id) for id in books_ids]
    return books


@app.get("/books/price-range")
async def books_by_price_range(
    filter_query: Annotated[filters.BookPriceRangeParameters, Query()],
) -> List[Book]:
    """
    Retorna uma lista de livros filtrados por faixa de preço e quantidade.
    """
    limit = filter_query.limit if filter_query.limit > 0 else 10

    books_ids = csv_analysis_ds.books_filtered_by_price(
        min=filter_query.min, max=filter_query.max, qty=limit
    )

    if books_ids is None:
        return []
    books = [csv_ds.get_book(id) for id in books_ids]
    return books


@app.get("/books/search", description="Busca um livro passando categoria ou titulo")
async def search_book(
    filter_query: Annotated[filters.BookFilterParameters, Query()],
) -> models.ListReturn:
    """
    Busca livros por título ou categoria com paginação.
    """
    if filter_query.title == "" and filter_query.category == "":
        raise HTTPException(status_code=400)
    r = csv_ds.search(
        title=filter_query.title, category=filter_query.category, page=filter_query.page
    )
    return models.ListReturn(data=r, length=len(r))


@app.get("/books/{book_id}", description="Busca um livro dado um id")
async def book(book_id: str) -> Book:
    """
    Retorna um livro pelo seu ID.
    Ou HTTP 404 se não encontrado.
    """
    r = csv_ds.get_book(book_id)
    if r is None:
        raise HTTPException(status_code=404)
    return r


@app.get("/categories/", description="Lista de categorias")
async def all_categories() -> dict:
    """
    Retorna uma lista de todas as categorias de livros.
    """
    cx = csv_ds.get_all_categories()
    return {"data": cx}


@app.get("/health/", description="Teste de endpoint")
async def health() -> models.HealthReturn:
    """
    Endpoint de verificação de saúde da API e da fonte de dados.
    """
    return models.HealthReturn(
        status="ok", data_source="ok" if csv_ds.health() else "error"
    )


@app.get("/stats/overview")
async def overview() -> dict:
    """
    Retorna um panorama de estatísticas: total de livros, preço médio e distribuição de avaliações.
    """
    # locale.setlocale(locale.LC_MONETARY, "en_GB")
    # preco_medio_formatado = locale.currency(
    #     csv_analysis_ds.prices_average(), grouping=True
    # )
    return {
        "total_livros": csv_analysis_ds.books_count(),
        "preco_medio": f"{csv_analysis_ds.prices_average():.5f}",
        "distribuicao_ratings": csv_analysis_ds.rating_distribution(),
    }


@app.get("/stats/categories")
async def categories_overview() -> dict:
    """
    Retorna estatísticas por categoria: quantidade de livros e dados de preços.
    """
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
    """
    Retorna os features do conjunto de teste para machine learning.
    """
    r = test_csv_ds.get_all_test_books()
    return models.ListReturn(data=r, length=len(r))

@app.get("/ml/training-data")
async def ml_training_data() -> models.ListReturn:
    """
    Retorna os dados do conjunto de treino para machine learning.
    """
    r = train_csv_ds.get_all_train_books()
    return models.ListReturn(data=r, length=len(r))

@app.post("/auth")
async def auth(userlogin: models.Userlogin):
    """
    Autentica um usuário e retorna um token JWT se as credenciais forem válidas.
    """
    from webapi.api.security import emit_jwt

    try:
        j = emit_jwt(userlogin.username, userlogin.password)
        return j
    except Exception:
        raise HTTPException(status_code=401)


def get_app():
    """
    Retorna a instância da aplicação FastAPI.
    """
    return app
