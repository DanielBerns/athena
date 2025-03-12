from typing import Optional
from contextlib import contextmanager
from sqlalchemy.orm import Session
from . import (  # Assuming your models are in the same directory or a parent package
    State,
    City,
    Place,
    db_create_session,
    db_open_session
)

def insert_state(session: Session, code: str, name: str) -> State:
    """Inserts a new state into the database."""
    state = State(code=code, name=name)
    session.add(state)
    session.flush()  # To get the generated ID
    return state

def insert_city(session: Session, name: str, state_id: int) -> City:
    """Inserts a new city into the database."""
    city = City(name=name, state_id=state_id)
    session.add(city)
    session.flush()  # To get the generated ID
    return city

def insert_place(session: Session, address: str, city_id: int) -> Place:
    """Inserts a new place into the database."""
    place = Place(address=address, city_id=city_id)
    session.add(place)
    session.flush()  # To get the generated ID
    return place

def insert_state_city_place(session: Session, state_code: str, state_name: str, city_name: str, place_address: str) -> Place:
    """Inserts a state, city, and place into the database, handling existing entries."""

    # Check if the state already exists
    state = session.query(State).filter_by(code=state_code).first()
    if not state:
        state = insert_state(session, state_code, state_name)

    # Check if the city already exists
    city = session.query(City).filter_by(name=city_name, state_id=state.id).first()
    if not city:
        city = insert_city(session, city_name, state.id)

    # Check if the place already exists
    place = session.query(Place).filter_by(address=place_address, city_id=city.id).first()
    if not place:
        place = insert_place(session, place_address, city.id)

    return place

def insert_multiple_state_city_places(session: Session, data: list[dict])->list[Place]:
    """
    Inserts multiple states, cities, and places based on a list of dictionaries.

    Args:
        session: The SQLAlchemy session.
        data: A list of dictionaries, where each dictionary represents a state, city, and place.
              Each dictionary should have the keys 'state_code', 'state_name', 'city_name', and 'place_address'.

    Returns:
        A list of Place objects that were created or retrieved.
    """
    places = []
    for item in data:
        place = insert_state_city_place(session,
                                    item['state_code'],
                                    item['state_name'],
                                    item['city_name'],
                                    item['place_address'])
        places.append(place)
    return places

# Example usage with db_create_session context manager:
def example_usage(db_uri: Optional[str] = None):
    with db_create_session(db_uri) as session:
        # Single insertion
        state = insert_state(session, "CA", "California")
        city = insert_city(session, "Los Angeles", state.id)
        place = insert_place(session, "123 Main St", city.id)
        print(f"Inserted place: {place.address} in {city.name}, {state.name}")

        # Combined insertion
        place2 = insert_state_city_place(session, "NY", "New York", "New York City", "456 Broadway")
        print(f"Inserted place: {place2.address} in New York City, New York")

        # Multiple insertions
        data = [
            {"state_code": "TX", "state_name": "Texas", "city_name": "Austin", "place_address": "789 Congress Ave"},
            {"state_code": "FL", "state_name": "Florida", "city_name": "Miami", "place_address": "100 Ocean Dr"}
        ]
        places = insert_multiple_state_city_places(session, data)
        for p in places:
            print(f"Inserted place: {p.address} in {p.city.name}, {p.city.state.name}")

if __name__ == "__main__":
    example_usage()
