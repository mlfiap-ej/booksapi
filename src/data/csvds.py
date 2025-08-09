import os
import csv

from typing import List

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from data.model.bookmodel import BookModel	
from data.model.booktestmodel import BookTestModel
from data.model.booktrainmodel import BookTrainModel
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
                Book(row.id, row.title, row.category, row.stock, row.price, row.rating, row.image)
            )
        return data_to_return

    def get_book(self, book_id: str) -> Book|None:
        s = self._get_session()
        stmt = select(BookModel).where(BookModel.id == book_id)
        row = s.execute(stmt).scalars().first()
        if not row:
            return None
        return Book(row.id,  row.title, row.category, row.stock, row.price, row.rating, row.image)

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
                Book(row.id, row.title, row.category, row.stock, row.price, row.rating, row.image)
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

    def get_all_test_books(self) -> List[Book]:
        s = self._get_session()
        stmt = select(BookTestModel)
        rows = s.scalars(stmt).fetchall()
        data_to_return = []
        for row in rows:
            data_to_return.append(
                Book(row.id, row.title, row.category, row.stock, row.price, row.rating, row.image)
            )
        return data_to_return

    def get_all_train_books(self) -> List[Book]:
        s = self._get_session()
        stmt = select(BookTrainModel)
        rows = s.scalars(stmt).fetchall()
        data_to_return = []
        for row in rows:
            data_to_return.append(
                Book(row.id, row.title, row.category, row.stock, row.price, row.rating, row.image)
            )
        return data_to_return

    def set_rating_for_category_price(self, category: str, price: float, rating: int) -> int:
        try:
            print("Saving ml request")
            with open("mockdata/ml_request.csv", "a") as file:
              print("Saving ml request 1")
              writer = csv.writer(file,quoting=csv.QUOTE_NONNUMERIC)
              writer.writerow([1, category, price, rating])
              print("Saving ml request 2")
        except Exception as e:
            print(f"Error saving ml request: {e}")
            return 0

        return 1
