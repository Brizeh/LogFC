from .models import boss_facto  # noqa: F401 - son import peuple Boss.registry
from .models.boss_class import Boss
import re
from datetime import datetime

class InputParser:
    def __init__(self, input_string, analysis, project=False):
        self.input = input_string
        self.analysis = analysis
        self.project = project
        self.urls = self.detectUrls()
        
        
    def __str__(self):
        title = f"{len(self.urls)} urls detected :\n"
        for url in self.urls:
            title+=f" - {url}\n"
        return title  
        
    def detectUrls(self):
        valid_terms = list(Boss.url_suffixes())
        valid_terms.sort(key=lambda x: (len(x), x), reverse=True)
        # RegEx pour capturer chaque lien valide, même s'ils sont collés
        regex_full = rf"https://dps\.report/[a-zA-Z0-9]{{4}}-\d{{8}}-\d{{6}}_({'|'.join(valid_terms)})"

        # Utilisation de re.finditer pour identifier toutes les correspondances
        matches = [match.group(0) for match in re.finditer(regex_full, self.input)]
        # Affichage des résultats
        if not self.project:
            dups = self.analysis.dups
            for match in matches:
                end = match.split("_")[-1]
                if dups.get(end):
                    dups[end].append(match)
                else:
                    dups[end] = [match]
        else:
            return list(set(matches.copy()))
        
        def extract_timestamp(url):
            timestamp_str = url.split('_')[0] # Extract the timestamp part (e.g., '20241124-205115')
            date = timestamp_str.split('-')[1]+"-"+timestamp_str.split('-')[2]
            return datetime.strptime(date, "%Y%m%d-%H%M%S")
    
        return [max(urlz, key=extract_timestamp) for urlz in self.analysis.dups.values()]
    