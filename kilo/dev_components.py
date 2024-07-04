from typing import Protocol

class MessageWriter(Protocol):
    def write(self, message: Dict[str, str]) -> None:
        ...

class MessageReader(Protocol):
    def read(self) -> Dict[str, str]:
        ...
        

class CRUD:
  def __init__(self) -> None:
    pass

  def create(self, message: Dict[str, str]) -> T:
    """Creates a new instance of the model.

    Args:
      message: A dictionary containing the data for the new instance.

    Returns:
      A new instance of the model.

    Raises:
      NotImplementedError: If the concrete subclass doesn't implement this method.
    """
    raise NotImplementedError("create method not implemented")

  def read(self, id: int) -> T:
    """Reads an existing instance of the model by its ID.

    Args:
      id: The ID of the instance to read.

    Returns:
      The instance of the model with the given ID.

    Raises:
      NotImplementedError: If the concrete subclass doesn't implement this method.
    """
    raise NotImplementedError("read method not implemented")

  def update(self, id: int, message: Dict[str, str]) -> T:
    """Updates an existing instance of the model by its ID.

    Args:
      id: The ID of the instance to update.
      message: A dictionary containing the data to update the instance with.

    Returns:
      The updated instance of the model.

    Raises:
      NotImplementedError: If the concrete subclass doesn't implement this method.
    """
    raise NotImplementedError("update method not implemented")

  def delete(self, id: int) -> None:
    """Deletes an existing instance of the model by its ID.

    Args:
      id: The ID of the instance to delete.

    Raises:
      NotImplementedError: If the concrete subclass doesn't implement this method.
    """
    raise NotImplementedError("delete method not implemented")

    
    
class ArticleCRUD:
    def create(self, event: Dict[str, str]) -> Article:
        pass
    
    def read(self, identifier: int) -> Article:
        pass
    
    def update(self, identifier: int, event: Dict[str, str]) -> Article:
        pass

    def delete(self, identifier: int) -> None:
        pass


class StateCRUD:
    def create(self, event: Dict[str, str]) -> State:
        pass
    
    def read(self, identifier: int) -> State:
        pass
    
    def update(self, identifier: int, event: Dict[str, str]) -> State:
        pass

    def delete(self, identifier: int) -> None:
        pass
    
class CityCRUD:
    def create(self, event: Dict[str, str]) -> City:
        pass
    
    def read(self, identifier: int) -> City:
        pass
    
    def update(self, identifier: int, event: Dict[str, str]) -> City:
        pass

    def delete(self, identifier: int) -> None:
        pass

class AddressCRUD:
    def create(self, event: Dict[str, str]) -> Address:
        pass
    
    def read(self, identifier: int) -> Address:
        pass
    
    def update(self, identifier: int, event: Dict[str, str]) -> Address:
        pass

    def delete(self, identifier: int) -> None:
        pass


class PointOfSaleCRUD:
    def create(self, event: Dict[str, str]) -> PointOfSale:
        pass
    
    def read(self, identifier: int) -> PointOfSale:
        pass
    
    def update(self, identifier: int, event: Dict[str, str]) -> PointOfSale:
        pass

    def delete(self, identifier: int) -> None:
        pass


class TimestampCRUD:
    def create(self, event: Dict[str, str]) -> Timestamp:
        pass
    
    def read(self, identifier: int) -> Timestamp:
        pass
    
    def update(self, identifier: int, event: Dict[str, str]) -> Timestamp:
        pass

    def delete(self, identifier: int) -> None:
        pass
