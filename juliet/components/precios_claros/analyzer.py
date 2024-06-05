from dataclasses import asdict
from pathlib import Path
from typing import Callable, Dict, Tuple, Generator
from components.core import Application, FlatStore, show
from components.helpers import get_container
from components.precios_claros.io import IO, Sample
from components.precios_claros.models import ArticleWithPricesTable
from components.precios_claros.collectors import Collector
from components.precios_claros.precios_claros import PreciosClaros


class Analyzer:

    @staticmethod
    def execute(application: Application) -> None:
        try:
            articles_collector = Collector()
            points_of_sale_collector = Collector()
            errors_collector = Collector()
            precios_claros = PreciosClaros(
                application.file_system.storage,
                application.file_system.results,
                application.file_system.reports,
                articles_collector,
                points_of_sale_collector,
                errors_collector
            )
            for sample_home in precios_claros.iterate(precios_claros.storage):
                precios_claros.analyze(sample_home)
            precios_claros.write("")                
        except Exception as panic:
                explanation = str(panic)
                show(explanation)
                event = {
                    'sample_home': str(sample_home),
                    'explanation': explanation
                }
   
            
