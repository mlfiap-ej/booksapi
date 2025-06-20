import os
from typing import List

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from data.model.bookmodel import BookModel
from model.book import Book

from decouple import config

stmt = select(BookModel).limit(5)
PAGE_SIZE = config("PAGE_SIZE", cast=int)

class CsvDataSource:
    def __init__(self, path):
        filepath = os.path.join(os.getcwd(), path)
        self.engine = create_engine('duckdb:///{}'.format(filepath))

    def _get_session(self):
        return Session(self.engine)

    def get_all_books(self, page: int = 1) -> List[Book]:
        s = self._get_session()
        stmt = select(BookModel).limit(PAGE_SIZE).offset((page - 1) * PAGE_SIZE)
        rows = s.scalars(stmt).fetchall()
        data_to_return = []
        for row in rows:
            data_to_return.append(
                Book(row.id, row.author, row.year, row.title, row.category, row.stock, row.price)
            )
        return data_to_return

    def get_book(self, book_id: str) -> Book|None:
        s = self._get_session()
        stmt = select(BookModel).where(BookModel.id == book_id)
        row = s.execute(stmt).scalars().first()
        if not row:
            return None
        return Book(row.id, row.author, row.year, row.title, row.category, row.stock, row.price)

    def search(self, page: int = 1, **kwargs) -> List[Book]:

        # TODO validar se a chave esta correta

        s = self._get_session()
        stmt = select(BookModel).limit(PAGE_SIZE).offset((page - 1) * PAGE_SIZE)
        if 'category' in kwargs.keys() and kwargs['category'].strip() != "":
            stmt = stmt.where(BookModel.category == kwargs['category'])
        if 'title' in kwargs.keys() and kwargs['title'].strip() != '':
            stmt = stmt.where(BookModel.title == kwargs['title'])

        rows = s.scalars(stmt).fetchall()
        data_to_return = []
        for row in rows:
            data_to_return.append(
                Book(row.id, row.author, row.year, row.title, row.category, row.stock, row.price)
            )
        return data_to_return

    def get_all_categories(self):
        stmt = select(BookModel.category).distinct()
        print(stmt)
        s = self._get_session()
        rows = s.scalars(stmt).fetchall()
        return rows

    def health(self):
        s = self._get_session()
        stmt = select(1)
        row = s.execute(stmt).scalars().first()
        return True


def build(path: str, type: str) -> CsvDataSource:
    if type == 'csv':
        return CsvDataSource(path)