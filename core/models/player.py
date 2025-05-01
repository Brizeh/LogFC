from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.boss import Boss


class Player:
    """
    Represents a player participating in a GW2 encounter.
    Tracks the player's performance across multiple encounters.
    """

    def __init__(self, boss: 'Boss', account: str):
        """
        Initializes a Player object.

        Args:
            boss: The first boss encounter where this player was seen
            account: The player's account name
        """
        self.account: str = account
        self.name: str = self._get_name_from_boss(boss)
        self.bosses: List['Boss'] = [boss]
        self.mvps: int = 0
        self.lvps: int = 0
        self.marks: Dict[str, float] = {}  # {boss_name: mark}

    def _get_name_from_boss(self, boss: 'Boss') -> str:
        """Retrieves the player's name from a boss encounter."""
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
        Adds a boss encounter to the player's history.

        Args:
            boss: The boss encounter to add
        """
        if boss not in self.bosses:
            self.bosses.append(boss)

    def add_mark(self, mark: float, boss_name: Optional[str] = None) -> None:
        """
        Adds a score to the player for a specific encounter.

        Args:
            mark: The assigned score (typically out of 20)
            boss_name: The name of the boss for which the score is assigned
        """
        if boss_name:
            self.marks[boss_name] = mark
        else:
            # Generates a unique key if the boss name is not specified
            key = f"mark_{len(self.marks)}"
            self.marks[key] = mark

    def get_mark(self) -> Optional[float]:
        """
        Calculates the player's average score across all encounters.

        Returns:
            The average score or None if no scores exist
        """
        if not self.marks:
            return None

        total = sum(self.marks.values())
        return total / len(self.marks)

    def __repr__(self) -> str:
        """Text representation of the Player object."""
        return f"Player({self.account}, mvps={self.mvps}, lvps={self.lvps})"
