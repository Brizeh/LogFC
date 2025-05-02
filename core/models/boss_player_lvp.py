from typing import List, Optional

from config.settings import ALL_PLAYERS
from core.models.boss_player_lvp_mvp import PlayerDamageMixin
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class PlayerLvpMixin(PlayerDamageMixin):

    def add_lvps(self, players: List[int]) -> None:
        """
        Adds players to the LVP (Least Valuable Player) list for this fight.

        Also increments the LVP count for each player in the global dictionary.

        Args:
            players: List of player indices to mark as LVP
        """
        self.lvp_accounts = [self.get_player_account(i) for i in players]

        for i in players:
            account = self.get_player_account(i)
            player = ALL_PLAYERS.get(account)
            if player:
                player.lvps += 1

    def get_lvp_cc_boss(self) -> Optional[str]:
        """
        Identifies and penalizes players with the worst contribution to boss control (CC).

        Finds the players who contributed the maximum CC value on the main boss,
        adds them to the LVP list, and generates a formatted message for the report.

        Returns:
            Formatted message for the report, or None if no CC was done
        """
        # Get players with the maximum CC contribution
        i_players, max_cc, total_cc = Analyzer.get_max_value(self.player_list, self.get_cc_boss)

        # If no players did CC, do not generate a message
        if total_cc == 0:
            return None

        # Add these players to the LVP list
        self.add_lvps(i_players)

        # Prepare variables for the message
        lvp_names = self.players_to_string(i_players)
        cc_ratio = max_cc / total_cc * 100

        # Generate the message
        return language_config.selected_language["LVP BOSS CC"].format(lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)

    def get_lvp_cc_total(self) -> Optional[str]:
        """
        Identifies and penalizes players with the worst contribution to total control (CC).

        Finds the players who contributed the maximum CC value in total (boss + adds),
        adds them to the LVP list, and generates a formatted message for the report.

        Returns:
            Formatted message for the report, or None if no CC was done
        """
        # Get players with the maximum total CC contribution
        i_players, max_cc, total_cc = Analyzer.get_max_value(self.player_list, self.get_cc_total)

        # If no players did CC, do not generate a message
        if total_cc == 0:
            return None

        # Add these players to the LVP list
        self.add_lvps(i_players)

        # Prepare variables for the message
        lvp_names = self.players_to_string(i_players)
        cc_ratio = max_cc / total_cc * 100

        # Generate the message
        return language_config.selected_language["LVP TOTAL CC"].format(lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)

    def get_lvp_dps(self) -> str:
        """
        Identifies and penalizes players with the worst damage contribution.

        Finds the players who dealt the most damage to the boss,
        adds them to the LVP list, and generates a formatted message for the report.
        This method also checks if the player frequently changed food,
        which could explain their poor performance.

        Returns:
            Formatted message for the report
        """
        # Get players with the maximum damage
        i_players, max_dmg, total_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)

        # Calculate additional statistics
        dmg_ratio = max_dmg / total_dmg * 100 if total_dmg > 0 else 0
        lvp_dps_name = self.players_to_string(i_players)
        dps = max_dmg / self.duration_ms if self.duration_ms > 0 else 0

        # Check for food changes
        food_swap_count = self.get_foodswap_count(i_players[0]) if i_players else 0

        # Add these players to the LVP list
        self.add_lvps(i_players)

        if food_swap_count:
            return language_config.selected_language["LVP DPS FOODSWAP"].format(
                lvp_dps_name=lvp_dps_name,
                max_dmg=max_dmg,
                dmg_ratio=dmg_ratio,
                dps=dps,
                foodSwapCount=food_swap_count
            )
        else:
            return language_config.selected_language["LVP DPS"].format(
                lvp_dps_name=lvp_dps_name,
                max_dmg=max_dmg,
                dmg_ratio=dmg_ratio,
                dps=dps
            )