from components.precios_claros.models import (
    PointOfSale,
    Article,
    ArticleWithPrices,
    PointsOfSaleTable,
    ArticleWithPricesTable,
)
from components.precios_claros.web_scraper import WebScraper
from components.precios_claros.io import IO
from components.precios_claros.actions import Actions
from components.precios_claros.html import HTML_INDEX, HTML_CHILD
from components.precios_claros.adapters import Index, Child
