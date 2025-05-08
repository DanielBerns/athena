import pdb
from pathlib import Path
from collections import defaultdict
import json
from contextlib import contextmanager
from typing import Generator, TextIO, Any, List

CODES_AND_STATES = {
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
  "buenos aires": "Buenos Aires",
  "catamarca": "Catamarca",
  "chaco": "Chaco",
  "cordoba": "Córdoba",
  "corrientes": "Corrientes",
  "la pampa": "La Pampa",
  "la rioja": "La Rioja",
  "neuquen": "Neuquén",
  "rio negro": "Río Negro",
  "salta": "Salta",
  "san luis": "San Luis",
  "santa fe": "Santa Fe",
  "santiago del estero": "Santiago del Estero",
  "tucuman": "Tucumán",
  "caba": "CABA",
  "jujuy": "Jujuy",
  "formosa": "Formosa",
  "misiones": "Misiones",
  "capital federal": "CABA",
  "mendoza": "Mendoza",
  "error": "Error"
}


def read_text_lines(resource: Path) -> Generator[str, None, None]:
    with open(resource, "r", encoding="utf-8") as text_file:
         for line in text_file:
             yield line


@contextmanager
def create_text_file(resource: Path) -> Generator[TextIO, None, None]:
    try:
        with open(resource, "w", encoding="utf-8") as target_file:
             yield target_file
    except Exception as message:
        print(f"Error with text file {str(resource):s}: {str(message):s}")


def points_of_sale_by_region(
    region: str,
    table: dict[str, list[dict[str, Any]]],
    region_states: List[str],
    target_file: Path
) -> None:
    with create_text_file(target_file) as report:
        report.write(f"# {region}: Puntos de venta por provincia\n\n")
        for code in region_states:
            points_of_sale = table.get(code, None)
            if points_of_sale:
                state = CODES_AND_STATES[code]
                report.write(f"## {state}\n\n")
                for index, pos in enumerate(points_of_sale):
                    report.write(f"  {index+1:d}. {pos['localidad']} - {pos['direccion']} - {pos['bandera']}\n")
                report.write("\n\n")


def cookie_demo() -> None:
    sample_directory = Path("/home/dberns/Info/athena/juliet/live/Storage/precios_claros/flatstore/samples/20250502183350")
    points_of_sale_directory = Path(sample_directory, "points_of_sale")
    points_of_sale_file = Path(points_of_sale_directory, "messages").with_suffix(".jsonl")

    target_directory = Path("/home/dberns/Info/athena/juliet/live/Reports/")

    table = defaultdict(list)

    for line in read_text_lines(points_of_sale_file):
        record = json.loads(line)
        state = record.get("provincia", "error")
        table[state].append(record)

    all_of_them_file = Path(target_directory, "all_of_them").with_suffix(".md")

    with create_text_file(all_of_them_file) as report:
        report.write("# Puntos de venta por provincia\n\n")
        for code, points_of_sale in table.items():
            state = CODES_AND_STATES[code]
            report.write(f"## {state}\n\n")
            for index, pos in enumerate(points_of_sale):
                report.write(f"  {index+1:d}. {pos['localidad']} - {pos['direccion']} - {pos['bandera']}\n")
            report.write("\n\n")

    # Chaco, Corrientes, Formosa y Misiones
    nea_file = Path(target_directory, "nea").with_suffix(".md")
    nea_states = ["ar-h", "ar-w", "ar-p", "ar-n"]
    points_of_sale_by_region("NEA", table, nea_states, nea_file)

    pdb.set_trace()
    # Jujuy, Salta, Tucuman, La Rioja, Santiago del Estero, Catamarca
    noa_file = Path(target_directory, "noa").with_suffix(".md")
    noa_states = ["ar-y", "jujuy",
                  "ar-a", "salta",
                  "ar-t", "tucuman",
                  "ar-f", "la rioja",
                  "ar-g", "santiago del estero"
                  "ar-k", "catamarca"
    ]
    points_of_sale_by_region("NOA", table, noa_states, noa_file)

    cordoba_file = Path(target_directory, "cordoba").with_suffix(".md")
    cordoba_states = ["ar-x", "cordoba"]
    points_of_sale_by_region("Córdoba", table, cordoba_states, cordoba_file)
