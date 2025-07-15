from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import declarative_base, DeclarativeBase, Mapped
from sqlalchemy.testing.schema import mapped_column

class Base(DeclarativeBase):
    pass

class BookTrainModel(Base):
    __tablename__ = "books_train"

    id: Mapped[str] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String)
    year: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)
    stock: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    rating: Mapped[int] = mapped_column(Integer)
    image: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return "<BookTrainModel {} {} {} {} {} {} {} {}>".format(
            self.id, self.author, self.year, self.title, self.category, self.stock, self.price, self.rating, self.image)