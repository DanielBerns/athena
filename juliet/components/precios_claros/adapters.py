from pathlib import Path
from jinja2 import Template
from typing import Tuple, List, Dict
from components.helpers import classname
from components.core.application import show
from components.precios_claros.models import (
    ArticleWithPricesTable, 
    ArticleWithPrices, 
    PointsOfSaleTable)


import pdb

class Child:

    def __init__(self, 
                 pattern: str, 
                 number: int,
                 header: str
    ) -> None:
        self._pattern: str = pattern        
        self._header: str = header
        self._content: List[ArticleWithPrices] = []        
        if len(pattern) == 0 or number < 0:
            self._url: str = "/error/empty_child.html"
            self._store_key: str = 'xxx'
            self._name: str = 'xxxxxx'
            show(f"{classname(self):s}.__init__: bad parameters - "
                 f"{pattern:s} - {number:d}"
            )
        else:
            store_key: str = f"{number // 256:03d}"
            name = f"{number:06d}"            
            self._store_key: str = store_key
            self._url: str = f"/{store_key:s}/{name:s}"
            self._name: str = name

    @property
    def pattern(self) -> str:
        return self._pattern

    @property
    def store_key(self) -> str:
        return self._store_key

    @property
    def url(self) -> str:
        return self._url

    @property
    def name(self) -> str:
        return self._name

    @property
    def header(self) -> str:
        return self._header
    
    @property
    def content(self) -> List[ArticleWithPrices]:
        return self._content
    
    def add(
        self, 
        article_with_prices_table: ArticleWithPricesTable,
        points_of_sale_table: PointsOfSaleTable
    ) -> None:
        for article_with_prices in article_with_prices_table.get(self.pattern):
            self.content.append(article_with_prices)

    def write(self, template_text: str) -> str:
        template = Template(template_text)
        return template.render(
            title=self.pattern,
            local_style="",             
            content=self.content,
            header=self.header
        )

        
class Index:
    def __init__(
        self, 
        root: str,        
        sample_key: str,
        province: str = "",
        city: str = ""
    ) -> None:
        self._content: List[Child] = []
        self._root: str = root
        selectors = {}
        if province:
            selectors['province'] = province
        if city:
            selectors['city'] = city
        label = ' _ '.join(selectors.values())
        year, month, day = sample_key[0:4], sample_key[4:6], sample_key[6:8]
        header = str = f"{year:s}/{month:s}/{day:s} en {label:s}"
        self._index_header: str = header
        self._child_header: str = header
        self._selectors = selectors
    
    @property
    def content(self) -> List[Child]:
        return self._content

    @property
    def root(self) -> str:
        return self._root
    
    @property
    def sample_key(self) -> str:
        return self._sample_key

    @property
    def index_header(self) -> str:
        return self._index_header

    @property
    def child_header(self) -> str:
        return self._child_header
    
    @property
    def selectors(self) -> str:
        return self._selectors

    def add(self, pattern: str) -> Child:
        child = Child(
            pattern, 
            len(self.content), 
            self.child_header
        )
        self.content.append(child)
        return child

    def write(self, template_text: str) -> str:
        template = Template(template_text)
        return template.render(
            title=self.index_header,
            local_style="", 
            content=self.content,
            root=self.root
        )
