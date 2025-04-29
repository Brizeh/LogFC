import re

from config.settings import BOSS_DICT
from utils.time import extract_timestamp


class InputParser:
    def __init__(self, input_string):
        self.input = input_string
        self.urls = self.detect_urls()

    def __str__(self):
        title = f"{len(self.urls)} urls detected :\n"
        for url in self.urls:
            title += f" - {url}\n"
        return title

    def detect_urls(self):
        valid_terms = list(BOSS_DICT.values())
        valid_terms.sort(key=lambda x: (len(x), x), reverse=True)
        # RegEx pour capturer chaque lien valide, même s'ils sont collés
        regex_full = rf"https://dps\.report/[a-zA-Z0-9]{{4}}-\d{{8}}-\d{{6}}_({'|'.join(valid_terms)})"

        # Utilisation de re.finditer pour identifier toutes les correspondances
        matches = [match.group(0) for match in re.finditer(regex_full, self.input)]

        # Affichage des résultats
        duplicates_checker = {}
        for match in matches:
            end = match.split("_")[-1]
            if duplicates_checker.get(end):
                duplicates_checker[end].append(match)
            else:
                duplicates_checker[end] = [match]

        return [max(urlz, key=extract_timestamp) for urlz in duplicates_checker.values()]