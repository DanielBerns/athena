from pathlib import Path
from typing import Tuple, List
from components.core import Application, show, TreeStore, open_scraper, register_error
from components.helpers import get_container, get_resource
from components.news.io import IO
from components.news.news_processors import NewsProcessor
from components.news.html_targets import HTMLTarget
from components.news.news_targets import NewsTarget
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
    def create_store(storage: Path) -> TreeStore:
        return TreeStore(storage, "treestore")
    
    @staticmethod
    def create_sample(
        store: TreeStore,
        resources: List[Tuple[str, str, str, str]]
    ) -> Path:
        show("Actions.create_sample start")        
        store.start()
        sample_home = store.create_sample_home()
        with open_scraper() as scraper:
            show("Actions.create_sample scraper start")        
            for identifier, url, name, suffix in resources:
                show(f"Actions.create_sample {identifier:s}")
                container = get_container(sample_home, identifier)
                content, attributes = scraper.get(url)
                IO.write(container, name, suffix, content, attributes)
            show("Actions.create_sample scraper stop")
        store.stop()
        show("Actions.create_sample stop")
        return sample_home

    @staticmethod
    def store_samples_to_news_target(
        store: TreeStore,
        news_target: NewsTarget,
        processors: List[NewsProcessor]
    ) -> None:
        show("Actions.store_samples_to_news_target start")        
        store.start()
        news_target.start()
        show("Actions.store_samples_to_news_target store.iterate start")                
        for sample_home in store.iterate():
            for this_processor in processors:
                try:
                    container = get_container(sample_home, this_processor.identifier)
                    content, attributes = IO.read(container, this_processor.name, this_processor.suffix)
                    show(f"Actions.store_samples_to_news_target {str(sample_home):s} read")        
                except Exception as panic:
                    register_error(str(panic))
                    show(f"Actions.store_samples_to_news_target {str(sample_home):s} error 1")                            
                else:
                    try:
                        for news in this_processor.execute(content, attributes):
                            news_target.add(news)
                        show(f"Actions.store_samples_to_news_target {str(sample_home):s} done")                            
                    except Exception as panic:
                        register_error(str(panic))
                        show(f"Actions.store_samples_to_news_target {str(sample_home):s} error 2")
        show("Actions.store_samples_to_news_target store.iterate stop")                
        news_target.stop()
        store.stop()
        show("Actions.store_samples_to_news_target stop")
