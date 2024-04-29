import logging
from pathlib import Path

from typing import Dict, Generator, Protocol, Tuple, DefaultDict, List, Callable
from collections import Counter, defaultdict

from components.helpers import get_container, i, classname
from components.core import MessageDocument, MessageGenerator, open_webclient, show, FlatStore
from components.precios_claros.models import (
    Article,
    PointOfSale,
    ArticleWithPricesTable,
    PointsOfSaleTable,
)
from components.precios_claros import WebScraper


class PreciosClarosError(Exception):
    def __init__(self, explanation: str) -> None:
        logging.error(explanation)
        super().__init__(explanation)


class Scraper(Protocol):
    def start(self) -> None:
        ...

    def stop(self) -> None:
        ...

    def points_of_sale(self) -> Generator[Dict[str, str], None, None]:
        ...

    def articles_per_point_of_sale(
        self, point_of_sale: Dict[str, str]
    ) -> Generator[Dict[str, str], None, None]:
        ...


class Sample:
    def __init__(self, container: Path) -> None:
        self._key: str = container.stem
        self._points_of_sale = MessageDocument(
            get_container(container, "points_of_sale")
        )
        self._selected_points_of_sale = MessageDocument(
            get_container(container, "selected_points_of_sale")
        )
        self._articles_per_point_of_sale = MessageDocument(
            get_container(container, "articles_per_point_of_sale")
        )

    @property
    def key(self) -> str:
        return self._key

    @property
    def points_of_sale(self) -> MessageDocument:
        return self._points_of_sale

    @property
    def selected_points_of_sale(self) -> MessageDocument:
        return self._selected_points_of_sale

    @property
    def articles_per_point_of_sale(self) -> MessageDocument:
        return self._articles_per_point_of_sale

    def start(self) -> None:
        self.points_of_sale.start()
        self.selected_points_of_sale.start()
        self.articles_per_point_of_sale.start()

    def stop(self) -> None:
        self.points_of_sale.stop()
        self.selected_points_of_sale.stop()
        self.articles_per_point_of_sale.stop()


class PointsOfSaleGenerator:
    def __init__(self, scraper: Scraper) -> None:
        self._scraper: Scraper = scraper

    @property
    def scraper(self) -> Scraper:
        return self._scraper

    def messages(self) -> Generator[Dict[str, str], None, None]:
        """A message is dictionary with str keys and str values."""
        for message in self.scraper.points_of_sale():
            processed_message = {
                "identifier": message["id"],
                "provincia": (message["provincia"]).lower(),
                "localidad": (message["localidad"]).lower(),
                "direccion": (message["direccion"]).lower(),
                "bandera": (message["banderaDescripcion"]).lower(),
                "comercio": (message["comercioRazonSocial"]).lower(),
                "sucursal": (message["sucursalNombre"]).lower(),
            }
            yield processed_message

    def start(self) -> None:
        """Placeholder for operations to perform before using the generator."""
        show(f"{classname(self):s}.start()")

    def stop(self) -> None:
        """Placeholder for operations to perform after using the generator."""
        show(f"{classname(self):s}.stop()")


class PointsOfSaleReader:
    def __init__(self) -> None:
        self._table = PointsOfSaleTable()

    @property
    def table(self) -> PointsOfSaleTable:
        return self._table

    def get(self, message: Dict[str, str]) -> Tuple[str, str, str, str, str]:
        identifier = message["identifier"]
        name = (message["bandera"]).lower()
        province = (message["provincia"]).lower()
        city = (message["localidad"]).lower()
        address = (message["direccion"]).lower()
        return identifier, name, province, city, address

    def update(self, origin: MessageGenerator) -> None:
        origin.start()
        for message in origin.messages():
            identifier, name, province, city, address = self.get(message)
            point_of_sale = PointOfSale(identifier, name, province, city, address)
            self.table.add(point_of_sale)
        origin.stop()


class ArticlesGenerator:
    def __init__(
        self, scraper: Scraper, selected_points_of_sale: MessageDocument
    ) -> None:
        self._scraper: Scraper = scraper
        self._selected_points_of_sale = selected_points_of_sale

    @property
    def scraper(self) -> Scraper:
        return self._scraper

    @property
    def selected_points_of_sale(self) -> MessageDocument:
        return self._selected_points_of_sale

    def messages(self) -> Generator[Dict[str, str], None, None]:
        """A message is dictionary with str keys and str values."""
        for pos in self.selected_points_of_sale.messages():
            for message in self.scraper.articles_per_point_of_sale(pos):
                processed_message = {
                    "identifier": message["id"],
                    "marca": (message["marca"]).lower(),
                    "nombre": (message["nombre"]).lower(),
                    "presentacion": (message["presentacion"]).lower(),
                    "precio": message["precio"],
                    "precio_min": message["precioMin"],
                    "precio_max": message["precioMax"],
                    "point_of_sale": message["point_of_sale"],
                }
                yield processed_message

    def start(self) -> None:
        """Placeholder for operations to perform before using the generator."""
        show(f"{classname(self):s}.start")
        self.selected_points_of_sale.start()

    def stop(self) -> None:
        """Placeholder for operations to perform after using the generator."""
        self.selected_points_of_sale.stop()
        show(f"{classname(self):s}.stop")


class ArticlesReader:
    def __init__(self, points_of_sale_table: PointsOfSaleTable) -> None:
        self._points_of_sale_table: PointsOfSaleTable = points_of_sale_table
        self._articles_counter: Counter = Counter()
        self._articles: Dict[str, Article] = {}
        self._prices: DefaultDict[str, List[Tuple[PointOfSale, int]]] = defaultdict(
            list
        )

    @property
    def points_of_sale_table(self) -> PointsOfSaleTable:
        return self._points_of_sale_table

    @property
    def articles_counter(self) -> Counter:
        return self._articles_counter

    @property
    def articles(self) -> Dict[str, Article]:
        return self._articles

    @property
    def prices(self) -> DefaultDict[str, List[Tuple[PointOfSale, int]]]:
        return self._prices

    def get(
        self, message: Dict[str, str]
    ) -> Tuple[str, str, str, str, int, PointOfSale]:
        article_code = message["identifier"]
        brand = (message["marca"]).lower()
        name = (message["nombre"]).lower()
        package = (message["presentacion"]).lower()
        _price = message["precio"]
        point_of_sale_identifier = message["point_of_sale"]

        try:
            price = int(float(_price) * 100)
        except ValueError:
            explanation = f"{classname(self):s}.get 1"
            register_error(explanation)
            raise PreciosClarosError(explanation)

        try:
            point_of_sale = self.points_of_sale_table.per_identifier[
                point_of_sale_identifier
            ]
        except KeyError:
            explanation = f"{classname(self):s}.get 2"
            register_error(explanation)
            raise PreciosClarosError(explanation)

        return article_code, brand, name, package, price, point_of_sale

    def update(self, origin: MessageGenerator) -> None:
        origin.start()
        for message in origin.messages():
            article_code, brand, name, package, price, point_of_sale = self.get(message)
            self.articles_counter[article_code] += 1
            if self.articles_counter[article_code] == 1:
                an_article = Article(article_code, brand, name, package)
                self.articles[article_code] = an_article
            else:
                an_article = self.articles[article_code]
                different_articles = any(
                    (
                        brand != an_article.brand,
                        name != an_article.name,
                        package != an_article.package,
                    )
                )
                if different_articles:
                    explanation = f"{classname(self):s}.update 1"
                    register_error(explanation)
                    raise PreciosClarosError(explanation)
            self.prices[article_code].append((point_of_sale, price))
        origin.stop()


class PointsOfSaleSelector:
    def __init__(
        self, points_of_sale: MessageDocument, select: Callable[[Dict[str, str]], bool]
    ):
        self._points_of_sale: MessageDocument = points_of_sale
        self._select: Callable[[Dict[str, str]], bool] = select

    def messages(self) -> Generator[Dict[str, str], None, None]:
        for message in self._points_of_sale.messages():
            if self._select(message):
                yield message

    def start(self) -> None:
        """Placeholder for operations to perform before using the generator."""
        pass

    def stop(self) -> None:
        """Placeholder for operations to perform after using the generator."""
        pass


class IOException(Exception):
    pass


class IO:
    # @staticmethod
    # def build(sample_home: Path) -> Sample:
    #     return Sample(sample_home)

    @staticmethod
    def write(sample: Sample, select: Callable[[Dict[str, str]], bool]) -> None:
        with open_webclient() as webclient:
            sample.start()
            web_scraper = WebScraper(webclient)
            web_scraper.start()
            posg = PointsOfSaleGenerator(web_scraper)
            sample.points_of_sale.update(posg)
            sposg = PointsOfSaleSelector(sample.points_of_sale, select)
            sample.selected_points_of_sale.update(sposg)
            aposg = ArticlesGenerator(web_scraper, sample.selected_points_of_sale)
            sample.articles_per_point_of_sale.update(aposg)
            web_scraper.stop()
            sample.stop()

    @staticmethod
    def get_article_with_prices_table(
        sample: Sample,
        place: str,
        points_of_sale: List[PointOfSale],
        articles_reader: ArticlesReader,
    ) -> ArticleWithPricesTable:
        article_with_prices_table = ArticleWithPricesTable()
        for article_code, prices_per_point_of_sale in articles_reader.prices.items():
            try:
                points_of_sale_with_prices = [
                    (a_point_of_sale, price)
                    for a_point_of_sale, price in prices_per_point_of_sale
                    if a_point_of_sale in points_of_sale
                ]
                if points_of_sale_with_prices:
                    article = articles_reader.articles[article_code]
                    article_with_prices_table.create(
                        article, points_of_sale_with_prices
                    )
            except KeyError:
                explanation = f"IO.get_article_with_prices_table: bad article_code {article_code:s}"
                register_error(explanation)
                raise PreciosClarosError(explanation)
        return article_with_prices_table

    @staticmethod
    def get_points_of_sale_table(sample: Sample) -> PointsOfSaleTable:
        points_of_sale_reader = PointsOfSaleReader()
        points_of_sale_reader.update(sample.selected_points_of_sale)
        return points_of_sale_reader.table

    @staticmethod
    def read(
        sample: Sample
    ) -> Tuple[PointsOfSaleTable, ArticlesReader]:
        points_of_sale_table = IO.get_points_of_sale_table(sample)
        articles_reader = ArticlesReader(points_of_sale_table)
        articles_reader.update(sample.articles_per_point_of_sale)
        show(
            f"    {sample.key:s} points_of_sale.per_place     : {len(points_of_sale_table.per_place):d}"
        )
        show(
            f"    {sample.key:s} points_of_sale.per_identifier: {len(points_of_sale_table.per_identifier):d}"
        )
        show(
            f"    {sample.key:s} articles                     : {len(articles_reader.articles_counter):d}"
        )
        
        return points_of_sale_table, articles_reader

    @staticmethod
    def iterate(
        sample: Sample,
        points_of_sale_table: PointsOfSaleTable,
        articles_reader: ArticlesReader,
    ) -> Generator[Tuple[str, ArticleWithPricesTable, List[PointOfSale]], None, None]:
        for place, points_of_sale in points_of_sale_table.per_place.items():
            article_with_prices_table = IO.get_article_with_prices_table(
                sample, place, points_of_sale, articles_reader
            )
            yield place, article_with_prices_table, points_of_sale

    @staticmethod
    def retrieve(
        reference_place: str,
        current_sample: Sample,
        current_points_of_sale_table: PointsOfSaleTable,
        current_articles_reader: ArticlesReader,
    ) -> Tuple[str, ArticleWithPricesTable, List[PointOfSale]]:
        try:
            points_of_sale = current_points_of_sale_table.per_place[reference_place]
            article_with_prices_table = IO.get_article_with_prices_table(
                current_sample, reference_place, points_of_sale, current_articles_reader
            )
        except KeyError:
            explanation = f"IO.retrieve: bad reference_place {reference_place:s}"
            register_error(explanation)
            raise PreciosClarosError(explanation)
        # If we reach this point, reference_place == current_place
        return reference_place, article_with_prices_table, points_of_sale
