from pathlib import Path
from typing import Generator, Dict, List
from uuid import uuid4
from bs4 import BeautifulSoup

from components.helpers import classname
from components.news.models import Record, News, year_month_day


class Paragraph:
    def __init__(self, record: Record, data: List[str], label: str) -> None:
        self._record: Record = record
        self._data: List[str] = data
        self._label: str = label
        
    @property
    def record(self) -> Record:
        return self._record

    @property
    def data(self) -> List[str]:
        return self._data
    
    @property
    def label(self) -> str:
        return self._label
    
    @property
    def as_html(self) -> str:
        parts = [f"<span>{dd:s}</span>" for dd in self._data]
        if self._label:
            parts.append(self._label)
        return " - ".join(parts)

    @property
    def plain_text(self) -> str:
        data = " ".join(self._data)
        return f"{self.label:s}. {data:s}" if self.label else data


class NewsADNSUR:
    def __init__(
        self,
        tag: str,
    ) -> None:
        self._tag: str = tag
        self._content: List[Paragraph] = []

    @property
    def tag(self) -> str:
        return self._tag

    def add(self, record: Record, data: List[str], label: str) -> None:
        paragraph = Paragraph(record, data, label)
        self._content.append(paragraph)

    @property
    def content(self) -> List[Paragraph]:
        return self._content
    
    @property
    def kind(self) -> str:
        return classname(self)
    
    @property
    def as_html(self) -> str:
        # def show_guid(record: Record) -> str:
        #     return f'<a href="{record.guid:s}">enlace</a>' if record.guid else ""
        
        return ''.join([f"<p>{paragraph.as_html:s}</p>" for paragraph in self.content])

    @property 
    def plain_text(self) -> str:
        return "\n".join(paragraph.plain_text for paragraph in self.content)


class ADNSUR:

    def __init__(self) -> None:
        self._identifier: str = "adnsur"
        self._name: str = "page"
        self._suffix: str = ".html"
    
    @property
    def identifier(self) -> str:
        return self._identifier
    
    @property
    def name(self) -> str:
        return self._name
        
    @property
    def suffix(self) -> str:
        return self._suffix
   
    def read_span_rows(
        self, 
        soup: BeautifulSoup,
        year: int,
        month: int,
        day: int
    ) -> Generator[News, None, None]:
        find_spans_within_container_divs = [    
            div.find_all("span") for div in soup.find_all("div", class_="container")    
        ]
        for spans_within_container_div in find_spans_within_container_divs:
            for span_number, span in enumerate(spans_within_container_div):
                if len(span) != 3:
                    continue
                strong_tag = span.find_all("strong")
                if len(strong_tag) != 1:
                    continue
                class_number_span_tags = span.find_all("span", class_="number")
                data = [a_span.text for a_span in class_number_span_tags]
                if len(data) == 0:
                    continue
                data.insert(0, strong_tag[0].text)
                news = NewsADNSUR("html-span")
                publication_date = "unknown"
                guid = str(uuid4())
                record: Record = Record(span_number, publication_date, guid, year, month, day)    
                label = ""   
                news.add(record, data, label)
                yield news

    def read_link_rows(
        self, 
        soup: BeautifulSoup,
        year: int,
        month: int,
        day: int
    ) -> Generator[News, None, None]:
        find_links_within_divs = [div.find_all("a") for div in soup.find_all("div")]
        for links_within_divs in find_links_within_divs:
            for link_number, link in enumerate(links_within_divs):
                if link:
                    data = [text_fragment for text_fragment in link.stripped_strings]
                    if data:
                        news = NewsADNSUR("html-link")                                            
                        publication_date = "unknown"
                        guid = link.get("href", str(uuid4())) 
                        record: Record = Record(link_number, publication_date, guid, year, month, day)    
                        label = link.get("aria-label", "")
                        news.add(record, data, label)
                        yield news
            
    def execute(self, content: str, attributes: Dict[str, str]) -> Generator[News, None, None]:
        year, month, day = year_month_day(attributes)
        soup = BeautifulSoup(content, "html.parser")
        yield from self.read_span_rows(soup, year, month, day)
        yield from self.read_link_rows(soup, year, month, day)
        
