from dataclasses import asdict

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
                self.cities[code.strip()] = (city_name.strip(), state_name.strip())

    
class PreciosClaros:
    
    def __init__(self, storage: Path, results: Path, reports: Path) -> None:
        self._storage = get_container(storage, "precios_claros")
        self._results = get_container(results, "precios_claros")
        self._reports = get_container(reports, "precios_claros")
        self._articles_editor = RecordEditor()        
        self._articles_collector = Collector()
        self._points_of_sale_editor = RecordEditor()        
        self._points_of_sale_collector = Collector()
        self._errors_collector = Collector()
        self._error_key = 0
        
    def load_record_rules(self):
        self.articles_editor.load_record_rules(self.results, "articles", ".md")  
        self.points_of_sale_editor.load_record_rules(self.results, "points_of_sale", ".md")        
        
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
    def articles_collector(self) -> Collector:
        return self._articles_collector

    @property
    def points_of_sale_editor(self) -> RecordEditor:
        return self._points_of_sale_editor

    @property
    def points_of_sale_collector(self) -> Collector:
        return self._points_of_sale_collector

    @property
    def errors_collector(self) -> Collector:
        return self._errors_collector
    
    @property
    def error_key(self) -> int:
        return self._error_key
    
    @error_key.setter
    def error_key(self, value: int) -> None:
        self._error_key = value

    def report_error(self, explanation: str, sample_home: Path) -> None:
        self.error_key += 1
        show(explanation)
        event = {
            'sample_home': str(sample_home),
            'explanation': explanation
        }
        self.error_collector.insert(str(self.error_key), event)
    
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
                    self.points_of_sale_collector.insert(
                        a_point_of_sale.identifier,
                        asdict(a_point_of_sale)
                    )
                for article_code, article_with_prices in article_with_prices_table.article_with_prices.items():
                    self.articles_collector.insert(
                        article_code, 
                        asdict(article_with_prices.article)
                    )
        except Exception as panic:
            self.report_error(str(panic), sample_home)
        show(f"{str(sample_home):s} end")
        
    def edit(self, sample_key: str) -> None:
        show(f"{str(sample_key):s} start")        
        try:
            for number, article in enumerate(Collector.read_table(self.results, "articles", ".md")):
                self.articles_editor.edit(article['code'], article)
                self.articles_collector.insert(article['code'], article)
                print(number, str(article))
                
            for number, point_of_sale in enumerate(Collector.read_table(self.results, "points_of_sale", ".md")):
                self.points_of_sale_editor.edit(point_of_sale['identifier'], point_of_sale)
                self.points_of_sale_collector.insert(point_of_sale['identifier'], point_of_sale)
                print(number, str(point_of_sale))                
        except Exception as panic:
            self.report_error(str(panic), sample_key)
        show(f"{str(sample_key):s} end")

    def write(self, modifier: str):
        articles_name = f"{modifier:s}articles"
        points_of_sale_name = f"{modifier:s}points_of_sale"
        errors_name = f"{modifier:s}errors"        
        self.articles_collector.write_table(self.results, articles_name, ".md")
        self.articles_collector.write_differences(self.results, articles_name, ".md")
        self.points_of_sale_collector.write_table(self.results, points_of_sale_name, ".md")
        self.points_of_sale_collector.write_differences(self.results, points_of_sale_name, ".md")                    
        self.errors_collector.write_table(self.results, errors_name, ".md")
        self.errors_collector.write_differences(self.results, errors_name, ".md")
