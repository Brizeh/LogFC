from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.boss import Boss


class Player:
    """
    Représente un joueur participant à une rencontre GW2.
    Suit les performances du joueur sur plusieurs rencontres.
    """

    def __init__(self, boss: 'Boss', account: str):
        """
        Initialise un objet Player.

        Args:
            boss: La première rencontre de boss où ce joueur a été vu
            account: Le nom de compte du joueur
        """
        self.account: str = account
        self.name: str = self._get_name_from_boss(boss)
        self.bosses: List['Boss'] = [boss]
        self.mvps: int = 0
        self.lvps: int = 0
        self.marks: Dict[str, float] = {}  # {boss_name: mark}

    def _get_name_from_boss(self, boss: 'Boss') -> str:
        """Récupère le nom du joueur depuis une rencontre de boss."""
        player_index = None
        for i in boss.player_list:
            if boss.get_player_account(i) == self.account:
                player_index = i
                break

        if player_index is not None:
            return boss.get_player_name(player_index)
        return self.account

    def add_boss(self, boss: 'Boss') -> None:
        """
        Ajoute une rencontre de boss à l'historique du joueur.

        Args:
            boss: La rencontre de boss à ajouter
        """
        if boss not in self.bosses:
            self.bosses.append(boss)

    def add_mark(self, mark: float, boss_name: Optional[str] = None) -> None:
        """
        Ajoute une note au joueur pour une rencontre spécifique.

        Args:
            mark: La note attribuée (généralement sur 20)
            boss_name: Le nom du boss pour lequel la note est attribuée
        """
        if boss_name:
            self.marks[boss_name] = mark
        else:
            # Génère une clé unique si le nom du boss n'est pas spécifié
            key = f"mark_{len(self.marks)}"
            self.marks[key] = mark

    def get_mark(self) -> Optional[float]:
        """
        Calcule la note moyenne du joueur sur toutes les rencontres.

        Returns:
            La note moyenne ou None si aucune note n'existe
        """
        if not self.marks:
            return None

        total = sum(self.marks.values())
        return total / len(self.marks)

    def __repr__(self) -> str:
        """Représentation textuelle de l'objet Player."""
        return f"Player({self.account}, mvps={self.mvps}, lvps={self.lvps})"