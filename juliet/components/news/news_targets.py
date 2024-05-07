from typing import Protocol
from components.news.models import News


class NewsTarget(Protocol):
    def start(self) -> None:
        ...
    
    def add(self, news: News) -> None:
        ...
        
    def stop(self) -> None:
        ...
    
