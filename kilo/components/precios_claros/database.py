# Give me a python module for inserting new info in this database.
# Write an example for inserting new prices.

from typing import List, Optional, Generator
from contextlib import contextmanager

import sqlalchemy as sa
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    relationship,
    Mapped,
    sessionmaker,
    Session
)


class Base(DeclarativeBase):
      pass


class Timestamp(Base):
    __tablename__ = "timestamp"
    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(nullable=False)
    month: Mapped[int] = mapped_column(nullable=False)
    day: Mapped[int] = mapped_column(nullable=False)
    hour: Mapped[int] = mapped_column(nullable=False)
    minute: Mapped[int] = mapped_column(nullable=False)
    second: Mapped[int] = mapped_column(nullable=False)
    prices: Mapped[List["Price"]] = relationship(back_populates="timestamp")

    def __repr__(self) -> str:
        return f"{self.year:4d}{self.month:>02d}{self.day:>02d}{self.hour:>02d}{self.minute:>02d}{self.second:>02d}"


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(64), index=True)


class State(Base):
    __tablename__ = "states"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(sa.String(32))
    name: Mapped[str] = mapped_column(sa.String(32))
    cities: Mapped[List["City"]] = relationship(back_populates="state")


class City(Base):
    __tablename__ = "cities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(32))
    state_id: Mapped[int] = mapped_column(sa.ForeignKey("states.id"))
    state: Mapped["State"] = relationship(back_populates="cities")
    places: Mapped[List["Place"]] = relationship(back_populates="city")


class Place(Base):
    __tablename__ = "places"
    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(sa.String(32))
    city_id: Mapped[int] = mapped_column(sa.ForeignKey("cities.id"))
    city: Mapped["City"] = relationship(back_populates="places")
    points_of_sale: Mapped[List["PointOfSale"]] = relationship(back_populates="place")


class PointOfSale(Base):
    __tablename__ = "points_of_sale"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(sa.String(16), index=True)
    flag: Mapped[str] = mapped_column(sa.String(32))
    business: Mapped[str] = mapped_column(sa.String(32))
    branch: Mapped[str] = mapped_column(sa.String(32))
    place_id: Mapped[int] = mapped_column(sa.ForeignKey("places.id"))
    place: Mapped["Place"] = relationship(back_populates="points_of_sale")
    prices: Mapped[List["Price"]] = relationship(back_populates="point_of_sale")


class ArticleCode(Base):
    __tablename__ = "article_codes"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(sa.String(32), unique=True)
    cards: Mapped[List["ArticleCard"]] = relationship(back_populates="article_code")
    prices: Mapped[List["Price"]] = relationship(back_populates="article_code")


class ArticleCard(Base):
    __tablename__ = "article_cards"
    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(sa.String(32))
    description: Mapped[str] = mapped_column(sa.String(256))
    package: Mapped[str] = mapped_column(sa.String(16))
    article_code_id: Mapped[int] = mapped_column(sa.ForeignKey("article_codes.id"))
    article_code: Mapped["ArticleCode"] = relationship(back_populates="cards")


class Price(Base):
    __tablename__ = "prices"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int] = mapped_column(nullable=False)
    timestamp_id: Mapped[int] = mapped_column(sa.ForeignKey("timestamp.id"))
    timestamp: Mapped["Timestamp"] = relationship(back_populates="prices")
    article_code_id: Mapped[int] = mapped_column(sa.ForeignKey("article_codes.id"))
    article_code: Mapped["ArticleCode"] = relationship(back_populates="prices")
    point_of_sale_id: Mapped[int] = mapped_column(sa.ForeignKey("points_of_sale.id"))
    point_of_sale: Mapped["PointOfSale"] = relationship(back_populates="prices")


class TaggedArticle(Base):
    __tablename__ = "tagged_articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    tag_id: Mapped[int] = mapped_column(sa.ForeignKey("tags.id"))
    article_code_id: Mapped[int] = mapped_column(sa.ForeignKey("article_codes.id"))


class TaggedPointOfSale(Base):
    __tablename__ = "tagged_points_of_sale"
    id: Mapped[int] = mapped_column(primary_key=True)
    tag_id: Mapped[int] = mapped_column(sa.ForeignKey("tags.id"))
    point_of_sale_id: Mapped[int] = mapped_column(sa.ForeignKey("points_of_sale.id"))


@contextmanager
def db_create_session(
    db_uri: Optional[str] = None
) -> Generator[Session, None, None]:
    if db_uri is None:
        db_uri = ":memory:"
    db_home = "sqlite+pysqlite:///" + db_uri
    db = sa.create_engine(db_home, future=True)
    Base.metadata.create_all(db)
    SessionLocal = sessionmaker(bind=db)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as panic:
        print(str(panic))
        session.rollback()
    finally:
        session.close()

@contextmanager
def db_open_session(
    db_uri: Optional[str] = None
) -> Generator[Session, None, None]:
    if db_uri is None:
        db_uri = ":memory:"
    db_home = "sqlite+pysqlite:///" + db_uri
    db = sa.create_engine(db_home, future=True)
    SessionLocal = sessionmaker(bind=db)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as panic:
        print(str(panic))
        session.rollback()
    finally:
        session.close()
