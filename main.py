from argparse import ArgumentParser
from time import perf_counter
import grequests
from src import func

from src.const import REQUEST_HEADERS, DPS_REPORT_JSON_URL, DEFAULT_LANGUAGE, DEFAULT_TITLE, DEFAULT_INPUT_FILE, ALL_BOSSES, ALL_PLAYERS
from src.models.log_class import Log
from src.models.boss_facto import BossFactory
from i18n.languages import language_config
from src.input import InputParser

def _make_parser() -> ArgumentParser:
    with open(DEFAULT_INPUT_FILE, "r") as file:
        default_input = file.read()
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', required=False)
    parser.add_argument('-l', '--language', required=False, default=DEFAULT_LANGUAGE)
    parser.add_argument('-r', '--reward', action='store_true', required=False)
    parser.add_argument('-i', '--input', required=False, default=default_input)
    return parser

def debugLog(url):
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
    # YES

def main(input_string, **kwargs) -> None:
    input = InputParser(input_string)
    print(input)
    urls = input.urls
    requests = []
    for url in urls:
        requests.append(grequests.get(url))
        requests.append(grequests.get(DPS_REPORT_JSON_URL+url, headers=REQUEST_HEADERS))
    responses = grequests.map(requests, size=2*len(urls))
    logs = [Log(url) for url in urls]
    for i in range(len(urls)):
        logs[i].set_jcontent(responses[2*i])
        logs[i].set_pjcontent(responses[2*i+1])
    for log in logs:
        BossFactory.create_boss(log)
    print("\n")
    split_run_message = func.get_message_reward(ALL_BOSSES, ALL_PLAYERS, titre=DEFAULT_TITLE)
    for message in split_run_message:
        print(message)
    print("\n")

if __name__ == "__main__":
    print("Starting\n")
    start_time = perf_counter()
    args = _make_parser().parse_args()
    language_config.set_language(args.language)
    main(args.input, reward_mode=args.reward, debug=args.debug, language=args.language)
    #debugLog("https://dps.report/i7N1-20241214-142308_frae")
    end_time = perf_counter()
    print(f"--- {end_time - start_time:.3f} seconds ---\n")