from typing import Protocol, List, Tuple, Dict
from dataclasses import dataclass

def year_month_day(attributes: Dict[str, str]) -> Tuple[int, int, int]:
    timestamp = attributes["timestamp"]
    return int(timestamp[:4]), int(timestamp[4:6]), int(timestamp[6:])
    
@dataclass    
class Record:
    number: int
    publication_date: str
    guid: str
    year: int
    month: int 
    day: int


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
        
    @property
    def plain_text(self) -> str:
        ...

