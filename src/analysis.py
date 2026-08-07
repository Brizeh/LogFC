from .const import DEFAULT_LANGUAGE, DEFAULT_TITLE
from .languages import LANGUES


class Analysis:
    """State of a single analysis run.

    Everything that varies from one run to the next lives here rather
    than in module-level variables: two analyses can therefore run in
    parallel without stepping on each other, even in different
    languages, and there's nothing to reset between two calls since the
    object is simply discarded at the end.

    What does not live here is shared, read-only configuration
    (CUSTOM_NAMES, ALL_MECHS, the language dictionaries).
    """

    def __init__(self, title: str = DEFAULT_TITLE, language: str = DEFAULT_LANGUAGE):
        self.title       = title
        self.language    = LANGUES[language]  # message dictionary
        self.bosses      = []   # Boss, in creation order
        self.players     = {}   # account -> Player
        self.arxiv       = {}   # log url -> account -> category -> stat
        self.extra_mechs = {}   # category -> stat -> description
        self.dups        = {}   # log suffix -> urls, for counting fails
