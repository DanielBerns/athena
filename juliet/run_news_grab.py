from typing import Dict

from components.configuration import CLI
from components.core import create_application, show
from components.news import Actions

def get_arguments() -> Dict[str, str]:
    cli = CLI()
    cli.add_arguments(
        "-d",
        "--dotenv",
        type=str,
        default=".env",
        required=False,
        help="name of dotenv file",
    )
    cli.add_arguments(
        "-m",
        "--mode",
        choices=["dev", "test", "live"],
        type=str,
        default="live",
        required=False,
        help="how to run? dev, test or live",
    )
    return cli.arguments


def main() -> None:
    application_name: str = "run_news_grab"
    arguments = get_arguments()

    resources = [
        ("adnsur",                  "https://www.adnsur.com.ar/",                             "page", ".html"),
        ("jornada",                 "https://www.diariojornada.com.ar/home",                  "page", ".html"),
        ("cronica",                 "https://www.diariocronica.com.ar/",                      "page", ".html"),
        ("elchubut_cdr",            "https://www.elchubut.com.ar/seccion/comodoro-rivadavia", "page", ".html"),
        ("elchubut_raw",            "https://www.elchubut.com.ar/seccion/rawson",             "page", ".html"),
        ("elchubut_trw",            "https://www.elchubut.com.ar/seccion/trelew",             "page", ".html"),
        ("elchubut_pmy",            "https://www.elchubut.com.ar/seccion/puerto-madryn",      "page", ".html"),
        ("elchubut_esq",            "https://www.elchubut.com.ar/seccion/esquel",             "page", ".html"),
        ("infobae",                 "https://www.infobae.com/",                               "page", ".html"),
        ("clarin_lo_ultimo",        "https://www.clarin.com/rss/lo-ultimo/",                  "info", ".xml"),
        ("clarin_politica",         "https://www.clarin.com/rss/politica/",                   "info", ".xml"),
        ("clarin_economia",         "https://www.clarin.com/rss/economia/",                   "info", ".xml"),
        ("clarin_internacional",    "https://www.clarin.com/rss/internacional/",              "info", ".xml"),
        ("ambito_ultimas_noticias", "https://www.ambito.com/rss/pages/ultimas-noticias.xml",  "info", ".xml"),
        ("ambito_economia",         "https://www.ambito.com/rss/pages/economia.xml",          "info", ".xml"),
        ("ambito_finanzas",         "https://www.ambito.com/rss/pages/finanzas.xml",          "info", ".xml"),
        ("ambito_politica",         "https://www.ambito.com/rss/pages/politica.xml",          "info", ".xml"),
        ("infobae_rss",             "https://www.infobae.com/feeds/rss/",                     "info", ".xml"),
        ("cronica_actualidad",      "https://www.diariocronica.com.ar/rss/actualidad",        "info", ".xml"),
        ("cronica_politica",        "https://www.diariocronica.com.ar/rss/politica",          "info", ".xml"),
        ("cronica_economia",        "https://www.diariocronica.com.ar/rss/economia",          "info", ".xml"),
        ("cronica_energia",         "https://www.diariocronica.com.ar/rss/energia",           "info", ".xml"),
        ("cronica_noticias",        "https://www.diariocronica.com.ar/rss/noticias",          "info", ".xml"),                                
    ]

    with create_application(application_name, arguments) as application:
        show(f"{application_name:s} 1")
        show(f"{application_name:s} 1")
        (   storage_news,
            results_news,
            reports_news,
        ) = Actions.start(application)
        store = Actions.create_store(storage_news)
        sample_home = Actions.create_sample(store, resources)
        show(f"{application_name:s} {str(sample_home):s} 2")

if __name__ == "__main__":
    main()
