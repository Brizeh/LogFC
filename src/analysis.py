from .const import DEFAULT_LANGUAGE, DEFAULT_TITLE
from .languages import LANGUES


class Analysis:
    """Etat d'une analyse de run.

    Tout ce qui varie d'un run a l'autre vit ici plutot que dans des
    variables de module : deux analyses peuvent donc tourner en parallele
    sans se marcher dessus, meme dans des langues differentes, et il n'y
    a plus rien a reinitialiser entre deux appels puisque l'objet est
    simplement jete a la fin.

    Ce qui n'y figure pas est de la configuration partagee en lecture
    seule (CUSTOM_NAMES, ALL_MECHS, les dictionnaires de langue).
    """

    def __init__(self, title: str = DEFAULT_TITLE, language: str = DEFAULT_LANGUAGE):
        self.title       = title
        self.language    = LANGUES[language]  # dictionnaire de messages
        self.bosses      = []   # Boss, dans l'ordre de creation
        self.players     = {}   # compte -> Player
        self.arxiv       = {}   # url du log -> compte -> categorie -> stat
        self.extra_mechs = {}   # categorie -> stat -> description
        self.dups        = {}   # suffixe de log -> urls, pour compter les fails
