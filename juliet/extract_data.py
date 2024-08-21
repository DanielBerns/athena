import json
from collections import defaultdict

uri = "/home/dberns/Info/athena/juliet/live/Storage/precios_claros/flatstore/samples/20240731183003/points_of_sale/messages.jsonl"


cities_per_state = defaultdict(list)

states = {
  "ar-a": "Salta",
  "ar-b": "Buenos Aires",
  "ar-c": "CABA",
  "ar-d": "San Luis",
  "ar-e": "Entre Rios",
  "ar-f": "La Rioja",
  "ar-g": "Santiago del Estero",
  "ar-h": "Chaco",
  "ar-j": "San Juan",
  "ar-k": "Catamarca",
  "ar-l": "La Pampa",
  "ar-m": "Mendoza",
  "ar-n": "Misiones",
  "ar-p": "Formosa",
  "ar-q": "Neuquén",
  "ar-r": "Río Negro",
  "ar-s": "Santa Fé",
  "ar-t": "Tucumán",
  "ar-u": "Chubut",
  "ar-v": "Tierra del Fuego",
  "ar-w": "Corrientes",
  "ar-x": "Córdoba",
  "ar-y": "San Salvador de Jujuy",
  "ar-z": "Santa Cruz",
}

with open(uri, "r", encoding="utf-8") as source, \
     open("cities_per_state.txt", "w", encoding="utf-8") as target:
    for line in source:
        data = json.loads(line)
        key = data["provincia"]
        value = data["localidad"]
        cities_per_state[key].append(value)

    target.write("{\n\n")
    for state, value in cities_per_state.items():
        cities_in_this_state = set(value)
        for name in cities_in_this_state:
            target.write(f'  "{name:s}": ("{name:s}", "{states[state]:s}"),\n')
    target.write("}\n\n")        
            
