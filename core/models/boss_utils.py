from typing import List, ClassVar

from config.settings import CUSTOM_NAMES
from core.models.boss_player_info import PlayerInfoMixin


class BossUtilsMixin(PlayerInfoMixin):

    # Constants for buff and mechanic IDs
    FOOD_SWAP_ICON: ClassVar[str] = "https://wiki.guildwars2.com/images/d/d6/Champion_of_the_Crown.png"


    def players_to_string(self, i_players: List[int]) -> str:
        """
        Converts a list of player indices into a formatted string with their names.

        Uses custom names if available, otherwise falls back to the player's log name.
        The result is formatted in Markdown for display.

        Args:
            i_players: List of player indices

        Returns:
            Formatted string of player names
        """
        name_list = []

        for i in i_players:
            account = self.get_player_account(i)
            custom_name = CUSTOM_NAMES.get(account)

            if custom_name:
                name_list.append(custom_name)
            else:
                name_list.append(self.get_player_name(i))

        return "__" + '__ / __'.join(name_list) + "__"

    def get_foodswap_count(self, i_player: int) -> int:
        """
        Counts how many times the player changed food during the fight.

        Detects food buff changes by identifying a specific icon.

        Args:
            i_player: Player index

        Returns:
            Number of food swaps
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return 0

        buff_map = self.log.pjcontent.get('buffMap', {})
        buff_uptimes = players[i_player].get('buffUptimes', [])

        food_swap_ids = []

        for buff_name, data in buff_map.items():
            if data.get('icon') == self.FOOD_SWAP_ICON:
                try:
                    food_swap_ids.append(int(buff_name[1:]))  # Remove 'b' prefix
                except ValueError:
                    continue

        food_swap_count = 0

        for buff in buff_uptimes:
            if buff.get('id') in food_swap_ids:
                states = buff.get('states', [])
                for state in states:
                    if len(state) > 1 and state[1] == 1:
                        food_swap_count += 1

        return food_swap_count