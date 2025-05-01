from argparse import ArgumentParser

from config.settings import DEFAULT_INPUT_FILE, DEFAULT_LANGUAGE


def make_parser() -> ArgumentParser:
    with open(DEFAULT_INPUT_FILE, "r") as file:
        default_input = file.read()
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', required=False)
    parser.add_argument('-l', '--language', required=False, default=DEFAULT_LANGUAGE)
    parser.add_argument('-r', '--reward', action='store_true', required=False)
    parser.add_argument('-i', '--input', required=False, default=default_input)
    return parser