import logging
from dataclasses import dataclass, field
from typing import dict, Any, Generator, List

from components.helpers.helpers import classname
from components.core.web_client import WebClient

@dataclass
class QueryLimits:
    total_items: int
    max_queries_per_page: int
    full_pages: int = field(init=False)
    full_page_queries: int = field(init=False)
    last_page_queries: int = field(init=False)

    def __post_init__(self) -> None:
        if self.total_items > 0 and self.max_queries_per_page > 0:
            self.full_pages: int = self.total_items // self.max_queries_per_page
            self.full_page_queries: int = self.max_queries_per_page
            self.last_page_queries: int = self.total_items % self.max_queries_per_page
        else:
            self.full_pages = self.full_page_queries = self.last_page_queries = 0

    def offset(self, page: int) -> int:
        return page * self.full_page_queries


class WebScraperError(Exception):
    pass


class Endpoints:
    def __init__(self) -> None:
        pass

    def home(self) -> str:
        return "https://d3e6htiiul5ek9.cloudfront.net/dev/"

    def build_url(
        self,
        url: str,
        offset: int,
        queries: int
    ) -> str:
        return f"{url:s}?offset={offset:d}&limit={queries:d}"

    def points_of_sale(self) -> str:
        return f"{self.home:s}sucursales"

    def points_of_sale_first_query_url(self) -> str:
        return f"{points_of_sale():s}?limit=0"

    def points_of_sale_next_query_url(
        self,
        offset: int,
        queries: int
    ) -> str:
        return self.build_url(self.points_of_sale, offset, queries)

    def articles_per_point_of_sale(
        self,
        point_of_sale: str
    ) -> str:
        return home + "productos?id_sucursal=" + point_of_sale

    def articles_per_point_of_sale_first_query_url(
        self,
        articles_per_point_of_sale: str
    ) -> str:
        return articles_per_point_of_sale + "&limit=0"

    def articles_next_query_url(
        self,
        articles_per_point_of_sale: str,
        offset: int,
        queries: int
        ) -> str: build_url(articles_per_point_of_sale, offset, queries)


class WebScraper:
    def __init__(
        self,
        webclient: WebClient,
        endpoints: Endpoints
    ) -> None:
        self._webclient = webclient
        self._endpoints = endpoints

    @property
    def webclient(self) -> WebClient:
        return self._webclient

    @property
    def endpoints(self) -> Endpoints:
        return self._endpoints

    def start(self) -> None:
        logging.info(f"{classname(self):s}.start()")

    def stop(self) -> None:
        logging.info(f"{classname(self):s}.stop()")

    def get_query_limits(self, url: str) -> QueryLimits:
        response = self.webclient.get(url)
        error_message = response.get("errorMessage", None)
        if error_message:
            explanation = f"{classname(self):s}.get_query_limits({url:s}) error_message 1"
            logging.debug(explanation)
            total_items = max_queries_per_page = 0
        else:
            total_items = response.get("total", 0)
            max_queries_per_page = response.get("maxLimitPermitido", 0)
            if total_items == 0 or max_queries_per_page == 0:
                total_items = max_queries_per_page = 0
        explanation = (
            f"total {str(total_items):s} - "
            f"max_queries_per_page {str(max_queries_per_page):s}"
        )
        logging.info(explanation)
        return QueryLimits(total_items, max_queries_per_page)

    def request_points_of_sale(
        self,
        offset: int,
        queries: int
    ) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self):s}.request_points_of_sale 1")
        url = self.endpoints.points_of_sale_next_query_url(offset, queries)
        logging.info(url)
        response = self.webclient.get(url)
        error_message = response.get("errorMessage", None)
        if error_message:
            explanation = (
                f"{classname(self):s}.request_points_of_sale 2: "
                f"page {str(offset):s} - {str(error_message):s} "
                f"from {str(url):s}."
            )
            logging.warning(explanation)
        else:
            points_of_sale = response.get("sucursales", None)
            if points_of_sale:
                for a_point_of_sale in points_of_sale:
                    yield a_point_of_sale
            else:
                explanation = (
                    f"{classname(self):s}.request_points_of_sale 3: "
                    f"page {offset:d} - {str(error_message):s}"
                )
                logging.warning(explanation)

    def itera_points_of_sale(self) -> Generator[dict[str, str], None, None]:
        logging.info(f"{classname(self):s}.itera_points_of_sale 1")
        url = self.endpoints.points_of_sale_first_query_url()
        query_limits = self.get_query_limits(url)
        if query_limits.total_items == 0:
            explanation = f"{classname(self):s}.itera_points_of_sale 2: zero query_limits"
            logging.error(explanation)
            raise WebScraperError(explanation)
        for page in range(0, query_limits.full_pages):
            for a_point_of_sale in self.request_points_of_sale(
                query_limits.offset(page), query_limits.full_page_queries
            ):
                yield a_point_of_sale
        for a_point_of_sale in self.request_points_of_sale(
            query_limits.offset(query_limits.full_pages),
            query_limits.last_page_queries,
        ):
            yield a_point_of_sale
        logging.info(f"{classname(self):s}.itera_points_of_sale 3: done")

    def request_articles(
        self, articles_url: str, offset: int, queries: int
    ) -> List[dict[str, str]]:
        logging.info(f"{classname(self):s}.get_articles 1: start")
        url = self.endpoints.articles_next_query_url(articles_url, offset, queries)
        response = self.webclient.get(url)
        error_message = response.get("errorMessage", None)
        if error_message:
            explanation = (
                f"{classname(self):s}.get_articles 2: "
                f"page {offset:d} - {str(error_message):s}"
            )
            logging.warning(explanation)
            articles = []
        else:
            logging.info(f"{classname(self):s}.get_articles 3: done")
            articles = response.get("productos", [])
        return articles_list

    def get_articles_per_point_of_sale(
        self, articles_url: str, offset: int, queries: int, point_of_sale_key: str
    ) -> Generator[dict[str, str], None, None]:
        articles = self.request_articles(articles_url, offset, queries)
        if articles:
            for number, an_article in enumerate(articles_list):
                an_article["point_of_sale_key"] = point_of_sale_key
                logging.info(
                    f"{classname(self):s}.articles_per_point_of_sale 3: "
                    f"{point_of_sale_key:s}: {number:d}"
                )
                yield an_article
        else:
            explanation = (
                f"{classname(self):s}.articles_per_point_of_sale 4: "
                f"{point_of_sale_key:s} - empty articles_list"
            )
            logging.warning(explanation)

    def itera_articles_per_point_of_sale(
        self, point_of_sale: dict[str, str]
    ) -> Generator[dict[str, str], None, None]:
        point_of_sale_key = point_of_sale["point_of_sale_key"]
        logging.info(f"{classname(self):s}.itera_articles_per_point_of_sale 1 {point_of_sale_key:s}")
        articles_url = self.endpoints.articles_per_point_of_sale_url(point_of_sale_key)
        first_query_url = self.articles_first_query_url(
            self.endpoints.articles_per_point_of_sale_url(point_of_sale_key)
        )
        query_limits = self.get_query_limits(first_query_url)
        if query_limits.total_items == 0:
            explanation = (
                f"{classname(self):s}.itera_articles_per_point_of_sale 2 "
                f"{point_of_sale_key:s}: zero query_limits"
            )
            logging.error(explanation)
            raise WebScraperError(explanation)
        for page in range(0, query_limits.full_pages):
            for article in self.get_articles_per_point_of_sale(
                articles_url,
                query_limits.offset(page),
                query_limits.full_page_queries,
                point_of_sale_key,
            ):
                yield article
        for article in self.get_articles_per_point_of_sale(
            articles_url,
            query_limits.offset(query_limits.full_pages),
            query_limits.last_page_queries,
            point_of_sale_key,
        ):
            yield article
        logging.info(
            f"{classname(self):s}.itera_per_point_of_sale 3: done {point_of_sale_key:s}"
        )
