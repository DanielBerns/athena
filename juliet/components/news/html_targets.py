from typing import TextIO, Dict
from components.news.models import News

HEAD = """
<!DOCTYPE html>
<html>
<meta charset="utf-8">
<title>Noticias</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
<body>
<div class="w3-container w3-pale-blue">
<h1>Filtrado de noticias</h1>

<div class="w3-panel w3-border-top w3-border-blue">
<p>Escriba un texto en la barra de búsqueda:</p>


<input type="text" id="filterInput" placeholder="texto...">
<button id="filterButton">Filtrar</button>


</div>

<ul id="search" class="w3-ul w3-pale-green">
"""

TAIL = """
</ul>
</div>
  <script>
    const searchList = document.getElementById('search');
    const filterInput = document.getElementById('filterInput');
    const filterButton = document.getElementById('filterButton');

    filterButton.addEventListener('click', () => {
      const filterPattern = filterInput.value.toLowerCase(); // Get and convert filter text to lowercase
      const listItems = searchList.querySelectorAll('li');

      for (const item of listItems) {
        const itemText = item.textContent.toLowerCase(); // Get and convert item text to lowercase
        const isMatch = itemText.includes(filterPattern); // Check if item text includes the pattern

        item.style.display = isMatch ? 'block' : 'none'; // Show/hide based on match
      }
    });
  </script>
</body>
</html>
"""

class HTMLTarget:
    def __init__(self, target: TextIO) -> None:
        self._target: TextIO = target

    @property
    def head(self) -> str:
        return HEAD

    @property
    def tail(self) -> str:
        return TAIL
    
    def start(self) -> None:
        self._target.write(self.head)
    
    def add(self, news: News) -> None:
        self._target.write('<li class="w3-border-top w3-border-blue">\n')
        self._target.write(f"{news.as_html:s}\n")
        self._target.write("</li>\n")    

    def stop(self) -> None:
        self._target.write(self.tail)
    
