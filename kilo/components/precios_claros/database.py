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


# Uncomment and configure these lines if needed
# db = sa.create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
# Session = sessionmaker(bind=db)
# Base = declarative_base()


class Base(DeclarativeBase):
      pass


class Timestamp(Base):
    __tablename__ = "timestamp"
    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(nullable=False)
    month: Mapped[int] = mapped_column(nullable=False)
    day: Mapped[int] = mapped_column(nullable=False)
    difference: Mapped[int] = mapped_column(nullable=False)
    points_of_sale: Mapped[List["PointOfCodeRepresentation"]] = relationship(back_populates="timestamp")
    prices: Mapped[List["Price"]] = relationship(back_populates="timestamp")


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(64), index=True)


class State(Base):
    __tablename__ = "states"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(sa.String(8))
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
    point_of_sale_id: Mapped[int] = mapped_column(sa.ForeignKey("points_of_sale.id"))
    point_of_sale_code: Mapped["PointOfSaleCode"] = relationship(back_populates="gates")


class PointOfSaleCode(Base):
    __tablename__ = "points_of_sale_codes"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(sa.String(16))
    gates: Mapped[List["Place"]] = relationship(back_populates="point_of_sale")
    representations: Mapped[List["PointOfSaleRepresentation"]] = relationship(back_populates="code")


class PointOfSaleRepresentation(Base):
    flag: Mapped[str] = mapped_column(sa.String(32))
    business: Mapped[str] = mapped_column(sa.String(32))
    branch: Mapped[str] = mapped_column(sa.String(32))
    code_id: Mapped[int] = mapped_column(sa.ForeignKey("point_of_sale_code.id"))
    code: Mapped["PointOfSaleCode"] = relationship(back_populates="representations")
    timestamp_id: Mapped[int] = mapped_column(sa.ForeignKey("timestamp.id"))
    timestamp: Mapped["Timestamp"] = relationship(back_populates="representations")


class ArticleCode(Base):
    __tablename__ = "article_codes"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(sa.String(32), unique=True)
    representations: Mapped[List["ArticleRepresentation"]] = relationship(back_populates="code")


class ArticleRepresentation(Base):
    __tablename__ = "article_representations"
    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(sa.String(32))
    description: Mapped[str] = mapped_column(sa.String(256))
    package: Mapped[str] = mapped_column(sa.String(16))
    code_id: Mapped[int] = mapped_column(sa.ForeignKey("article_codes.id"))
    code: Mapped["ArticleCode"] = relationship(back_populates="representations")


class Price(Base):
    __tablename__ = "prices"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int] = mapped_column(nullable=False)
    timestamp_id: Mapped[int] = mapped_column(sa.ForeignKey("timestamp.id"))
    article_id: Mapped[int] = mapped_column(sa.ForeignKey("articles.id"))
    point_of_sale_id: Mapped[int] = mapped_column(sa.ForeignKey("points_of_sale.id"))


class TaggedArticle(Base):
    __tablename__ = "tagged_articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    tag_id: Mapped[int] = mapped_column(sa.ForeignKey("tags.id"))
    article_id: Mapped[int] = mapped_column(sa.ForeignKey("articles.id"))


class TaggedPointOfSale(Base):
    __tablename__ = "tagged_point_of_sale"
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
