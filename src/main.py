from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, wait
import IPython
from time import perf_counter
import sys
import traceback

from const import DEFAULT_LANGUAGE, DEFAULT_TITLE, DEFAULT_INPUT_FILE, ALL_BOSSES, ALL_PLAYERS

from models.log_class import Log
import func
from languages import LANGUES

def _make_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', required=False)
    parser.add_argument('-l', '--language', required=False, default=DEFAULT_LANGUAGE)
    parser.add_argument('-r', '--reward', action='store_true', required=False)
    parser.add_argument('-i', '--input', required=False, default=DEFAULT_INPUT_FILE)
    return parser

class ThreadPoolExecutorStackTraced(ThreadPoolExecutor):

    def submit(self, fn, *args, **kwargs):
        return super(ThreadPoolExecutorStackTraced, self).submit(
            self._function_wrapper, fn, *args, **kwargs)

    def _function_wrapper(self, fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            print(f"Problematic log is : {args[0]}")
            raise sys.exc_info()[0](traceback.format_exc())

def main(input_file, **kwargs) -> None:
    input_lines = func.txt_file_to_lines(input_file)
    input_urls, error = func.lines_to_urls(input_lines, **kwargs)
    if error:
        print(input_urls)
    # Pour tester séparément
    # input_urls = ["https://dps.report/XXNc-20240117-232331_vg"]
    
    with ThreadPoolExecutorStackTraced() as executor:
        futures = [executor.submit(Log, url) for url in input_urls]
        wait(futures)
        
    print("\n")
    if kwargs.get("debug", False):
        IPython.embed()
    # Fonction reward si pas de test
    if not error:
        split_run_message = func.get_message_reward(ALL_BOSSES, ALL_PLAYERS, titre=DEFAULT_TITLE)
        for message in split_run_message:
            print(message)

    print("\n")

if __name__ == "__main__":
    print("Starting\n")
    start_time = perf_counter()
    LANGUES["selected_language"] = LANGUES["FR"]
    args = _make_parser().parse_args()
    main(args.input, reward_mode=args.reward, debug=args.debug, language=args.language)
    end_time = perf_counter()
    print(f"--- {end_time - start_time:.3f} seconds ---\n")