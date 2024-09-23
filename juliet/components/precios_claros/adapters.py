from pathlib import Path
from jinja2 import Template
from typing import Tuple, List, Dict, Optional
from components.helpers import classname
from components.core.application import show
from components.precios_claros.models import (
    PointOfSale,
    ArticleWithPricesTable,
    ArticleWithPrices,
    PointsOfSaleTable,
    DeltaArticleWithPrices,
)
from components.precios_claros.html import (
    HTML_CHILD, 
    HTML_INDEX, 
    HTML_ROOT,
    DeltaChildConstants,
    build_DeltaChildConstants,
    DeltaIndexConstants,
    build_DeltaIndexConstants,
    DeltaRootConstants,
    build_DeltaRootConstants,
)


class DeltaChild:
    ATTRIBUTES = ("w3-pale-blue", "w3-pale-green w3-text-black", "w3-red w3-text-white", "w3-blue w3-text-white")

    def __init__(
        self,
        pattern: str,
        number: int,
        root_constants: DeltaRootConstants,
        index_constants: DeltaIndexConstants
    ) -> None:
        self._root_constants = root_constants
        self._index_constants = index_constants
        self._child_constants = build_DeltaChildConstants(pattern, number)
        self._bravo_table: ArticleWithPricesTable = ArticleWithPricesTable()        
        self._alpha_table: ArticleWithPricesTable = ArticleWithPricesTable()
        self._now_table: ArticleWithPricesTable = ArticleWithPricesTable()

    @property
    def root_constants(self) -> DeltaRootConstants:
        return self._root_constants
        
    @property
    def index_constants(self) -> DeltaIndexConstants:
        return self._index_constants

    @property
    def child_constants(self) -> DeltaChildConstants:
        return self._child_constants

    @property
    def bravo_table(self) -> ArticleWithPricesTable:
        return self._bravo_table

    @property
    def alpha_table(self) -> ArticleWithPricesTable:
        return self._alpha_table

    @property
    def now_table(self) -> ArticleWithPricesTable:
        return self._now_table

    def fill_table(
        self,
        article_with_prices_table: ArticleWithPricesTable,
        points_of_sale: List[PointOfSale],
        child_table: ArticleWithPricesTable
    ) -> None:
        show(f"table {self.child_constants.store_key:s} start {self.child_constants.pattern:s}")
        for awp in article_with_prices_table.get(self.child_constants.pattern):
            if awp:
                show(f"  article.code {awp.article.code:s}")
                child_table.insert(awp)                
            else:
                show(f"awp is none")
        show(f"{self.child_constants.store_key:s} stop")                        
       
    def get_content(self) -> List[DeltaArticleWithPrices]:
        def get_delta(key: str) -> Optional[DeltaArticleWithPrices]:
            bravo_awp = self.bravo_table.article_with_prices.get(key, None)
            alpha_awp = self.alpha_table.article_with_prices.get(key, None)
            now_awp = self.now_table.article_with_prices.get(key, None)
            try:
                dawp = DeltaArticleWithPrices(bravo_awp, alpha_awp, now_awp)
            except Exception as panic:
                show(f"{key:s} error: {str(panic):s}")
                dawp = None
            return dawp

        all_the_keys = (
            self.bravo_table.article_with_prices.keys()
            | self.alpha_table.article_with_prices.keys()
            | self.now_table.article_with_prices.keys()
        )

        deltas = [get_delta(key) for key in all_the_keys]
        return [dd for dd in deltas if dd]

    def write(self) -> str:
        template = Template(HTML_CHILD)
        return template.render(
            title=self.child_constants.pattern,
            local_style="",
            attributes=DeltaChild.ATTRIBUTES,
            content=self.get_content(),
            header=self.index_constants.header,
            pos_label=self.root_constants.pos_label,
            bravo_label=self.root_constants.bravo_label,
            alpha_label=self.root_constants.alpha_label,            
            now_label=self.root_constants.now_label,
        )





class DeltaIndex:
    def __init__(
        self,
        root_constants: DeltaRootConstants,
        bravo_place: str,
        alpha_place: str,
        now_place: str
    ) -> None:
        self._root_constants = root_constants
        self._index_constants = build_DeltaIndexConstants(
            root_constants.delta_key, 
            bravo_place, 
            alpha_place, 
            now_place, 
            root_constants.now_label)
        self._content: List[DeltaChild] = []

    @property
    def root_constants(self) -> DeltaRootConstants:
        return self._root_constants
        
    @property
    def index_constants(self) -> DeltaIndexConstants:
        return self._index_constants
        
    @property
    def content(self) -> List[DeltaChild]:
        return self._content

    def add(self, pattern: str) -> DeltaChild:
        child = DeltaChild(
            pattern,
            len(self.content),
            self.root_constants,
            self.index_constants
        )
        self.content.append(child)
        return child

    def write(self) -> str:
        template = Template(HTML_INDEX)
        return template.render(
            index_constants=self.index_constants,            
            local_style="",
            content=self.content,
        )


class DeltaRoot:
    def __init__(
        self, 
        bravo_key: str,
        alpha_key: str,
        now_key: str
        ) -> None:
        self._root_constants: DeltaRootConstants = build_DeltaRootConstants(bravo_key, alpha_key, now_key)
        self._cities: List[Tuple[str, str]] = []
        
    @property
    def root_constants(self) -> DeltaRootConstants:
        return self._root_constants
    
    @property
    def cities(self) -> List[Tuple[str, str]]:
        return self._cities

    def write(self) -> str:
        template = Template(HTML_ROOT)
        return template.render(constants=self.root_constants, cities=self.cities)    
