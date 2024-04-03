from pathlib import Path
from typing import Tuple, List
from components.core import Application, show, TreeStore, open_scraper
from components.helpers import get_container
from components.news.io import IO

class Actions:
    @staticmethod
    def start(
        application: Application
    ) -> Tuple[Path, Path, Path]:
        name = "news"
        storage: Path = get_container(application.file_system.storage, name)
        results: Path = get_container(application.file_system.results, name)
        reports: Path = get_container(application.file_system.reports, name)
        return storage, results, reports
    
    @staticmethod
    def create_sample(
        application: Application,
        resources: List[Tuple[str, str, str, str]]
    ) -> Path:
        show(f"Actions.create_sample() 1")
        (   storage_news,
            results_news,
            reports_news,
        ) = Actions.start(application)
        store = TreeStore(storage_news, "treestore")
        store.start()
        sample_home = store.create_sample_home()
        with open_scraper() as scraper:
            for identifier, url, name, suffix in resources:
                container = get_container(sample_home, identifier)
                content, attributes = scraper.get(url)
                IO.write(container, name, suffix, content, attributes)
        store.stop()
        show(f"Actions.create_sample() 2")
        return sample_home
