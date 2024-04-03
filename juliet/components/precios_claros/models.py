from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import logging
from typing import Tuple, List, Set, Protocol, Dict, Generator, DefaultDict, Optional
from math import log

from components.helpers import classname, get_container, get_resource
from components.core import show


@dataclass
class PointOfSale:
    identifier: str
    name: str
    province: str
    city: str
    address: str

    def place(self) -> str:
        return f"{self.province:s}:{self.city:s}"


class SelectPointOfSale(Protocol):
    def select(self, point_of_sale: PointOfSale) -> bool:
        ...


class SelectPointOfSaleProvince:
    def __init__(self, province: str) -> None:
        self._province: str = province

    def select(self, point_of_sale: PointOfSale) -> bool:
        return point_of_sale.province == self._province


class SelectPointOfSaleProvinceAndCity:
    def __init__(self, province: str, city: str) -> None:
        self._province: str = province
        self._city: str = city

    def select(self, point_of_sale: PointOfSale) -> bool:
        return (
            point_of_sale.city == self._city
            and point_of_sale.province == self._province
        )


def get_place_keys(place: str) -> Tuple[str, str]:
    parts = place.split(":")
    province_key = parts[0]
    city_key = parts[1].replace(" ", "_")
    return province_key, city_key


@dataclass
class Article:
    code: str
    brand: str
    name: str
    package: str


PointOfSaleAndPrice = Tuple[PointOfSale, int]


class ModelsException(Exception):
    def __init__(self, remark: str) -> None:
        logging.error(remark)
        super().__init__(remark)


class PointsOfSaleTable:
    def __init__(self) -> None:
        self._per_place: DefaultDict[str, List[PointOfSale]] = defaultdict(list)
        self._per_identifier: Dict[str, PointOfSale] = dict()

    @property
    def per_place(self) -> DefaultDict[str, List[PointOfSale]]:
        return self._per_place

    @property
    def per_identifier(self) -> Dict[str, PointOfSale]:
        return self._per_identifier

    def add(self, point_of_sale: PointOfSale) -> None:
        self.per_place[point_of_sale.place()].append(point_of_sale)
        self.per_identifier[point_of_sale.identifier] = point_of_sale

    def place_and_points_of_sale(
        self,
    ) -> Generator[Tuple[str, List[PointOfSale]], None, None]:
        for place, points_of_sale in self.per_place.items():
            yield place, points_of_sale

    def point_of_sale(self) -> Generator[PointOfSale, None, None]:
        for point_of_sale in self.per_identifier.values():
            yield point_of_sale


def f2i(f: float) -> int:
    return int(f * 100)


def i2f(i: int) -> float:
    return i / 100


def get_place_key(place: str) -> str:
    return place.replace("-", "_").replace(":", "_").replace(" ", "_")


def get_price_descriptors(prices: List[PointOfSaleAndPrice]) -> Tuple[int, int, int]:
    if len(prices) == 0:
        remark = "get_price_descriptors 1: len(prices) == 0"
        raise ModelsException(remark)
    ordered_prices = sorted(prices, key=lambda x: x[1])
    try:
        int_prices = [price for point_of_sale, price in ordered_prices]
    except ValueError:
        remark = "get_price_descriptors 2: bad prices"
        raise ModelsException(remark)
    else:
        prices_min, prices_max = int_prices[0], int_prices[-1]
        if prices_min == prices_max:
            prices_geomean = prices_min / 100
        else:
            log_float_prices = [log(pp, 10) for pp in int_prices]
            log_prices_geomean = sum(log_float_prices) / len(log_float_prices) - 2
            prices_geomean = 10**log_prices_geomean
        return prices_min, f2i(prices_geomean), prices_max


# @dataclass
# class LabelAndValue:
#     label: str
#     value: str


def format_price(price: int) -> str:
    formatted: str = f"${i2f(price):,.2f}"
    return f"{formatted:>14s}"


class ArticleWithPrices:
    def __init__(
        self, article: Article, prices_per_point_of_sale: List[PointOfSaleAndPrice]
    ) -> None:
        self._article: Article = article
        self._prices_per_point_of_sale: List[
            PointOfSaleAndPrice
        ] = prices_per_point_of_sale
        prices_min, prices_geomean, prices_max = get_price_descriptors(
            self.prices_per_point_of_sale
        )
        self._prices_min: str = format_price(prices_min)
        self._prices_geomean: str = format_price(prices_geomean)
        self._prices_max: str = format_price(prices_max)

    @property
    def article(self) -> Article:
        return self._article

    @property
    def prices_per_point_of_sale(self) -> List[PointOfSaleAndPrice]:
        return self._prices_per_point_of_sale

    @property
    def formatted_prices_per_point_of_sale(self) -> Dict[str, str]:
        def get_label_and_value(
            point_of_sale: PointOfSale, price: int
        ) -> Tuple[str, str]:
            # label = (f"{point_of_sale.identifier:<15s} - {point_of_sale.name:>40s}"
            #          f"{point_of_sale.address:>30s}"
            #         )
            label = f"{point_of_sale.name:>40s} - {point_of_sale.address:>30s}"
            value = format_price(price)
            return label, value

        sorted_pps = sorted(self.prices_per_point_of_sale, key=lambda x: x[1])
        entries = (
            get_label_and_value(point_of_sale, price)
            for (point_of_sale, price) in sorted_pps
        )
        result: Dict[str, str] = dict(entries)
        return result

    @property
    def name_and_brand(self) -> str:
        return f"{self.article.name:<30s} - {self.article.brand:<15s}"

    @property
    def code(self) -> str:
        return f"{self.article.code:<15s}"

    @property
    def prices_min(self) -> str:
        return self._prices_min

    @property
    def prices_geomean(self) -> str:
        return self._prices_geomean

    @property
    def prices_max(self) -> str:
        return self._prices_max


def match(value: str, pattern: str) -> bool:
    if len(pattern) == 0:
        return False
    if len(value) < len(pattern):
        return False
    return all(a == b for a, b in zip(value, pattern))


class ModelsError(Exception):
    pass


class DeltaArticleWithPrices:
    def __init__(
        self,
        bravo_awp: Optional[ArticleWithPrices],
        alpha_awp: Optional[ArticleWithPrices],
        now_awp: Optional[ArticleWithPrices],
    ) -> None:
        code: str
        name_and_brand: str
        bravo_stats: Tuple[str, str, str]
        bravo_attributes: Tuple[int, int, int]
        bravo_prices_per_pos: Dict[str, str]
        alpha_stats: Tuple[str, str, str]
        alpha_attributes: Tuple[int, int, int]
        now_stats: Tuple[str, str, str]
        now_attributes: Tuple[int, int, int]
        now_prices_per_pos: Dict[str, str]

        now_bit: int = 0
        bravo_bit: int = 0
        alpha_bit: int = 0

        now_attributes = (0, 0, 0)
        alpha_attributes = (0, 0, 0)
        bravo_attributes = (0, 0, 0)

        if now_awp:
            now_bit = 1
            code = now_awp.code
            name_and_brand = now_awp.name_and_brand
            now_stats = (now_awp.prices_min, now_awp.prices_geomean, now_awp.prices_max)
            now_prices_per_pos = now_awp.formatted_prices_per_point_of_sale
        else:
            code = "&nbsp;"
            name_and_brand = "&nbsp;"
            now_stats = ("&nbsp;", "&nbsp;", "&nbsp;")
            now_prices_per_pos = {}

        if alpha_awp:
            alpha_bit = 1
            code = alpha_awp.code
            name_and_brand = alpha_awp.name_and_brand
            alpha_stats = (
                alpha_awp.prices_min,
                alpha_awp.prices_geomean,
                alpha_awp.prices_max,
            )
            alpha_prices_per_pos = alpha_awp.formatted_prices_per_point_of_sale

        if now_bit:
                now_attributes = (
                    2 if now_awp.prices_min > alpha_awp.prices_min else 1,
                    2 if now_awp.prices_geomean > alpha_awp.prices_geomean else 1,
                    2 if now_awp.prices_max > alpha_awp.prices_max else 1
                )
        else:
            alpha_stats = ("&nbsp;", "&nbsp;", "&nbsp;")
            alpha_prices_per_pos = {}

        if bravo_awp:
            bravo_bit = 1
            code = bravo_awp.code
            name_and_brand = bravo_awp.name_and_brand
            bravo_stats = (
                bravo_awp.prices_min,
                bravo_awp.prices_geomean,
                bravo_awp.prices_max,
            )
            bravo_prices_per_pos = bravo_awp.formatted_prices_per_point_of_sale
            if alpha_bit:
                alpha_attributes = (
                    2 if alpha_awp.prices_min > bravo_awp.prices_min else 1,
                    2 if alpha_awp.prices_geomean > bravo_awp.prices_geomean else 1,
                    2 if alpha_awp.prices_max > bravo_awp.prices_max else 1
                )
            elif now_bit:
                now_attributes = (
                    2 if now_awp.prices_min > bravo_awp.prices_min else 1,
                    2 if now_awp.prices_geomean > bravo_awp.prices_geomean else 1,
                    2 if now_awp.prices_max > bravo_awp.prices_max else 1
                )
        else:
            bravo_stats = ("&nbsp;", "&nbsp;", "&nbsp;")
            bravo_prices_per_pos = {}

        check: bool = ((now_bit * 2 + bravo_bit) * 2 + alpha_bit) != 0
        if check == 0:
            remark = f"{classname(self):s}.__init__: {check} - {now_bit:d} {bravo_bit:d} {alpha_bit:d}"
            show(remark)
            # raise ModelsError(remark)
        self._check: bool = check
        self._bravo_awp: Optional[ArticleWithPrices] = bravo_awp
        self._alpha_awp: Optional[ArticleWithPrices] = alpha_awp
        self._now_awp: Optional[ArticleWithPrices] = now_awp
        self._code: str = code
        self._name_and_brand: str = name_and_brand
        self._bravo_values: List[Tuple[str, int]] = [
            (ss, aa) for ss, aa in zip(bravo_stats, bravo_attributes)
        ]
        self._alpha_values: List[Tuple[str, int]] = [
            (ss, aa) for ss, aa in zip(alpha_stats, alpha_attributes)
        ]
        self._now_values: List[Tuple[str, int]] = [
            (ss, aa) for ss, aa in zip(now_stats, now_attributes)
        ]
        self._bravo_prices_per_pos: Dict[str, str] = bravo_prices_per_pos
        self._alpha_prices_per_pos: Dict[str, str] = alpha_prices_per_pos
        self._now_prices_per_pos: Dict[str, str] = now_prices_per_pos
        self._list_of_pos: Set[str] = (
            bravo_prices_per_pos.keys()
            | alpha_prices_per_pos.keys()
            | now_prices_per_pos.keys()
        )

    @property
    def check(self) -> bool:
        return self._check

    @property
    def now_awp(self) -> Optional[ArticleWithPrices]:
        return self._now_awp

    @property
    def bravo_awp(self) -> Optional[ArticleWithPrices]:
        return self._bravo_awp

    @property
    def alpha_awp(self) -> Optional[ArticleWithPrices]:
        return self._alpha_awp

    @property
    def code(self) -> str:
        return self._code

    @property
    def name_and_brand(self) -> str:
        return self._name_and_brand

    @property
    def now_values(self) -> List[Tuple[str, int]]:
        return self._now_values

    @property
    def bravo_values(self) -> List[Tuple[str, int]]:
        return self._bravo_values

    @property
    def alpha_values(self) -> List[Tuple[str, int]]:
        return self._alpha_values

    @property
    def now_prices_per_pos(self) -> Dict[str, str]:
        return self._now_prices_per_pos

    @property
    def bravo_prices_per_pos(self) -> Dict[str, str]:
        return self._bravo_prices_per_pos

    @property
    def alpha_prices_per_pos(self) -> Dict[str, str]:
        return self._alpha_prices_per_pos

    @property
    def list_of_pos(self) -> Set[str]:
        return self._list_of_pos


class ArticleWithPricesTable:
    def __init__(self) -> None:
        self._article_with_prices: Dict[str, ArticleWithPrices] = dict()

    @property
    def article_with_prices(self) -> Dict[str, ArticleWithPrices]:
        return self._article_with_prices

    def create(
        self, article: Article, prices_per_point_of_sale: List[PointOfSaleAndPrice]
    ) -> None:
        self.article_with_prices[article.code] = ArticleWithPrices(
            article, prices_per_point_of_sale
        )

    def insert(self, article_with_prices: ArticleWithPrices) -> None:
        self.article_with_prices[article_with_prices.article.code] = article_with_prices

    def select_values_by_article_code(
        self, article_codes: List[str]
    ) -> Generator[ArticleWithPrices, None, None]:
        for this_article_code in article_codes:
            try:
                yield self.article_with_prices[this_article_code]
            except KeyError:
                continue

    def select_values_by_prefix(
        self, prefixes: List[str]
    ) -> Generator[ArticleWithPrices, None, None]:
        for this_prefix in prefixes:
            for article_code, article_with_prices in self.article_with_prices.items():
                if article_with_prices.article.name.startswith(this_prefix):
                    yield article_with_prices

    def values(self) -> Generator[ArticleWithPrices, None, None]:
        for article_code, article_with_prices in self.article_with_prices.items():
            yield article_with_prices

    def article_names(self) -> Generator[str, None, None]:
        for article_code, article_with_prices in self.article_with_prices.items():
            yield article_with_prices.article.name

    def get(self, pattern: str) -> Generator[ArticleWithPrices, None, None]:
        for article_with_prices in self.article_with_prices.values():
            name = article_with_prices.article.name
            if match(name, pattern):
                yield article_with_prices
