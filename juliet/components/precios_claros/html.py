from dataclasses import dataclass
from typing import Tuple
from components.core import show, register_error


class HTMLException(Exception):
    pass

@dataclass
class DeltaChildConstants:
    pattern: str
    number: int
    url: str
    store_key: str 
    name: str


def build_DeltaChildConstants(pattern: str, number: int) -> DeltaChildConstants:
    url: str
    store_key: str
    name: str
    if len(pattern) == 0 or number < 0:
        store_key = "error"
        name = "empty_child"
        show(
            f"build_DeltaChildConstants: bad parameters - "
            f"{pattern:s} - {number:d}"
        )
    else:
        store_key = f"{number // 256:03d}"
        name = f"{number:06d}"
    url = f"/{store_key:s}/{name:s}"

    return DeltaChildConstants(pattern, number, url, store_key, name)


def get_year_month_day(source: str) -> Tuple[str, str, str]:
    year, month, day = source[0:4], source[4:6], source[6:8]
    return year, month, day


def get_label(source: str) -> str:
    year, month, day = get_year_month_day(source)
    return f"{year:s}/{month:s}/{day:s}"


@dataclass
class DeltaRootConstants:
    bravo_label: str
    alpha_label: str
    now_label: str
    delta_key: str
    pos_label: str
    
def build_DeltaRootConstants(bravo_key: str, alpha_key: str, now_key: str) -> DeltaRootConstants:
    bravo_prefix = bravo_key[:8]
    alpha_prefix = alpha_key[:8]
    now_prefix = now_key[:8]
    bravo_label = get_label(bravo_prefix)
    alpha_label = get_label(alpha_prefix)
    now_label = get_label(now_prefix)
    delta_key = f"{now_prefix:s}-{alpha_prefix:s}-{bravo_prefix:s}"
    return DeltaRootConstants(bravo_label, alpha_label, now_label, delta_key, "Punto de venta")


@dataclass
class DeltaIndexConstants:
    now_place_key: str
    province: str
    city: str
    root: str
    header: str

  
def build_DeltaIndexConstants(
    delta_key: str,
    bravo_place: str, 
    alpha_place: str, 
    now_place: str,
    now_label: str
) -> DeltaIndexConstants:
    assert(bravo_place == now_place)
    assert(alpha_place == now_place)
    now_place_key = now_place.replace("-", "_").replace(":", "_").replace(" ", "_")
    parts = now_place.split(":")
    if len(parts) != 2:
        explanation = f"build_DeltaIndexConstants: bad place {now_place:s}"
        register_error(explanation)
        raise HTMLException(explanation)
    province=parts[0]
    city=parts[1]
    root = f"/precios_claros/category/{delta_key:s}/{now_place_key:s}"
    header = f"{now_label:s} en {city:s}, {province:s}"
    return DeltaIndexConstants(now_place_key, province, city, root, header)


HTML_INDEX = """
<!DOCTYPE html>
<html lang="es-ar">
<head>
<meta charset="UTF-8">            
    <title>{{index_constants.header}}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="/static/css/w3.css">
    <link rel="stylesheet" href="/static/css/w3-theme-teal.css">
    <link rel="stylesheet" href="/static/css/font-awesome-4.7.0/css/font-awesome.css">   
    <link href="/static/img/favicon.ico" rel="shortcut icon">    
    <script src="/static/js/w3.js"></script>    
    {{ local_style }}
</head>
<body>

<h1 class="w3-center">{{index_constants.header}}</h1>

<div class="w3-row">
<input oninput="w3.filterHTML('#patterns', 'li', this.value)" class="w3-input w3-light-gray" placeholder="Búsqueda de artículos...">
</div>

<div id="patterns" class="w3-container w3-pale-green">

<ul class="w3-ul w3-border w3-hoverable"">
{% for child in content %}
    <li class="w3-pale-blue"><a href="{{index_constants.root}}{{child.child_constants.url}}">{{child.child_constants.pattern}}</a></li>
{% endfor %}
</ul>

</div>

</body></html>"""


HTML_CHILD = """
<!DOCTYPE html>
<html lang="es-ar">
<head>
<meta charset="UTF-8">            
    <title>{{title}}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="/static/css/w3.css">
    <link rel="stylesheet" href="/static/css/w3-theme-teal.css">
    <link rel="stylesheet" href="/static/css/font-awesome-4.7.0/css/font-awesome.css">   
    <script src="/static/js/w3.js"></script>        
    <link href="/static/img/favicon.ico" rel="shortcut icon">    
    {{ local_style }}
</head>
<body>
<h1 class="w3-center">{{ title }}</h1>
<div class="w3-container w3-light-grey">

<article class="w3-row">
<input oninput="w3.filterHTML('#articles', 'article', this.value)" class="w3-input w3-light-gray" placeholder="Búsqueda de artículos...">
</article>

<div id="articles">
{% for dawp in content %}
    <br>
    <article class="w3-row w3-pale-green w3-topbar w3-border-teal">
        <div class="w3-col w3-left-align"><h2>{{ dawp.name_and_brand }}</h2></div>
        <div class="w3-col w3-left-align"><h3>{{ dawp.code }}</h3></div>
        <ul class="w3-ul">
            <li class="w3-container w3-row w3-pale-blue">
              <div class="w3-card-4 w3-topbar w3-border-teal">
                <div class="w3-col m3 l3 w3-left-align w3-sand">Rango de precios</div>
                <div class="w3-col m3 l3 w3-right-align w3-sand">Mínimo</div> 
                <div class="w3-col m3 l3 w3-right-align w3-sand">Indicativo</div> 
                <div class="w3-col m3 l3 w3-right-align w3-sand">Máximo</div>                 
                {% if dawp.now_values %}
                    <div class="w3-col m3 l3 w3-right-align">{{ now_label }}</div>
                    {% for ss, aa in dawp.now_values %}
                        <div class="w3-col m3 l3 w3-right-align {{ attributes[aa] }}">{{ ss }}</div>
                    {% endfor %}
                {% endif %}
                {% if dawp.alpha_values %}
                    <div class="w3-col m3 l3 w3-right-align">{{ alpha_label }}</div>                
                    {% for ss, aa in dawp.alpha_values %}
                        <div class="w3-col m3 l3 w3-right-align {{ attributes[aa] }}">{{ ss }}</div>
                    {% endfor %}
                {% endif %}
                {% if dawp.bravo_values %}
                    <div class="w3-col m3 l3 w3-right-align">{{ bravo_label }}</div>                                
                    {% for ss, aa in dawp.bravo_values %}
                        <div class="w3-col m3 l3 w3-right-align {{ attributes[aa] }}">{{ ss }}</div>
                    {% endfor %}
                {% endif %}
              </div>
              <br>
            </li>
            <li class="w3-container w3-row w3-pale-green"> 
              <div class="w3-card-4 w3-topbar w3-border-teal">
                <div class="w3-col m3 l3 w3-left-align  w3-sand">{{ pos_label }}</div> 
                <div class="w3-col m3 l3 w3-right-align w3-sand">{{ now_label }}</div>
                <div class="w3-col m3 l3 w3-right-align w3-sand">{{ alpha_label }}</div> 
                <div class="w3-col m3 l3 w3-right-align w3-sand">{{ bravo_label }}</div>                 
              </div>
            </li>
            {% for pos in dawp.list_of_pos %}
            <li class="w3-row w3-pale-blue"> 
              <div class="w3-card-4">
                <div class="w3-col m3 l3 w3-left-align">{{pos}}</div> 
                <div class="w3-col m3 l3 w3-right-align">{{dawp.now_prices_per_pos.get(pos, "&nbsp;")}}</div>
                <div class="w3-col m3 l3 w3-right-align">{{dawp.alpha_prices_per_pos.get(pos, "&nbsp;")}}</div> 
                <div class="w3-col m3 l3 w3-right-align">{{dawp.bravo_prices_per_pos.get(pos, "&nbsp;")}}</div>                 
              </div>
            </li>
            {% endfor %}
        </ul>        
        
    </article>
{% endfor %}
</div>

</div>

</body></html>"""


HTML_ROOT = """
<div class="w3-panel w3-pale-green" style="min-height:460px">
  <br>


  <div class="w3-bar-block w3-border w3-light-grey">
    <h3 class="w3-bar-item">Precios en Comodoro Rivadavia</h3>
    
    <p class="w3-bar-item">
      <a href="/precios_claros/index/{{ constants.delta_key }}/ar_u_comodoro_rivadavia">
       ({{ constants.bravo_label }} - {{ constants.alpha_label }} - {{ constants.now_label }})
      </a>
    </p>
    
  </div>
  <br>

  <div class="w3-bar-block w3-border w3-light-grey">
    <h3 class="w3-bar-item">Precios en Puerto Madryn</h3>
    <p class="w3-bar-item">
      <a href="/precios_claros/index/{{ constants.delta_key }}/ar_u_puerto_madryn">
       ({{ constants.bravo_label }} - {{ constants.alpha_label }} - {{ constants.now_label }})
      </a>
    </p>
    
  </div>
  <br>

  <div class="w3-bar-block w3-border w3-light-grey">
    <h3 class="w3-bar-item">Precios en Rada Tilly</h3>
    <p class="w3-bar-item">
      <a href="/precios_claros/index/{{ constants.delta_key }}/ar_u_rada_tilly">
       ({{ constants.bravo_label }} - {{ constants.alpha_label }} - {{ constants.now_label }})
      </a>
    </p>
    
  </div>
  <br>


  <div class="w3-bar-block w3-border w3-light-grey">
    <h3 class="w3-bar-item">Precios en Trelew</h3>

    <p class="w3-bar-item">
      <a href="/precios_claros/index/{{ constants.delta_key }}/ar_u_trelew">
       ({{ constants.bravo_label }} - {{ constants.alpha_label }} - {{ constants.now_label }})
      </a>
    </p>
  </div>
  <br>

  <div class="w3-bar-block w3-border w3-light-grey">
    <h3 class="w3-bar-item">Precios en Ushuaia</h3>
    <p class="w3-bar-item">
      <a href="/precios_claros/index/{{ constants.delta_key }}/ar_v_ushuaia">
       ({{ constants.bravo_label }} - {{ constants.alpha_label }} - {{ constants.now_label }})
      </a>
    </p>

  </div>
  <br>
  
</div>
""" 
