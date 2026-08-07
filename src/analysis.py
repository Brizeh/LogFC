from .const import DEFAULT_TITLE


class Analysis:
    """Etat d'une analyse de run.

    Tout ce qui varie d'un run a l'autre vit ici plutot que dans des
    variables de module : deux analyses peuvent donc tourner en parallele
    sans se marcher dessus, et il n'y a plus rien a reinitialiser entre
    deux appels puisque l'objet est simplement jete a la fin.

    Ce qui n'y figure pas est de la configuration partagee en lecture
    seule (CUSTOM_NAMES, ALL_MECHS, les dictionnaires de langue).
    """

    def __init__(self, title: str = DEFAULT_TITLE):
        self.title       = title
        self.bosses      = []   # Boss, dans l'ordre de creation
        self.players     = {}   # compte -> Player
        self.arxiv       = {}   # url du log -> compte -> categorie -> stat
        self.extra_mechs = {}   # categorie -> stat -> description
        self.dups        = {}   # suffixe de log -> urls, pour compter les fails
