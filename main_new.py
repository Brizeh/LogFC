from argparse import ArgumentParser
from time import perf_counter

import grequests

from config.settings import DEFAULT_LANGUAGE, DEFAULT_INPUT_FILE, REQUEST_HEADERS, DPS_REPORT_JSON_URL, ALL_BOSSES, \
    ALL_PLAYERS, DEFAULT_TITLE
from core.factories.boss_factory import BossFactory
from core.models.log import Log
from i18n.languages import language_config
from services.parsers.input_parser import InputParser
from views.report_generator import ReportGenerator


# from core.factories.boss_factory import BossFactory
# from services.parsers.input_parser import InputParser


def _make_parser() -> ArgumentParser:
    with open(DEFAULT_INPUT_FILE, "r") as file:
        default_input = file.read()
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', required=False)
    parser.add_argument('-l', '--language', required=False, default=DEFAULT_LANGUAGE)
    parser.add_argument('-r', '--reward', action='store_true', required=False)
    parser.add_argument('-i', '--input', required=False, default=default_input)
    return parser


def debug_log(url):
    # ... code pour déboguer un log spécifique ...
    pass


def main(input_string, **kwargs):

    # Parse the input and retrieve the URLs
    input_parser = InputParser(input_string)
    urls = input_parser.urls

    # Récupérer les données pour chaque URL
    requests = []
    for url in urls:
        requests.append(grequests.get(url))
        requests.append(grequests.get(DPS_REPORT_JSON_URL + url, headers=REQUEST_HEADERS))

    # Execute the requests
    responses = grequests.map(requests, size=2 * len(urls))

    # Créer les objets Log et leur attribuer les contenus JSON
    logs = [Log(url) for url in urls]
    for i in range(len(urls)):
        logs[i].set_jcontent(responses[2 * i])
        logs[i].set_pjcontent(responses[2 * i + 1])

    # Créer les objets Boss correspondants
    for log in logs:
        BossFactory.create_boss(log)

    # Générer et afficher le rapport
    print(f"--- test\n")
    # split_run_message = ReportGenerator.generate_report(ALL_BOSSES, ALL_PLAYERS, titre=DEFAULT_TITLE)
    # for message in split_run_message:
    #     print(message)


if __name__ == "__main__":
    print("Starting\n")
    start_time = perf_counter()

    # Initialize the parser with the default parameters
    args = _make_parser().parse_args()

    # Define the language to use in the report
    language_config.set_language(args.language)

    # Run the main function
    main(args.input, reward_mode=args.reward, debug=args.debug)

    end_time = perf_counter()
    print(f"--- Generated in {end_time - start_time:.3f} seconds ---\n")
