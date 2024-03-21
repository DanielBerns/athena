HTML_INDEX = """
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
    {{ local_style }}
</head>
<body>

<h1 class="w3-center">{{ title }}</h1>

<div class="w3-row">
<input oninput="w3.filterHTML('#patterns', 'li', this.value)" class="w3-input w3-light-gray" placeholder="Búsqueda de artículos...">
</div>

<div id="patterns" class="w3-container w3-pale-green">

<ul class="w3-ul w3-border w3-hoverable"">
{% for child in content %}
    <li class="w3-pale-blue"><a href="{{root}}{{child.url}}">{{child.pattern}}</a></li>
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
    <link rel="stylesheet" href="/static/css/font-awesome.min.css">            
    <script src="/static/js/w3.js"></script>        
    {{ local_style }}
</head>
<body>
<h1 class="w3-center">{{ title }}</h1>
<div class="w3-container w3-light-grey">

<article class="w3-row">
<input oninput="w3.filterHTML('#articles', 'article', this.value)" class="w3-input w3-light-gray" placeholder="Búsqueda de artículos...">
</article>

<div id="articles">
{% for awp in content %}
<br>
<article class="w3-row w3-pale-green">
<div class="w3-col w3-left-align"><h2>{{ awp.name_and_brand }}</h2></div>
<div class="w3-col w3-left-align"><h3>{{ awp.code }}</h3></div>
<ul class="w3-ul">
<li class="w3-row w3-pale-blue"> 
<div class="w3-col m5 l6 w3-left-align">precio indicativo</div> 
<div class="w3-col m4 l5 w3-right-align">{{ awp.reference_price }}</div>
</li>
{% for entry in awp.entries() %}
<li class="w3-row w3-pale-blue"> 
<div class="w3-col m5 l6 w3-left-align">{{ entry.label }}</div> 
<div class="w3-col m4 l5 w3-right-align">{{ entry.value }}</div>
</li>
{% endfor %}
</ul>
</article>
{% endfor %}
</div>

</div>

</body></html>"""

# <span>{{ awp.code }}</span>

# <!--
# <ul>
# {% for entry in awp.entries() %}
# <li> <span> {{ entry.label }} </span> <span> {{ entry.value }} </span> </li>
# {% endfor %}
# </ul>
# -->
