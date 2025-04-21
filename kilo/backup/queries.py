import logging
from typing import List, Optional, Generator
from contextlib import contextmanager
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    relationship,
    Mapped,
    WriteOnlyMapped,
    sessionmaker,
    Session,
)


class DatabaseException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logging.error(message)


def get_int(string: str) -> int:
    try:
        return int(string)
    except Exception as panic:
        logging.error(f"*** Error database.get_int")
        logging.error(f"    string: {str(panic)}")
        message = f"*** Error database.get_int ({type(panic).__name__}): {str(panic)}"
        raise DatabaseException(message)


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
    prices: WriteOnlyMapped["Price"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

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
    prices: WriteOnlyMapped["Price"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ArticleCode(Base):
    __tablename__ = "article_codes"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(sa.String(32), unique=True)
    cards: Mapped[List["ArticleCard"]] = relationship(back_populates="article_code")
    prices: WriteOnlyMapped["Price"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


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
def db_get_session(db_uri: Optional[str] = None) -> Generator[Session, None, None]:
    if db_uri is None:
        db_uri = ":memory:"
        create_db = True
    else:
        db_path = Path(db_uri)
        create_db = not db_path.exists()
    db_home = "sqlite+pysqlite:///" + db_uri
    db = sa.create_engine(db_home, future=True)
    if create_db:
        Base.metadata.create_all(db)
    SessionLocal = sessionmaker(bind=db)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as panic:
        logging.error(str(panic))
        session.rollback()
    finally:
        session.close()


def query_article_cards_ordered(session: Session) -> List[ArticleCard]:
    """Queries article_cards ordered by brand, description, and package."""
    return session.query(ArticleCard).order_by(
        ArticleCard.brand, ArticleCard.description, ArticleCard.package
    ).all()

#Example Usage.
if __name__ == "__main__":
    with db_get_session() as session:
        # Create some sample data
        article_code1 = ArticleCode(code="AC001")
        article_code2 = ArticleCode(code="AC002")

        article_card1 = ArticleCard(brand="BrandB", description="DescriptionC", package="Package2", article_code=article_code1)
        article_card2 = ArticleCard(brand="BrandA", description="DescriptionB", package="Package1", article_code=article_code2)
        article_card3 = ArticleCard(brand="BrandA", description="DescriptionC", package="Package1", article_code=article_code1)
        article_card4 = ArticleCard(brand="BrandB", description="DescriptionA", package="Package3", article_code=article_code2)
        article_card5 = ArticleCard(brand="BrandA", description="DescriptionC", package="Package2", article_code=article_code1)

        session.add_all([article_code1, article_code2, article_card1, article_card2, article_card3, article_card4, article_card5])
        session.commit()

        # Query and print the ordered article cards
        ordered_cards = query_article_cards_ordered(session)
        for card in ordered_cards:
            print(f"Brand: {card.brand}, Description: {card.description}, Package: {card.package}")


import logging
from typing import List, Optional, Generator
from contextlib import contextmanager
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    relationship,
    Mapped,
    WriteOnlyMapped,
    sessionmaker,
    Session,
)


# ... (rest of your model definitions remain the same) ...


@contextmanager
def db_get_session(db_uri: Optional[str] = None) -> Generator[Session, None, None]:
    if db_uri is None:
        db_uri = ":memory:"
        create_db = True
    else:
        db_path = Path(db_uri)
        create_db = not db_path.exists()
    db_home = "sqlite+pysqlite:///" + db_uri
    db = sa.create_engine(db_home, future=True)
    if create_db:
        Base.metadata.create_all(db)
    SessionLocal = sessionmaker(bind=db)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as panic:
        logging.error(str(panic))
        session.rollback()
    finally:
        session.close()


def iterate_article_cards_ordered_in_batches(session: Session, batch_size: int = 100) -> Generator[ArticleCard, None, None]:
    """Iterates through article_cards ordered by brand, description, and package in batches."""
    query = session.query(ArticleCard).order_by(
        ArticleCard.brand, ArticleCard.description, ArticleCard.package
    )
    for batch in query.yield_per(batch_size):
        yield batch

#Example Usage.
if __name__ == "__main__":
    with db_get_session() as session:
        # Create a large amount of sample data
        for i in range(1000): # simulating a large amount of data
            article_code = ArticleCode(code=f"AC{i:04d}")
            article_card = ArticleCard(brand=f"Brand{i % 3}", description=f"Description{i % 5}", package=f"Package{i % 2}", article_code=article_code)
            session.add_all([article_code, article_card])
        session.commit()

        # Iterate through the article cards in batches
        for card in iterate_article_cards_ordered_in_batches(session, batch_size=50): #batch_size of 50
            print(f"Brand: {card.brand}, Description: {card.description}, Package: {card.package}")






# =====================================================================

def iterate_prices_by_article_code_ordered_by_timestamp(session: Session, article_code_value: str, batch_size: int = 100) -> Generator[Price, None, None]:
    """
    Iterates through prices for a given ArticleCode, ordered by their timestamps in batches.

    Args:
        session: The SQLAlchemy session.
        article_code_value: The code of the ArticleCode to filter by.
        batch_size: The number of prices to fetch in each batch.

    Yields:
        Price objects ordered by their associated timestamp.
    """
    query = session.query(Price).join(Price.article_code).join(Price.timestamp).filter(
        ArticleCode.code == article_code_value
    ).order_by(
        Timestamp.year,
        Timestamp.month,
        Timestamp.day,
        Timestamp.hour,
        Timestamp.minute,
        Timestamp.second
    )
    for batch in query.yield_per(batch_size):
        yield batch

# Example of iterating in batches
if __name__ == "__main__":
    with db_get_session() as session:
        # ... (create sample data as before or more) ...

        article_code_to_query = "TEST001"
        for price in iterate_prices_by_article_code_ordered_by_timestamp(session, article_code_to_query, batch_size=50):
            print(f"  Amount: {price.amount}, Timestamp: {price.timestamp}")



#==============================================================================

import logging
from typing import List, Optional, Generator
from contextlib import contextmanager
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    relationship,
    Mapped,
    WriteOnlyMapped,
    sessionmaker,
    Session,
)


class DatabaseException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logging.error(message)


def get_int(string: str) -> int:
    try:
        return int(string)
    except Exception as panic:
        logging.error(f"*** Error database.get_int")
        logging.error(f"    string: {str(panic)}")
        message = f"*** Error database.get_int ({type(panic).__name__}): {str(panic)}"
        raise DatabaseException(message)


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
    prices: WriteOnlyMapped["Price"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

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
    prices: WriteOnlyMapped["Price"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ArticleCode(Base):
    __tablename__ = "article_codes"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(sa.String(32), unique=True)
    cards: Mapped[List["ArticleCard"]] = relationship(back_populates="article_code")
    prices: WriteOnlyMapped["Price"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


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
def db_get_session(db_uri: Optional[str] = None) -> Generator[Session, None, None]:
    if db_uri is None:
        db_uri = ":memory:"
        create_db = True
    else:
        db_path = Path(db_uri)
        create_db = not db_path.exists()
    db_home = "sqlite+pysqlite:///" + db_uri
    db = sa.create_engine(db_home, future=True)
    if create_db:
        Base.metadata.create_all(db)
    SessionLocal = sessionmaker(bind=db)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as panic:
        logging.error(str(panic))
        session.rollback()
    finally:
        session.close()


def query_prices_by_article_code_ordered_by_timestamp_and_place(session: Session, article_code_value: str) -> List[Price]:
    """
    Queries for prices associated with a given ArticleCode, ordered by timestamp and then by place.

    Args:
        session: The SQLAlchemy session.
        article_code_value: The code of the ArticleCode to filter by.

    Returns:
        A list of Price objects ordered first by timestamp and then by place address.
    """
    return session.query(Price).join(Price.article_code).join(Price.timestamp).join(Price.point_of_sale).join(PointOfSale.place).filter(
        ArticleCode.code == article_code_value
    ).order_by(
        Timestamp.year,
        Timestamp.month,
        Timestamp.day,
        Timestamp.hour,
        Timestamp.minute,
        Timestamp.second,
        Place.address  # Order by place address
    ).all()

# Example Usage
if __name__ == "__main__":
    with db_get_session() as session:
        # Create some sample data
        timestamp1 = Timestamp(year=2025, month=4, day=4, hour=10, minute=0, second=0)
        timestamp2 = Timestamp(year=2025, month=4, day=4, hour=10, minute=15, second=0)

        article_code_a = ArticleCode(code="PRODUCT001")

        city1 = City(name="CityA")
        city2 = City(name="CityB")

        place1 = Place(address="AddressB", city=city1)
        place2 = Place(address="AddressA", city=city1)
        place3 = Place(address="AddressC", city=city2)

        pos1 = PointOfSale(code="POSA", flag="Flag1", business="BusinessX", branch="Branch1", place=place1)
        pos2 = PointOfSale(code="POSB", flag="Flag2", business="BusinessY", branch="Branch2", place=place2)
        pos3 = PointOfSale(code="POSC", flag="Flag3", business="BusinessZ", branch="Branch3", place=place3)

        price1 = Price(amount=100, timestamp=timestamp1, article_code=article_code_a, point_of_sale=pos1)
        price2 = Price(amount=110, timestamp=timestamp1, article_code=article_code_a, point_of_sale=pos2)
        price3 = Price(amount=95, timestamp=timestamp2, article_code=article_code_a, point_of_sale=pos1)
        price4 = Price(amount=120, timestamp=timestamp2, article_code=article_code_a, point_of_sale=pos3)
        price5 = Price(amount=105, timestamp=timestamp1, article_code=article_code_a, point_of_sale=pos3)

        session.add_all([timestamp1, timestamp2, article_code_a, city1, city2, place1, place2, place3, pos1, pos2, pos3, price1, price2, price3, price4, price5])
        session.commit()

        # Query prices for ArticleCode "PRODUCT001" ordered by timestamp and then place
        article_code_to_query = "PRODUCT001"
        ordered_prices = query_prices_by_article_code_ordered_by_timestamp_and_place(session, article_code_to_query)

        print(f"Prices for ArticleCode '{article_code_to_query}' ordered by timestamp and then place:")
        for price in ordered_prices:
            print(f"  Amount: {price.amount}, Timestamp: {price.timestamp}, Place: {price.point_of_sale.place.address}")

#===========================================================================================================================
import logging
from typing import List, Optional, Generator
from contextlib import contextmanager
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    relationship,
    Mapped,
    WriteOnlyMapped,
    sessionmaker,
    Session,
)


class DatabaseException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logging.error(message)


def get_int(string: str) -> int:
    try:
        return int(string)
    except Exception as panic:
        logging.error(f"*** Error database.get_int")
        logging.error(f"    string: {str(panic)}")
        message = f"*** Error database.get_int ({type(panic).__name__}): {str(panic)}"
        raise DatabaseException(message)


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
    prices: WriteOnlyMapped["Price"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

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
    prices: WriteOnlyMapped["Price"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ArticleCode(Base):
    __tablename__ = "article_codes"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(sa.String(32), unique=True)
    cards: Mapped[List["ArticleCard"]] = relationship(back_populates="article_code")
    prices: WriteOnlyMapped["Price"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


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
def db_get_session(db_uri: Optional[str] = None) -> Generator[Session, None, None]:
    if db_uri is None:
        db_uri = ":memory:"
        create_db = True
    else:
        db_path = Path(db_uri)
        create_db = not db_path.exists()
    db_home = "sqlite+pysqlite:///" + db_uri
    db = sa.create_engine(db_home, future=True)
    if create_db:
        Base.metadata.create_all(db)
    SessionLocal = sessionmaker(bind=db)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as panic:
        logging.error(str(panic))
        session.rollback()
    finally:
        session.close()


def query_prices_by_article_code_ordered_by_timestamp_and_city(session: Session, article_code_value: str) -> List[Price]:
    """
    Queries for prices associated with a given ArticleCode, ordered by timestamp and then by city name.

    Args:
        session: The SQLAlchemy session.
        article_code_value: The code of the ArticleCode to filter by.

    Returns:
        A list of Price objects ordered first by timestamp and then by city name.
    """
    return session.query(Price).join(Price.article_code).join(Price.timestamp).join(Price.point_of_sale).join(PointOfSale.place).join(Place.city).filter(
        ArticleCode.code == article_code_value
    ).order_by(
        Timestamp.year,
        Timestamp.month,
        Timestamp.day,
        Timestamp.hour,
        Timestamp.minute,
        Timestamp.second,
        City.name  # Order by city name
    ).all()

# Example Usage
if __name__ == "__main__":
    with db_get_session() as session:
        # Create some sample data
        timestamp1 = Timestamp(year=2025, month=4, day=4, hour=10, minute=0, second=0)
        timestamp2 = Timestamp(year=2025, month=4, day=4, hour=10, minute=15, second=0)

        article_code_a = ArticleCode(code="ITEM001")

        city1 = City(name="Buenos Aires")
        city2 = City(name="Córdoba")
        city3 = City(name="Rosario")

        place1_ba = Place(address="AddressX", city=city1)
        place2_ba = Place(address="AddressY", city=city1)
        place1_co = Place(address="AddressA", city=city2)
        place1_ro = Place(address="AddressB", city=city3)

        pos1_ba = PointOfSale(code="BA01", flag="F1", business="B1", branch="Br1", place=place1_ba)
        pos2_ba = PointOfSale(code="BA02", flag="F2", business="B2", branch="Br2", place=place2_ba)
        pos1_co = PointOfSale(code="CO01", flag="F3", business="B3", branch="Br3", place=place1_co)
        pos1_ro = PointOfSale(code="RO01", flag="F4", business="B4", branch="Br4", place=place1_ro)

        price1_t1_ba = Price(amount=100, timestamp=timestamp1, article_code=article_code_a, point_of_sale=pos1_ba)
        price2_t1_co = Price(amount=110, timestamp=timestamp1, article_code=article_code_a, point_of_sale=pos1_co)
        price3_t2_ba = Price(amount=105, timestamp=timestamp2, article_code=article_code_a, point_of_sale=pos2_ba)
        price4_t2_ro = Price(amount=115, timestamp=timestamp2, article_code=article_code_a, point_of_sale=pos1_ro)
        price5_t1_ro = Price(amount=102, timestamp=timestamp1, article_code=article_code_a, point_of_sale=pos1_ro)

        session.add_all([timestamp1, timestamp2, article_code_a, city1, city2, city3, place1_ba, place2_ba, place1_co, place1_ro, pos1_ba, pos2_ba, pos1_co, pos1_ro, price1_t1_ba, price2_t1_co, price3_t2_ba, price4_t2_ro, price5_t1_ro])
        session.commit()

        # Query prices for ArticleCode "ITEM001" ordered by timestamp and then city
        article_code_to_query = "ITEM001"
        ordered_prices = query_prices_by_article_code_ordered_by_timestamp_and_city(session, article_code_to_query)

        print(f"Prices for ArticleCode '{article_code_to_query}' ordered by timestamp and then city:")
        for price in ordered_prices:
            print(f"  Amount: {price.amount}, Timestamp: {price.timestamp}, City: {price.point_of_sale.place.city.name}")


#==========================================================================================================================
import logging
from typing import List, Optional, Generator
from contextlib import contextmanager
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    relationship,
    Mapped,
    WriteOnlyMapped,
    sessionmaker,
    Session,
)


class DatabaseException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logging.error(message)


def get_int(string: str) -> int:
    try:
        return int(string)
    except Exception as panic:
        logging.error(f"*** Error database.get_int")
        logging.error(f"    string: {str(panic)}")
        message = f"*** Error database.get_int ({type(panic).__name__}): {str(panic)}"
        raise DatabaseException(message)


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
    prices: WriteOnlyMapped["Price"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

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
    prices: WriteOnlyMapped["Price"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ArticleCode(Base):
    __tablename__ = "article_codes"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(sa.String(32), unique=True)
    cards: Mapped[List["ArticleCard"]] = relationship(back_populates="article_code")
    prices: WriteOnlyMapped["Price"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


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
def db_get_session(db_uri: Optional[str] = None) -> Generator[Session, None, None]:
    if db_uri is None:
        db_uri = ":memory:"
        create_db = True
    else:
        db_path = Path(db_uri)
        create_db = not db_path.exists()
    db_home = "sqlite+pysqlite:///" + db_uri
    db = sa.create_engine(db_home, future=True)
    if create_db:
        Base.metadata.create_all(db)
    SessionLocal = sessionmaker(bind=db)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as panic:
        logging.error(str(panic))
        session.rollback()
    finally:
        session.close()


def query_prices_by_article_code_and_city_ordered_by_timestamp_and_pos(session: Session, article_code_value: str, city_name: str) -> List[Price]:
    """
    Queries for prices associated with a given ArticleCode and city,
    ordered by timestamp and then by point of sale code.

    Args:
        session: The SQLAlchemy session.
        article_code_value: The code of the ArticleCode to filter by.
        city_name: The name of the City to filter by.

    Returns:
        A list of Price objects ordered first by timestamp and then by point of sale code.
    """
    return session.query(Price).join(Price.article_code).join(Price.timestamp).join(Price.point_of_sale).join(PointOfSale.place).join(Place.city).filter(
        ArticleCode.code == article_code_value,
        City.name == city_name
    ).order_by(
        Timestamp.year,
        Timestamp.month,
        Timestamp.day,
        Timestamp.hour,
        Timestamp.minute,
        Timestamp.second,
        PointOfSale.code  # Order by point of sale code
    ).all()

# Example Usage
if __name__ == "__main__":
    with db_get_session() as session:
        # Create some sample data
        timestamp1 = Timestamp(year=2025, month=4, day=5, hour=9, minute=0, second=0)
        timestamp2 = Timestamp(year=2025, month=4, day=5, hour=9, minute=30, second=0)
        timestamp3 = Timestamp(year=2025, month=4, day=5, hour=10, minute=0, second=0)

        article_code_x = ArticleCode(code="PRODUCT-X")

        city_a = City(name="Comodoro Rivadavia")
        city_b = City(name="Trelew")

        place_a1 = Place(address="Street 123", city=city_a)
        place_a2 = Place(address="Avenue ABC", city=city_a)
        place_b1 = Place(address="Road XYZ", city=city_b)

        pos_a1_1 = PointOfSale(code="CR-001", flag="Active", business="Store A", branch="Main", place=place_a1)
        pos_a1_2 = PointOfSale(code="CR-002", flag="Open", business="Store B", branch="Downtown", place=place_a1)
        pos_a2_1 = PointOfSale(code="CR-003", flag="New", business="Store A", branch="Uptown", place=place_a2)
        pos_b1_1 = PointOfSale(code="TW-001", flag="Normal", business="Store C", branch="Center", place=place_b1)

        price1 = Price(amount=50, timestamp=timestamp1, article_code=article_code_x, point_of_sale=pos_a1_1)
        price2 = Price(amount=55, timestamp=timestamp2, article_code=article_code_x, point_of_sale=pos_a1_1)
        price3 = Price(amount=60, timestamp=timestamp1, article_code=article_code_x, point_of_sale=pos_a1_2)
        price4 = Price(amount=62, timestamp=timestamp3, article_code=article_code_x, point_of_sale=pos_a1_2)
        price5 = Price(amount=70, timestamp=timestamp1, article_code=article_code_x, point_of_sale=pos_a2_1)
        price6 = Price(amount=75, timestamp=timestamp2, article_code=article_code_x, point_of_sale=pos_a2_1)
        price7 = Price(amount=80, timestamp=timestamp1, article_code=article_code_x, point_of_sale=pos_b1_1)

        session.add_all([timestamp1, timestamp2, timestamp3, article_code_x, city_a, city_b, place_a1, place_a2, place_b1, pos_a1_1, pos_a1_2, pos_a2_1, pos_b1_1, price1, price2, price3, price4, price5, price6, price7])
        session.commit()

        # Query prices for ArticleCode "PRODUCT-X" in "Comodoro Rivadavia" ordered by timestamp and point of sale
        article_code_to_query = "PRODUCT-X"
        city_to_query = "Comodoro Rivadavia"
        ordered_prices = query_prices_by_article_code_and_city_ordered_by_timestamp_and_pos(session, article_code_to_query, city_to_query)

        print(f"Prices for ArticleCode '{article_code_to_query}' in '{city_to_query}' ordered by timestamp and point of sale:")
        for price in ordered_prices:
            print(f"  Amount: {price.amount}, Timestamp: {price.timestamp}, Point of Sale: {price.point_of_sale.code}")


#=========================================================================================================

import logging
from typing import List, Optional, Generator
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    relationship,
    Mapped,
    WriteOnlyMapped,
    sessionmaker,
    Session,
)


class DatabaseException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logging.error(message)


def get_int(string: str) -> int:
    try:
        return int(string)
    except Exception as panic:
        logging.error(f"*** Error database.get_int")
        logging.error(f"    string: {str(panic)}")
        message = f"*** Error database.get_int ({type(panic).__name__}): {str(panic)}"
        raise DatabaseException(message)


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
    prices: WriteOnlyMapped["Price"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"{self.year:4d}{self.month:>02d}{self.day:>02d}{self.hour:>02d}{self.minute:>02d}{self.second:>02d}"

    def to_datetime(self) -> datetime:
        return datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)

    @classmethod
    def from_datetime(cls, dt: datetime) -> "Timestamp":
        return cls(
            year=dt.year, month=dt.month, day=dt.day, hour=dt.hour, minute=dt.minute, second=dt.second
        )


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
    prices: WriteOnlyMapped["Price"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ArticleCode(Base):
    __tablename__ = "article_codes"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(sa.String(32), unique=True)
    cards: Mapped[List["ArticleCard"]] = relationship(back_populates="article_code")
    prices: WriteOnlyMapped["Price"] = relationship(
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


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
def db_get_session(db_uri: Optional[str] = None) -> Generator[Session, None, None]:
    if db_uri is None:
        db_uri = ":memory:"
        create_db = True
    else:
        db_path = Path(db_uri)
        create_db = not db_path.exists()
    db_home = "sqlite+pysqlite:///" + db_uri
    db = sa.create_engine(db_home, future=True)
    if create_db:
        Base.metadata.create_all(db)
    SessionLocal = sessionmaker(bind=db)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as panic:
        logging.error(str(panic))
        session.rollback()
    finally:
        session.close()


def query_prices_by_article_code_city_and_timestamp_ordered_by_pos(
    session: Session, article_code_value: str, city_name: str, target_timestamp: datetime
) -> List[Price]:
    """
    Queries for prices associated with a given ArticleCode, city, and timestamp,
    ordered by point of sale code.

    Args:
        session: The SQLAlchemy session.
        article_code_value: The code of the ArticleCode to filter by.
        city_name: The name of the City to filter by.
        target_timestamp: The specific datetime to filter by.

    Returns:
        A list of Price objects ordered by point of sale code.
    """
    target_ts = Timestamp.from_datetime(target_timestamp)
    return session.query(Price).join(Price.article_code).join(Price.timestamp).join(Price.point_of_sale).join(PointOfSale.place).join(Place.city).filter(
        ArticleCode.code == article_code_value,
        City.name == city_name,
        Timestamp.year == target_ts.year,
        Timestamp.month == target_ts.month,
        Timestamp.day == target_ts.day,
        Timestamp.hour == target_ts.hour,
        Timestamp.minute == target_ts.minute,
        Timestamp.second == target_ts.second,
    ).order_by(
        PointOfSale.code  # Order by point of sale code
    ).all()


def query_prices_by_article_code_city_and_timestamp_ordered_by_timestamp_and_pos(
    session: Session, article_code_value: str, city_name: str, target_timestamp: datetime
) -> List[Price]:
    """
    Queries for prices associated with a given ArticleCode, city, and timestamp,
    ordered by timestamp and then by point of sale code.

    Args:
        session: The SQLAlchemy session.
        article_code_value: The code of the ArticleCode to filter by.
        city_name: The name of the City to filter by.
        target_timestamp: The specific datetime to filter by.

    Returns:
        A list of Price objects ordered first by timestamp and then by point of sale code.
    """
    target_ts = Timestamp.from_datetime(target_timestamp)
    return session.query(Price).join(Price.article_code).join(Price.timestamp).join(Price.point_of_sale).join(PointOfSale.place).join(Place.city).filter(
        ArticleCode.code == article_code_value,
        City.name == city_name,
        Timestamp.year == target_ts.year,
        Timestamp.month == target_ts.month,
        Timestamp.day == target_ts.day,
        Timestamp.hour == target_ts.hour,
        Timestamp.minute == target_ts.minute,
        Timestamp.second == target_ts.second,
    ).order_by(
        Timestamp.year,
        Timestamp.month,
        Timestamp.day,
        Timestamp.hour,
        Timestamp.minute,
        Timestamp.second,
        PointOfSale.code  # Order by point of sale code
    ).all()


# Example Usage
if __name__ == "__main__":
    with db_get_session() as session:
        # Create some sample data
        timestamp1 = Timestamp(year=2025, month=4, day=5, hour=9, minute=0, second=0)
        timestamp2 = Timestamp(year=2025, month=4, day=5, hour=9, minute=0, second=10)
        timestamp3 = Timestamp(year=2025, month=4, day=5, hour=9, minute=30, second=0)

        article_code_y = ArticleCode(code="PRODUCT-Y")

        city_c = City(name="Esquel")

        place_c1 = Place(address="Main St 100", city=city_c)
        place_c2 = Place(address="Side Rd 50", city=city_c)

        pos_c1_a = PointOfSale(code="EQ-001", flag="OK", business="Local Shop", branch="A", place=place_c1)
        pos_c1_b = PointOfSale(code="EQ-002", flag="Good", business="Big Store", branch="B", place=place_c1)
        pos_c2_a = PointOfSale(code="EQ-003", flag="Fine", business="Local Shop", branch="C", place=place_c2)

        price1 = Price(amount=10, timestamp=timestamp1, article_code=article_code_y, point_of_sale=pos_c1_a)
        price2 = Price(amount=11, timestamp=timestamp2, article_code=article_code_y, point_of_sale=pos_c1_a)
        price3 = Price(amount=12, timestamp=timestamp1, article_code=article_code_y, point_of_sale=pos_c1_b)
        price4 = Price(amount=13, timestamp=timestamp1, article_code=article_code_y, point_of_sale=pos_c2_a)
        price5 = Price(amount=14, timestamp=timestamp3, article_code=article_code_y, point_of_sale=pos_c1_a)

        session.add_all([timestamp1, timestamp2, timestamp3, article_code_y, city_c, place_c1, place_c2, pos_c1_a, pos_c1_b, pos_c2_a, price1, price2, price3, price4, price5])
        session.commit()

        # Query prices for ArticleCode "PRODUCT-Y" in "Esquel" for a specific timestamp
        article_code_to_query = "PRODUCT-Y"
        city_to_query = "Esquel"
        timestamp_to_query = datetime(2025, 4, 5, 9, 0, 0)  # Example timestamp

        ordered_prices = query_prices_by_article_code_city_and_timestamp_ordered_by_timestamp_and_pos(
            session, article_code_to_query, city_to_query, timestamp_to_query
        )

        print(f"Prices for ArticleCode '{article_code_to_query}' in '{city_to_query}' at '{timestamp_to_query}' ordered by timestamp and point of sale:")
        for price in ordered_prices:
            print(f"  Amount: {price.amount}, Timestamp: {price.timestamp}, Point of Sale: {price.point_of_sale.code}")

        print("\nQuerying ordered only by Point of Sale for the same criteria:")
        ordered_by_pos_only = query_prices_by_article_code_city_and_timestamp_ordered_by_pos(
            session, article_code_to_query, city_to_query, timestamp_to_query
        )
        for price in ordered_by_pos_only:
            print(f"  Amount: {price.amount}, Timestamp: {price.timestamp}, Point of Sale: {price.point_of_sale.code}")
