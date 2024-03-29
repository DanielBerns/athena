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
    <link href="/static/img/favicon.ico" rel="shortcut icon">    
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
    <article class="w3-row w3-pale-green">
        <div class="w3-col w3-left-align"><h2>{{ dawp.name_and_brand }}</h2></div>
        <div class="w3-col w3-left-align"><h3>{{ dawp.code }}</h3></div>
        <ul class="w3-ul">
            <li class="w3-row w3-pale-blue"> 
                <div class="w3-col m12 l12 w3-left-align">Rango de precios</div> 
                {% if dawp.now_stats %}
                    <div class="w3-col m3 l3 w3-right-align">Hoy</div>
                    {% for stat in dawp.now_stats %}
                        <div class="w3-col m3 l3 w3-right-align">{{ stat }}</div>
                    {% endfor %}
                {% endif %}
                {% if dawp.week_stats %}
                    <div class="w3-col m3 l3 w3-right-align">La semana pasada</div>                
                    {% for stat in dawp.week_stats %}
                        <div class="w3-col m3 l3 w3-right-align">{{ stat }}</div>
                    {% endfor %}
                {% endif %}
                {% if dawp.month_stats %}
                    <div class="w3-col m3 l3 w3-right-align">El mes pasado</div>                                
                    {% for stat in dawp.month_stats %}
                        <div class="w3-col m3 l3 w3-right-align">{{ stat }}</div>
                    {% endfor %}
                {% endif %}
            </li>
            <li class="w3-row w3-pale-blue"> 
            <div class="w3-col m3 l3 w3-left-align">Punto de venta</div> 
            <div class="w3-col m3 l3 w3-right-align">Hoy</div>
            <div class="w3-col m3 l3 w3-right-align">La semana pasada</div> 
            <div class="w3-col m3 l3 w3-right-align">El mes pasado</div>                 
            </li>
            {% for pos in dawp.list_of_pos %}
                <li class="w3-row w3-pale-blue"> 
                <div class="w3-col m3 l3 w3-left-align">{{pos}}</div> 
                <div class="w3-col m3 l3 w3-right-align">{{dawp.now_prices_per_pos.get(pos, "&nbsp;")}}</div>
                <div class="w3-col m3 l3 w3-right-align">{{dawp.week_prices_per_pos.get(pos, "&nbsp;")}}</div> 
                <div class="w3-col m3 l3 w3-right-align">{{dawp.week_prices_per_pos.get(pos, "&nbsp;")}}</div>                 
                </li>
            {% endfor %}
        </ul>        
        
    </article>
{% endfor %}
</div>

</div>

</body></html>"""


# {% for dawp in content %}
#     <br>
#     <article class="w3-row w3-pale-green">
#         <div class="w3-col w3-left-align"><h2>{{ dawp.name_and_brand }}</h2></div>
#         <div class="w3-col w3-left-align"><h3>{{ dawp.code }}</h3></div>
#         <ul class="w3-ul">
#             <li class="w3-row w3-pale-blue"> 
#                 <div class="w3-col m12 l12 s12 w3-left-align">Rango de precios</div> 
#                 {% for now, week, month in zip(dawp.now_stats, dawp.week_stats, dwap.month_stats) %}
#                     <div class="w3-col m4 l5 s6 w3-right-align">{{ now }}</div>
#                     <div class="w3-col m4 l5 s6 w3-right-align">{{ week }}</div>
#                     <div class="w3-col m4 l5 s6 w3-right-align">{{ month }}</div>
#                 {% endfor %}
#             </li>
#             {% for pos in dawp.list_of_pos %}
#                 <li class="w3-row w3-pale-blue"> 
#                 <div class="w3-col m5 l6 w3-left-align">Now {{pos}}</div> 
#                 <div class="w3-col m4 l5 w3-right-align">Week {{pos}}</div>
#                 <div class="w3-col m4 l5 w3-right-align">Month {{pos}}</div>
#                 </li>
#             {% endfor %}
#         </ul>
#     </article>
# {% endfor %}
# </div>
