from dataclasses import asdict
from pathlib import Path
from typing import Dict, Tuple, Optional, Generator
from components.precios_claros.io import IO, Sample
from components.precios_claros.record_editor import RecordEditor
from components.precios_claros.collectors import Collector
from components.precios_claros.tools import Tool
from components.precios_claros.buckets import Bucket
from components.core import show, FlatStore
from components.helpers import get_container, classname


class StatesEditor:
    def __init__(self) -> None:
        self._states: Dict[str, str] = {}
        
    @property
    def states(self) -> Dict[str, str]:
        return self._states

    def load(self, container: Path) -> None:
        resource = get_resource(container, "states", ".md")
        with open(resource, "r") as origin:
            for line in origin:
                code, name = line.split(":")
                self.states[code.strip()] = name.strip()

    
class CitiesEditor:
    def __init__(self) -> None:
        self._cities: Dict[str, Tuple[str, str]] = {}
        
    @property
    def cities(self) -> Dict[str, Tuple[str, str]]:
        return self._cities

    def load(self, container: Path) -> None:
        resource = get_resource(container, "cities", ".md")
        with open(resource, "r") as origin:
            for line in origin:
                key, values = line.split(":")
                city_name, state_name = values.split(",")
                self.cities[key.strip()] = (city_name.strip(), state_name.strip())

    
class PreciosClaros:

    @staticmethod
    def get_containers(
        storage: Path, 
        results: Path, 
        reports: Path
    ) -> None:
        storage_precios_claros = get_container(storage, "precios_claros")
        results_precios_claros = get_container(results, "precios_claros")
        reports_precios_claros = get_container(reports, "precios_claros")
        return storage_precios_claros, results_precios_claros, reports_precios_claros

    def __init__(
        self, 
        storage: Path, 
        results: Path, 
        reports: Path,
        articles_tool: Tool,
        points_of_sale_tool: Tool,
        errors_tool: Tool
    ) -> None:
        _storage, _results, _reports = PreciosClaros.get_containers(storage, results, reports)
        self._storage = _storage
        self._results = _results
        self._reports = _reports
        self._articles_editor = RecordEditor()        
        self._points_of_sale_editor = RecordEditor()        
        self._articles_tool = articles_tool
        self._points_of_sale_tool = points_of_sale_tool
        self._errors_tool = errors_tool
        self._error_key = 0
        
    def load_record_rules(self):
        self.articles_editor.load_record_rules(self.results, "record_rules_articles", ".md")  
        self.points_of_sale_editor.load_record_rules(self.results, "record_rules_points_of_sale", ".md")        
        
    def write_clean_records(self):
        self.articles_editor.write_clean_records(
            self.results, "clean_articles", ".md", 
            ["code", "brand", "name", "package"]
        )  
        self.points_of_sale_editor.write_clean_records(
            self.results, "clean_points_of_sale", ".md", 
            ["identifier", "name", "province", "city", "address"])        
        
    @property
    def storage(self) -> Path:
        return self._storage

    @property
    def results(self) -> Path:
        return self._results

    @property
    def reports(self) -> Path:
        return self._reports

    @property
    def articles_editor(self) -> RecordEditor:
        return self._articles_editor

    @property
    def articles_tool(self) -> Tool:
        return self._articles_tool

    @property
    def points_of_sale_editor(self) -> Tool:
        return self._points_of_sale_editor

    @property
    def points_of_sale_tool(self) -> Tool:
        return self._points_of_sale_tool

    @property
    def errors_tool(self) -> Tool:
        return self._errors_tool
    
    @property
    def error_key(self) -> int:
        return self._error_key
    
    @error_key.setter
    def error_key(self, value: int) -> None:
        self._error_key = value

    def report_error(self, explanation: str, sample_home: Optional[Path] = None) -> None:
        self.error_key += 1
        show(explanation)
        event = {
            'explanation': explanation
        }
        if sample_home:
            event['sample_home'] = str(sample_home)
        self.errors_tool.insert(str(self.error_key), event)
    
    def analyze(self, sample_home: Path) -> None:
        show(f"{str(sample_home):s} start")
        try:
            sample = Sample(sample_home)
            points_of_sale_table, articles_reader = IO.read(sample)
            for place, article_with_prices_table, points_of_sale in IO.iterate(
                sample, points_of_sale_table, articles_reader
            ):
                show(f"  {place:s}")
                for a_point_of_sale in points_of_sale:
                    self.points_of_sale_tool.insert(
                        a_point_of_sale.identifier,
                        asdict(a_point_of_sale)
                    )
                for article_code, article_with_prices in article_with_prices_table.article_with_prices.items():
                    self.articles_tool.insert(
                        article_code, 
                        asdict(article_with_prices.article)
                    )
        except Exception as panic:
            self.report_error(str(panic), sample_home)
        show(f"{str(sample_home):s} end")
        
    def edit(self, sample_home: Path) -> None:
        show(f"{str(sample_home):s} start")
        try:
            sample = Sample(sample_home)
            points_of_sale_table, articles_reader = IO.read(sample)
            for place, article_with_prices_table, points_of_sale in IO.iterate(
                sample, points_of_sale_table, articles_reader
            ):
                show(f"  {place:s}")
                for a_point_of_sale in points_of_sale:
                    key = a_point_of_sale.identifier
                    modified_point_of_sale = self.points_of_sale_editor.edit(key, asdict(a_point_of_sale))
                    self.points_of_sale_tool.insert(key, modified_point_of_sale)

                for article_code, article_with_prices in article_with_prices_table.article_with_prices.items():
                    modified_article = self.articles_editor.edit(article_code, asdict(article_with_prices.article))
                    self.articles_tool.insert(article_code, modified_article)                    
        except Exception as panic:
            self.report_error(str(panic), sample_home)
        show(f"{str(sample_home):s} end")

    def write(self, modifier: str):
        articles_name = f"{modifier:s}articles"
        points_of_sale_name = f"{modifier:s}points_of_sale"
        errors_name = f"{modifier:s}errors"        
        self.articles_tool.write(self.results, articles_name, ".md")
        self.points_of_sale_tool.write(self.results, points_of_sale_name, ".md")
        self.errors_tool.write(self.results, errors_name, ".md")

    @staticmethod
    def iterate(storage: Path) -> Generator[Path, None, None]:
        store = FlatStore(storage, "flatstore")
        store.start()
        for sample_key in store.sorted_sample_keys():
            show(f"{str(sample_key):s}")
            try:
                sample_home = store.sample_home(sample_key)
                yield sample_home
            except Exception as panic:
                explanation = str(panic)
                register_error(explanation)
