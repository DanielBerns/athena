import logging
from pathlib import Path

from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from components.precios_claros.database import (
    Timestamp,
    Tag,
    State,
    City,
    Place,
    PointOfSaleCode,
    PointOfSaleRepresentation,
    ArticleCode,
    ArticleRepresentation,
    Price
)

def find_or_create_timestamp(
    session: Session,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int
) -> Timestamp:
    """Finds or creates a Timestamp record."""
    timestamp = session.query(Timestamp).filter_by(
        year=year, month=month, day=day, hour=hour, minute=minute, second=second
    ).first()
    if not timestamp:
        timestamp = Timestamp(
            year=year, month=month, day=day, hour=hour, minute=minute, second=second
        )
        session.add(timestamp)
        session.flush()
    return timestamp

def find_or_create_tag(
    session: Session,
    name: str
) -> Tag:
    """Finds or creates a Tag record."""
    tag = session.query(Tag).filter_by(name=name).first()
    if not tag:
        tag = Tag(name=name)
        session.add(tag)
        session.flush()
    return tag

def find_or_create_state(
    session: Session,
    code: str,
    name: str
) -> State:
    """Finds or creates a State record."""
    state = session.query(State).filter_by(code=code, name=name).first()
    if not state:
        state = State(code=code, name=name)
        session.add(state)
        session.flush()
    return state

def find_or_create_city(
    session: Session,
    name: str,
    state_id: int
) -> City:
    """Finds or creates a City record."""
    city = session.query(City).filter_by(name=name, state_id=state_id).first()
    if not city:
        city = City(name=name, state_id=state_id)
        session.add(city)
        session.flush()
    return city

def find_or_create_place(
    session: Session,
    address: str,
    city_id: int
) -> Place:
    """Finds or creates a Place record."""
    place = session.query(Place).filter_by(address=address, city_id=city_id).first()
    if not place:
        place = Place(address=address, city_id=city_id)
        session.add(place)
        session.flush()
    return place

def find_or_create_point_of_sale_code(
    session: Session,
    code: str
) -> PointOfSaleCode:
    """Finds or creates a PointOfSaleCode record."""
    point_of_sale_code = session.query(PointOfSaleCode).filter_by(code=code).first()
    if not point_of_sale_code:
        point_of_sale_code = PointOfSaleCode(code=code)
        session.add(point_of_sale_code)
        session.flush()
    return point_of_sale_code

def find_or_create_point_of_sale_representation(
    session: Session,
    flag: str,
    business: str,
    branch: str,
    point_of_sale_code_id: int,
    place_id: int
) -> PointOfSaleRepresentation:
    """Finds or creates a PointOfSaleRepresentation record."""
    representation = session.query(PointOfSaleRepresentation).filter_by(
        flag=flag, business=business, branch=branch, point_of_sale_code_id=point_of_sale_code_id, place_id=place_id
    ).first()
    if not representation:
        representation = PointOfSaleRepresentation(
            flag=flag, business=business, branch=branch, point_of_sale_code_id=point_of_sale_code_id, place_id=place_id
        )
        session.add(representation)
        session.flush()
    return representation

def find_or_create_article_code(
    session: Session,
    code: str
) -> ArticleCode:
    """Finds or creates an ArticleCode record."""
    article_code = session.query(ArticleCode).filter_by(code=code).first()
    if not article_code:
        article_code = ArticleCode(code=code)
        session.add(article_code)
        session.flush()
    return article_code

def find_or_create_article_representation(
    session: Session,
    brand: str,
    description: str,
    package: str,
    article_code_id: int
) -> ArticleRepresentation:
    """Finds or creates an ArticleRepresentation record."""
    representation = session.query(ArticleRepresentation).filter_by(
        brand=brand, description=description, package=package, article_code_id=article_code_id
    ).first()
    if not representation:
        representation = ArticleRepresentation(
            brand=brand, description=description, package=package, article_code_id=article_code_id
        )
        session.add(representation)
        session.flush()
    return representation

def find_or_create_price(
    session: Session,
    amount: int,
    timestamp_id: int,
    article_code_id: int,
    point_of_sale_code_id: int
) -> Price:
    """Finds or creates a Price record."""
    price = session.query(Price).filter_by(
        timestamp_id=timestamp_id,
        article_code_id=article_code_id,
        point_of_sale_code_id=point_of_sale_code_id
    ).first()
    if not price:
        price = Price(
            amount=amount,
            timestamp_id=timestamp_id,
            article_code_id=article_code_id,
            point_of_sale_code_id=point_of_sale_code_id
        )
        session.add(price)
        session.flush()
    return price

def find_or_create_tagged_article(
    session: Session,
    tag_id: int,
    article_code_id: int
) -> TaggedArticle:
    """Finds or creates a TaggedArticle record."""
    tagged_article = session.query(TaggedArticle).filter_by(
        tag_id=tag_id,
        article_code_id=article_code_id
    ).first()
    if not tagged_article:
        tagged_article = TaggedArticle(tag_id=tag_id, article_code_id=article_code_id)
        session.add(tagged_article)
        session.flush()
    return tagged_article

def find_or_create_tagged_point_of_sale(
    session: Session,
    tag_id: int,
    point_of_sale_code_id: int
) -> TaggedPointOfSale:
    """Finds or creates a TaggedPointOfSale record."""
    tagged_point_of_sale = session.query(TaggedPointOfSale).filter_by(tag_id=tag_id, point_of_sale_code_id=point_of_sale_code_id).first()
    if not tagged_point_of_sale:
        tagged_point_of_sale = TaggedPointOfSale(tag_id=tag_id, point_of_sale_code_id=point_of_sale_code_id)
        session.add(tagged_point_of_sale)
        session.flush()
    return tagged_point_of_sale
