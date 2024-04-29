from typing import Protocol, List
from dataclasses import dataclass

@dataclass    
class Record:
    number: int
    publication_date: str 
    guid: str 


class News(Protocol):
    @property
    def kind(self) -> str:
        ...

    @property
    def record(self) -> Record:
        ...
    
    @property
    def as_html(self) -> str:
        ...

