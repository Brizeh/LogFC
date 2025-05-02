from const import BOSS_DICT
import re
from datetime import datetime

class InputParser:
    def __init__(self, input_string):
        self.input = input_string
        self.urls = self.detectUrls()
        
    def __str__(self):
        title = f"{len(self.urls)} urls detected :\n"
        for url in self.urls:
            title+=f" - {url}\n"
        return title  
        
    def detectUrls(self):
        valid_terms = list(BOSS_DICT.values())
        valid_terms.sort(key=lambda x: (len(x), x), reverse=True)
        # RegEx pour capturer chaque lien valide, même s'ils sont collés
        regex_full = rf"https://dps\.report/[a-zA-Z0-9]{{4}}-\d{{8}}-\d{{6}}_({'|'.join(valid_terms)})"

        # Utilisation de re.finditer pour identifier toutes les correspondances
        matches = [match.group(0) for match in re.finditer(regex_full, self.input)]

        # Affichage des résultats
        dupsChecker = {}
        for match in matches:
            end = match.split("_")[-1]
            if dupsChecker.get(end):
                dupsChecker[end].append(match)
            else:
                dupsChecker[end] = [match]
        
        def extract_timestamp(url):
            timestamp_str = url.split('_')[0] # Extract the timestamp part (e.g., '20241124-205115')
            date = timestamp_str.split('-')[1]+"-"+timestamp_str.split('-')[2]
            return datetime.strptime(date, "%Y%m%d-%H%M%S")
    
        return [max(urlz, key=extract_timestamp) for urlz in dupsChecker.values()]
    