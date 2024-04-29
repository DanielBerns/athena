from dataclasses import asdict
from pathlib import Path
from typing import Callable, Dict, Tuple
from components.core import Application, FlatStore, show
from components.helpers import get_container
from components.precios_claros.io import IO, Sample
from components.precios_claros.models import ArticleWithPricesTable
from components.precios_claros.collectors import Collector

# import pdb


class Analyzer:

    @staticmethod
    def execute(application: Application) -> None:
        precios_claros = PreciosClaros(
            application.file_system.storage,
            application.file_system.results,
            application.file_system.reports
        )
        store = FlatStore(precios_claros.storage, "flatstore")
        store.start()
        for sample_key in store.sorted_sample_keys():
            show(f"{str(sample_key):s}")
            try:
                sample_home = store.sample_home(sample_key)
                precios_claros.analyze(sample_home)
            except Exception as panic:
                explanation = str(panic)
                show(explanation)
                event = {
                    'sample_key': sample_key,
                    'explanation': explanation
                }

        precios_claros.write("")                
   
            
