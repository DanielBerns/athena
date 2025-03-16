from sqlalchemy.orm import Session

from database import City, Place

def insert_new_place(
    session: Session,
    address: str,
    city_name: str,
    state_code: str  # Added state_code to locate the city correctly
) -> None:
    """
    Inserts a new Place into the database.

    Args:
        session: The SQLAlchemy session.
        address: The address of the place.
        city_name: The name of the city where the place is located.
        state_code: The code of the state where the city is located.
    """

    # 1. Retrieve the City
    # First, we need to find the city to which this place belongs.
    # We'll query based on both city_name and state_code to ensure we get the correct city.
    city = session.query(City).filter_by(name=city_name).join(City.state).filter_by(code=state_code).first()

    # If the city doesn't exist, we can't proceed. You might want to handle this differently
    # (e.g., create the city or raise an exception).  For this example, we'll raise a ValueError.
    if not city:
        raise ValueError(f"City with name '{city_name}' in state '{state_code}' not found.")

    # 2. Create the new Place object
    new_place = Place(
        address=address,
        city=city  # Assign the retrieved City object
    )

    # 3. Add and commit
    session.add(new_place)
    session.commit()  # Commit within the function



def insert_new_place(
    session: Session,
    address: str,
    city_name: str,
    state_code: str
) -> None:
    """
    Inserts a new Place into the database, checking for the existence of the State.

    Args:
        session: The SQLAlchemy session.
        address: The address of the place.
        city_name: The name of the city where the place is located.
        state_code: The code of the state where the city is located.
    """
    # 1. Retrieve the State
    # Before proceeding, verify that the state exists.
    state = session.query(State).filter_by(code=state_code).first()
    if not state:
        raise DatabaseException(f"State with code '{state_code}' not found.")

    # 2. Retrieve the City
    # Now, find the city within the given state.
    city = session.query(City).filter_by(name=city_name, state_id=state.id).first()
    if not city:
        raise Database(f"City with name '{city_name}' in state '{state_code}' not found.")

    # 3. Create the new Place object
    new_place = Place(
        address=address,
        city=city
    )

    # 4. Add and commit
    session.add(new_place)
    session.commit()



def insert_new_city(
    session: Session,
    city_name: str,
    state_code: str
) -> None:
    """
    Inserts a new City into the database, checking for the existence of the State.

    Args:
        session: The SQLAlchemy session.
        city_name: The name of the city to insert.
        state_code: The code of the state where the city is located.
    """
    # 1. Retrieve the State
    # Verify that the state exists before creating the city.
    state = session.query(State).filter_by(code=state_code).first()
    if not state:
        raise ValueError(f"State with code '{state_code}' not found.")

    # 2. Create the new City object
    new_city = City(
        name=city_name,
        state=state  # Assign the retrieved State object
    )

    # 3. Add and commit
    session.add(new_city)
    session.commit()









from sqlalchemy.orm import Session

from database import PointOfSaleCode

def insert_new_point_of_sale_code_if_not_exists(
    session: Session,
    code: str
) -> PointOfSaleCode:
    """
    Inserts a new PointOfSaleCode into the database only if a code with the
    same value does not already exist.

    Args:
        session: The SQLAlchemy session.
        code: The code for the point of sale.

    Returns:
        The PointOfSaleCode object (either the existing one or the newly created one).
    """
    # 1. Check if the PointOfSaleCode already exists
    existing_point_of_sale_code = session.query(PointOfSaleCode).filter_by(code=code).first()

    # 2. If it doesn't exist, create and add it
    if not existing_point_of_sale_code:
        new_point_of_sale_code = PointOfSaleCode(
            code=code
        )
        session.add(new_point_of_sale_code)
        session.commit()  # Commit immediately to get the new object's ID
        return new_point_of_sale_code
    else:
        return existing_point_of_sale_code

if __name__ == "__main__":
    from database import db_create_session

    with db_create_session() as session:
        # Example usage:
        point_of_sale_code = insert_new_point_of_sale_code_if_not_exists(
            session=session,
            code="POS-5678"
        )
        print(f"Point of sale code: {point_of_sale_code.code} (ID: {point_of_sale_code.id})")

        # Example of trying to insert a duplicate:
        point_of_sale_code = insert_new_point_of_sale_code_if_not_exists(
            session=session,
            code="POS-5678"
        )
        print(f"Point of sale code: {point_of_sale_code.code} (ID: {point_of_sale_code.id})")  # Will print the same object


def insert_point_of_sale_if_not_exists(
    session: Session,
    code: str,
    flag: str,
    business: str,
    branch: str,
    place_id: int,
) -> Optional[PointOfSale]:
    """
    Inserts a PointOfSale into the database if one with the given code
    does not already exist.

    Args:
        session: The SQLAlchemy Session to use.
        code: The code of the point of sale.
        flag: The flag of the point of sale.
        business: The business of the point of sale.
        branch: The branch of the point of sale.
        place_id: The ID of the place associated with the point of sale.

    Returns:
        The PointOfSale object if it was created or if it already exists,
        None if an error occurred.
    """
    try:
        # Check if a PointOfSale with the given code already exists
        existing_point_of_sale = session.execute(
            select(PointOfSale).filter_by(code=code)
        ).scalar_one_or_none()

        if existing_point_of_sale:
            return existing_point_of_sale  # PointOfSale already exists

        # Create a new PointOfSale object
        new_point_of_sale = PointOfSale(
            code=code,
            flag=flag,
            business=business,
            branch=branch,
            place_id=place_id,
        )

        # Add the new PointOfSale to the session
        session.add(new_point_of_sale)

        # Commit the session to persist the changes
        session.commit()

        return new_point_of_sale
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()  # Rollback in case of error
        return None






from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional

from database import Price


def insert_price_if_not_exists(
    session: Session,
    amount: int,
    timestamp_id: int,
    article_code_id: int,
    point_of_sale_id: int,
) -> Optional[Price]:
    """
    Inserts a Price into the database if a price with the given attributes
    does not already exist.

    Args:
        session: The SQLAlchemy Session to use.
        amount: The amount of the price.
        timestamp_id: The ID of the timestamp associated with the price.
        article_code_id: The ID of the article code associated with the price.
        point_of_sale_id: The ID of the point of sale associated with the price.

    Returns:
        The Price object if it was created or if it already exists,
        None if an error occurred.
    """
    try:
        # Check if a Price with the given attributes already exists
        existing_price = session.execute(
            select(Price).filter_by(
                amount=amount,
                timestamp_id=timestamp_id,
                article_code_id=article_code_id,
                point_of_sale_id=point_of_sale_id,
            )
        ).scalar_one_or_none()

        if existing_price:
            return existing_price  # Price already exists

        # Create a new Price object
        new_price = Price(
            amount=amount,
            timestamp_id=timestamp_id,
            article_code_id=article_code_id,
            point_of_sale_id=point_of_sale_id,
        )

        # Add the new Price to the session
        session.add(new_price)

        # Commit the session to persist the changes
        session.commit()

        return new_price
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()  # Rollback in case of error
        return None

if __name__ == '__main__':
    from database import db_create_session, Timestamp, ArticleCode, PointOfSale

    # Example Usage
    with db_create_session() as session:
        # Create dummy data for the relationships
        # Replace this with your actual data retrieval or creation logic

        # Create a Timestamp
        new_timestamp = Timestamp(year=2024, month=10, day=27, hour=12, minute=30, second=0)
        session.add(new_timestamp)
        session.commit()

        # Create an ArticleCode
        new_article_code = ArticleCode(code="ARTICLE-123")
        session.add(new_article_code)
        session.commit()

        # Create a PointOfSale (assuming you have a Place associated with it)
        # For simplicity, let's assume a Place with ID 1 exists
        new_point_of_sale = PointOfSale(code="POS-456", flag="Active", business="Example", branch="Branch", place_id=1)
        session.add(new_point_of_sale)
        session.commit()


        # Example: Inserting a new Price
        price = insert_price_if_not_exists(
            session=session,
            amount=100,
            timestamp_id=new_timestamp.id,
            article_code_id=new_article_code.id,
            point_of_sale_id=new_point_of_sale.id,
        )

        if price:
            print(f"Price inserted or found: {price.amount}")
        else:
            print("Failed to insert Price.")

        # Example: Trying to insert the same Price again
        price_again = insert_price_if_not_exists(
            session=session,
            amount=100,
            timestamp_id=new_timestamp.id,
            article_code_id=new_article_code.id,
            point_of_sale_id=new_point_of_sale.id,
        )
        if price_again:
            print(f"Price found: {price_again.amount}")
        else:
            print("Failed to insert Price.")


from sqlalchemy.orm import Session
from typing import Optional

from database import ArticleCard


def insert_article_card(
    session: Session,
    brand: str,
    description: str,
    package: str,
    article_code_id: int,
) -> ArticleCard:
    """
    Inserts a new ArticleCard into the database.

    Args:
        session: The SQLAlchemy Session to use.
        brand: The brand of the article card.
        description: The description of the article card.
        package: The package information of the article card.
        article_code_id: The ID of the article code associated with the article card.

    Returns:
        The newly created ArticleCard object.
    """
    try:
        # Create a new ArticleCard object
        new_article_card = ArticleCard(
            brand=brand,
            description=description,
            package=package,
            article_code_id=article_code_id,
        )

        # Add the new ArticleCard to the session
        session.add(new_article_card)

        # Commit the session to persist the changes
        session.commit()

        return new_article_card
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()  # Rollback in case of error
        return None  # Or you might want to raise the exception
