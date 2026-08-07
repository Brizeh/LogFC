from argparse import ArgumentParser
from time import perf_counter
import grequests
import json

from . import func
from . import wingman
from .analysis import Analysis
from .const import REQUEST_HEADERS, DPS_REPORT_JSON_URL, DEFAULT_LANGUAGE, DEFAULT_TITLE, DEFAULT_INPUT_FILE
from .models.log_class import Log
from .models.boss_facto import BossFactory
from .input import InputParser

import matplotlib.pyplot as plt

def printjson(data: dict) -> None:
    try:
        name = next(
            key for key, value in globals().items()
            if value is data
        )
    except:
        name ="data"
    with open(f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def _make_parser() -> ArgumentParser:
    try:
        with open(DEFAULT_INPUT_FILE, "r") as file:
            default_input = file.read()
    except FileNotFoundError:
        print(f"{DEFAULT_INPUT_FILE} not found, copy src/input_logs.example.txt to create it")
        default_input = ""
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', required=False)
    parser.add_argument('-l', '--language', required=False, default=DEFAULT_LANGUAGE)
    parser.add_argument('-r', '--reward', action='store_true', required=False)
    parser.add_argument('-i', '--input', required=False, default=default_input)
    return parser

def debugLog(url):
    analysis = Analysis()
    log = Log(url)
    pjcontent = grequests.get(DPS_REPORT_JSON_URL, params={"permalink": url}, headers=REQUEST_HEADERS)
    responses = grequests.map([pjcontent], size=1)
    log.set_pjcontent(responses[0])
    BossFactory.create_boss(log, analysis)
    wingman.fetch_percentiles(analysis.bosses)
    boss = analysis.bosses[0]
    print(boss.start_date)
    if boss.mvp:
        for mvp in boss.mvp:
            print(mvp)
    if boss.lvp:
        for lvp in boss.lvp:
            print(lvp)

def main(input_string, **kwargs) -> None:
    analysis = Analysis(title=DEFAULT_TITLE, language=kwargs.get('language') or DEFAULT_LANGUAGE)
    input = InputParser(input_string, analysis)
    print(input)
    urls = input.urls
    requests = [grequests.get(DPS_REPORT_JSON_URL+url, headers=REQUEST_HEADERS) for url in urls]
    responses = grequests.map(requests, size=len(urls))
    logs = [Log(url) for url in urls]
    for i in range(len(urls)):
        logs[i].set_pjcontent(responses[i])
    for log in logs:
        BossFactory.create_boss(log, analysis)
    wingman.fetch_percentiles(analysis.bosses)
    print("\n")
    split_run_message = func.get_message_reward(analysis)
    for message in split_run_message:
        print(message)
    print("\n")

if __name__ == "__main__":
    print("Starting\n")
    start_time = perf_counter()
    args = _make_parser().parse_args()
    main(args.input, reward_mode=args.reward, debug=args.debug, language=args.language)
    #debugLog("https://dps.report/kjk1-20260729-002814_deci")
    print(f"\nFinished in {perf_counter() - start_time:.2f} seconds")