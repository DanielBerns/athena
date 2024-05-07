from typing import TextIO, Dict
from components.news.models import News


class NLPTarget:
    def __init__(self, target: TextIO) -> None:
        self._target: TextIO = target

    def start(self) -> None:
        self._target.write(self.head)
    
    def add(self, news: News) -> None:
        self._target.write('<li class="w3-border-top w3-border-blue">\n')
        self._target.write(f"{news.as_html:s}\n")
        self._target.write("</li>\n")    

    def stop(self) -> None:
        self._target.write(self.tail)
    
