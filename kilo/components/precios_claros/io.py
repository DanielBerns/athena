def itera_kilo_points_of_sale(self) -> Generator[Dict[str, str], None, None]:
    logging.info(f"{classname(self):s}.start()")
    for scraped_point_of_sale in self.scraper.itera_points_of_sale():
        kilo_point_of_sale = get_kilo_point_of_sale(scraped_point_of_sale)
        yield kilo_point_of_sale
    logging.info(f"{classname(self):s}.stop()")

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

    def itera_article_per_point_of_sale(self) -> Generator[Dict[str, str], None, None]:
        for pos in self.itera_selected_kilo_points_of_sale():
            for scraped_article_per_point_of_sale in self.scraper.itera_articles_per_point_of_sale(pos.point_of_sale):
                kilo_article_per_point_of_sale = get_kilo_article_per_point_of_sale(scraped_article_per_point_of_sale)
                yield kilo_article_per_point_of_sale

    def start(self) -> None:
        """Placeholder for operations to perform before using the generator."""
        show(f"{classname(self):s}.start")
        self.selected_points_of_sale.start()

    def stop(self) -> None:
        """Placeholder for operations to perform after using the generator."""
        self.selected_points_of_sale.stop()
        show(f"{classname(self):s}.stop")
