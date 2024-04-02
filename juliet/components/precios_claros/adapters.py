from pathlib import Path
from jinja2 import Template
from typing import Tuple, List, Dict
from components.helpers import classname
from components.core.application import show
from components.precios_claros.models import (
    PointOfSale,
    ArticleWithPricesTable,
    ArticleWithPrices,
    PointsOfSaleTable,
    DeltaArticleWithPrices,
)

import pdb


class DeltaChild:
    ATTRIBUTES = ("w3-pale-blue", "w3-pale-green", "w3-pale-red")
    
    def __init__(
        self,
        pattern: str,
        number: int,
        header: str,
        pos_label: str,
        now_label: str,
        alpha_label: str,
        bravo_label: str,
    ) -> None:
        self._pattern: str = pattern
        self._header: str = header
        self._pos_label: str = pos_label
        self._now_label: str = now_label
        self._alpha_label: str = alpha_label
        self._bravo_label: str = bravo_label
        self._now_table: ArticleWithPricesTable = ArticleWithPricesTable()
        self._alpha_table: ArticleWithPricesTable = ArticleWithPricesTable()
        self._bravo_table: ArticleWithPricesTable = ArticleWithPricesTable()

        store_key: str
        name: str

        if len(pattern) == 0 or number < 0:
            store_key = "error"
            name = "empty_child"
            show(
                f"{classname(self):s}.__init__: bad parameters - "
                f"{pattern:s} - {number:d}"
            )
        else:
            store_key = f"{number // 256:03d}"
            name = f"{number:06d}"

        self._url: str = f"/{store_key:s}/{name:s}"
        self._store_key: str = store_key
        self._name: str = name

    @property
    def pattern(self) -> str:
        return self._pattern

    @property
    def store_key(self) -> str:
        return self._store_key

    @property
    def pos_label(self) -> str:
        return self._pos_label

    @pos_label.setter
    def pos_label(self, value: str) -> None:
        self._pos_label = value

    @property
    def now_label(self) -> str:
        return self._now_label

    @now_label.setter
    def now_label(self, value: str) -> None:
        self._now_label = value

    @property
    def alpha_label(self) -> str:
        return self._alpha_label

    @alpha_label.setter
    def alpha_label(self, value: str) -> None:
        self._alpha_label = value

    @property
    def bravo_label(self) -> str:
        return self._bravo_label

    @bravo_label.setter
    def bravo_label(self, value: str) -> None:
        self._bravo_label = value

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
    def now_table(self) -> ArticleWithPricesTable:
        return self._now_table

    @property
    def bravo_table(self) -> ArticleWithPricesTable:
        return self._bravo_table

    @property
    def alpha_table(self) -> ArticleWithPricesTable:
        return self._alpha_table

    def fill_now_table(
        self,
        article_with_prices_table: ArticleWithPricesTable,
        points_of_sale: List[PointOfSale],
    ) -> None:
        for awp in article_with_prices_table.get(self.pattern):
            self.now_table.insert(awp)

    def fill_alpha_table(
        self,
        article_with_prices_table: ArticleWithPricesTable,
        points_of_sale: List[PointOfSale],
    ) -> None:
        for awp in article_with_prices_table.get(self.pattern):
            self.alpha_table.insert(awp)

    def fill_bravo_table(
        self,
        article_with_prices_table: ArticleWithPricesTable,
        points_of_sale: List[PointOfSale],
    ) -> None:
        for awp in article_with_prices_table.get(self.pattern):
            self.bravo_table.insert(awp)

    def get_content(self) -> List[DeltaArticleWithPrices]:
        def get_delta(key: str) -> DeltaArticleWithPrices:
            # pdb.set_trace()
            bravo_awp = self.bravo_table.article_with_prices.get(key, None)
            alpha_awp = self.bravo_table.article_with_prices.get(key, None)
            now_awp = self.now_table.article_with_prices.get(key, None)
            dawp = DeltaArticleWithPrices(bravo_awp, alpha_awp, now_awp)
            if not dawp.check:
                remark = f"dawp.check is False for {key:s}"
                show(remark)
            return dawp

        all_the_keys = (
            self.now_table.article_with_prices.keys()
            | self.bravo_table.article_with_prices.keys()
            | self.alpha_table.article_with_prices.keys()
        )

        return [get_delta(key) for key in all_the_keys]

    def write(self, template_text: str) -> str:
        template = Template(template_text)
        return template.render(
            title=self.pattern,
            local_style="",
            attributes=DeltaChild.ATTRIBUTES,
            content=self.get_content(),
            header=self.header,
            pos_label=self.pos_label,
            now_label=self.now_label,
            alpha_label=self.alpha_label,
            bravo_label=self.bravo_label,
        )


def get_year_month_day(label: str) -> Tuple[str, str, str]:
    year, month, day = label[0:4], label[4:6], label[6:8]
    return year, month, day


def process_label(label: str) -> str:
    year, month, day = get_year_month_day(label)
    return f"{year:s}/{month:s}/{day:s}"


def get_header(label: str, province: str, city: str) -> str:
    year, month, day = get_year_month_day(label)
    header = str = f"{year:s}/{month:s}/{day:s} en {city:s}, {province:s}"
    return header


class DeltaIndex:
    def __init__(
        self,
        root: str,
        pos_label: str,
        now_label: str,
        alpha_label: str,
        bravo_label: str,
        province: str = "",
        city: str = "",
    ) -> None:
        self._content: List[DeltaChild] = []
        self._root: str = root
        header: str = get_header(now_label, province, city)
        self._index_header: str = header
        self._child_header: str = header
        self._pos_label: str = pos_label
        self._now_label: str = process_label(now_label)
        self._alpha_label: str = process_label(alpha_label)
        self._bravo_label: str = process_label(bravo_label)
        # selectors = {}
        # if province:
        #     selectors['province'] = province
        # if city:
        #     selectors['city'] = city
        # self._selectors = selectors

    @property
    def content(self) -> List[DeltaChild]:
        return self._content

    @property
    def root(self) -> str:
        return self._root

    @property
    def index_header(self) -> str:
        return self._index_header

    @property
    def child_header(self) -> str:
        return self._child_header

    @property
    def pos_label(self) -> str:
        return self._pos_label

    @property
    def now_label(self) -> str:
        return self._now_label

    @property
    def alpha_label(self) -> str:
        return self._alpha_label

    @property
    def bravo_label(self) -> str:
        return self._bravo_label

    # @property
    # def selectors(self) -> str:
    #     return self._selectors

    def add(self, pattern: str) -> DeltaChild:
        child = DeltaChild(
            pattern,
            len(self.content),
            self.child_header,
            self.pos_label,
            self.now_label,
            self.alpha_label,
            self.bravo_label,
        )
        self.content.append(child)
        return child

    def write(self, template_text: str) -> str:
        template = Template(template_text)
        return template.render(
            title=self.index_header,
            local_style="",
            content=self.content,
            root=self.root,
        )
