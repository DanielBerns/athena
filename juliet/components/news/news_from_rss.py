from pathlib import Path
from typing import Generator, Dict
from bs4 import BeautifulSoup

from components.helpers import classname
from components.news.models import Record, News

# import pdb

class NewsRSS:
    def __init__(
        self,
        record: Record,
        title: str,
        content: str
    ) -> None:
        self._record: Record = record
        self._title: str = title
        self._content: str = content

    @property
    def kind(self) -> str:
        return classname(self)
    
    @property
    def record(self) -> Record:
        return self._record
    
    @property
    def as_html(self) -> str:
        # pdb.set_trace()
        return f"<p><span>{self.title:s}</span>: <span>{self.content:s}</span> <a href='{self.record.guid:s}'>enlace</a></p>"
        
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def content(self) -> str:
        return self._content


class RSS:

    def __init__(self, identifier: str, name: str = "info", suffix: str = ".xml") -> None:
        self._identifier: str = identifier
        self._name: str = name
        self._suffix: str = suffix
    
    @property
    def identifier(self) -> str:
        return self._identifier
    
    @property
    def name(self) -> str:
        return self._name
        
    @property
    def suffix(self) -> str:
        return self._suffix

    
    def read_item_rows(self, soup: BeautifulSoup) -> Generator[News, None, None]:
        all_items = soup.find_all('item')
        
        for item_number, item in enumerate(all_items):
            try:
                publication_date = item.find('pubDate').text            
                guid = item.find('guid').text
                title = item.find('title').text
                content = item.find('description').text
                record: Record = Record(item_number, publication_date, guid)    
                yield NewsRSS(record, title, content)
            except Exception as panic:
                pass

    def execute(self, content: str, attributes: Dict[str, str]) -> Generator[News, None, None]:
        soup = BeautifulSoup(content, "xml")
        yield from self.read_item_rows(soup)

    
