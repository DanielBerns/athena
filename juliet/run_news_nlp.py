from typing import Dict

from components.configuration import CLI
from components.core import create_application, show
from components.helpers import get_resource
from components.news import Actions, ADNSUR, RSS, TrieTarget, TokenizerTarget


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
    application_name: str = "run_news_nlp"
    arguments = get_arguments()

    processors = [
        ADNSUR(),
        RSS("clarin_lo_ultimo",        "info", ".xml"),
        RSS("clarin_politica",         "info", ".xml"),
        RSS("clarin_economia",         "info", ".xml"),
        RSS("clarin_internacional",    "info", ".xml"),
        RSS("ambito_ultimas_noticias", "info", ".xml"),
        RSS("ambito_economia",         "info", ".xml"),
        RSS("ambito_finanzas",         "info", ".xml"),
        RSS("ambito_politica",         "info", ".xml"),        
    ]
    
    with create_application(application_name, arguments) as application:
        show(f"{application_name:s} start")
        (   storage_news,
            results_news,
            reports_news,
        ) = Actions.start(application)
        store = Actions.create_store(storage_news)
        tokenizer_target = TokenizerTarget()
        Actions.store_samples_to_news_target(store, tokenizer_target, processors)
        report_tokenizer = get_resource(reports_news, "tokenizer", ".md")
        tokenizer_target.write(report_tokenizer)
        trie_target = tokenizer_target.get_trie_target()
        Actions.store_samples_to_news_target(store, trie_target, processors)        
        report_trie = get_resource(reports_news, "trie", ".md")
        trie_target.write(report_trie)
        report_show = get_resource(reports_news, "show", ".md")
        trie_target.show(report_show)        
        pattern_frequencies = trie_target.trie.pattern_frequencies(7)
        report_pattern_frequencies = get_resource(reports_news, "pattern_frequencies", ".md")
        with open(report_pattern_frequencies, 'w') as target:
            for pattern, frequency in pattern_frequencies:
                target.write(trie_target.tokenizer.decode(pattern) + "\n")
                target.write(f"  {frequency:d}\n")
        useful_words = tokenizer_target.tokenizer.useful_words()
        report_useful_words = get_resource(reports_news, "useful_words", ".md")
        with open(report_useful_words, 'w') as target:
            for frequency, word in useful_words:
                target.write(f"{word:s} - {frequency:d}\n")

        show(f"{application_name:s} stop")

if __name__ == "__main__":
    main()
