from typing import List

from core.models.log import Log


class DataAccessMixin:
    """Fournit les méthodes d'accès aux données de base"""

    def __init__(self, log: Log, *args, **kwargs) -> None:
        """
        Initializes a boss encounter from a Log object.

        Args:
            log: The Log object containing the encounter data
        """
        super().__init__(*args, **kwargs)
        self.log: Log = log