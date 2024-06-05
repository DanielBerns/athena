from dataclasses import asdict
from pathlib import Path
from typing import Callable, Dict, Tuple, Generator
from components.core import Application, FlatStore, show
from components.helpers import get_container
from components.precios_claros.io import IO, Sample
from components.precios_claros.models import ArticleWithPricesTable
from components.precios_claros.buckets import Bucket
from components.precios_claros.precios_claros import PreciosClaros

# import pdb

class Editor:

    @staticmethod
    def execute(application: Application) -> None:
        try:
            articles_bucket = Bucket()
            points_of_sale_bucket = Bucket()
            errors_bucket = Bucket()
            precios_claros = PreciosClaros(
                application.file_system.storage,
                application.file_system.results,
                application.file_system.reports,
                articles_bucket,
                points_of_sale_bucket,
                errors_bucket
            )
            precios_claros.load_record_rules()
            precios_claros.write_clean_records()                                
        except Exception as panic:
            explanation = str(panic)
            show(explanation)
            event = {
                'explanation': explanation
            }
