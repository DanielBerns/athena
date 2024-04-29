from typing import Protocol, Generator, Dict
from components.news.models import News

class NewsProcessor(Protocol):
    def execute(self, content: str, attributes: Dict[str, str]) -> Generator[News, None, None]:
        ...

    @property
    def identifier(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...
        
    @property
    def suffix(self) -> str:
        ...
        
