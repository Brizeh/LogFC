from time import perf_counter

import grequests

from config.settings import REQUEST_HEADERS, DPS_REPORT_JSON_URL, ALL_BOSSES, ALL_PLAYERS, DEFAULT_TITLE
from core.factories.boss_factory import BossFactory
from core.models.log import Log
from i18n.languages import language_config
from services.parsers.argument_parser import make_parser
from services.parsers.input_parser import InputParser
from views.report_generator import ReportGenerator


def debug_log(url):
    log = Log(url)
    jcontent = grequests.get(url)
    pjcontent = grequests.get(DPS_REPORT_JSON_URL, params={"permalink": url}, headers=REQUEST_HEADERS)
    responses = grequests.map([jcontent, pjcontent], size=2)
    log.set_jcontent(responses[0])
    log.set_pjcontent(responses[1])
    BossFactory.create_boss(log)
    boss = ALL_BOSSES[0]
    print(boss.start_date)
    print(boss.mvp)
    print(boss.lvp)


def main(input_string, **kwargs):

    # Parse the input
    input_parser = InputParser(input_string)
    print(input_parser)

    # Retrieve the URLs
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
    report_generator = ReportGenerator(ALL_BOSSES, ALL_PLAYERS, titre=DEFAULT_TITLE)
    split_run_message = report_generator.generate()
    for message in split_run_message:
        print(message)


if __name__ == "__main__":
    print("Starting\n")
    start_time = perf_counter()

    # Initialize the parser with the default parameters
    args = make_parser().parse_args()

    # Define the language to use in the report
    language_config.set_language(args.language)

    # Run the main function
    main(args.input, reward_mode=args.reward, debug=args.debug)

    end_time = perf_counter()
    print(f"--- Generated in {end_time - start_time:.3f} seconds ---\n")
