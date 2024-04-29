from pathlib import Path
from typing import Tuple, List
from components.core import Application, show, TreeStore, open_scraper, register_error
from components.helpers import get_container, get_resource
from components.news.io import IO
from components.news.news_processors import NewsProcessor
from components.news.html_targets import HTMLTarget

# import pdb

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

    @staticmethod
    def process(
        application: Application,
        processors: List[NewsProcessor]
    ) -> None:
        show(f"Actions.process_sample() 1")
        (   storage_news,
            results_news,
            reports_news,
        ) = Actions.start(application)
        store = TreeStore(storage_news, "treestore")
        store.start()
        resource = get_resource(reports_news, "news", ".html")
        with open(resource, "w") as target:
            news_html = HTMLTarget(target)
            news_html.start()
            counter = 0
            for sample_home in store.iterate():
                test = (counter % 25) > 1
                counter += 1
                if test:
                    continue
                for a_processor in processors:
                    try:
                        container = get_container(sample_home, a_processor.identifier)
                        content, attributes = IO.read(container, a_processor.name, a_processor.suffix)
                    except Exception as panic:
                        register_error(str(panic))
                    else:
                        try:
                            for news in a_processor.execute(content, attributes):
                                news_html.add(news)
                        except Exception as panic:
                            register_error(str(panic))
            show(f"counter == '{counter:d}'")
            news_html.stop()
        store.stop()
        show(f"Actions.process_sample() 2")
