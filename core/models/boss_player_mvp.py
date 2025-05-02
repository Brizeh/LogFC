from typing import List, Callable, Optional

from config.settings import ALL_PLAYERS
from core.models.boss_player_xvp import PlayerDamageMixin
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class PlayerMvpMixin(PlayerDamageMixin):

    def add_mvps(self, players: List[int]) -> None:
        """
        Adds players to the MVP (Most Valuable Player) list for this fight.

        Also increments the MVP count for each player in the global dictionary.

        Args:
            players: List of player indices to mark as MVP
        """
        self.mvp_accounts = [self.get_player_account(i) for i in players]

        for i in players:
            account = self.get_player_account(i)
            player = ALL_PLAYERS.get(account)
            if player:
                player.mvps += 1

    def get_mvp_cc_boss(self, extra_exclude: List[Callable[[int], bool]] = None) -> Optional[str]:
        """
        Identifies and rewards players with the best contribution to boss control (CC).

        Finds the players who contributed the minimum CC value on the main boss,
        adds them to the MVP list, and generates a formatted message for the report.

        Args:
            extra_exclude: List of additional filtering functions to exclude certain players

        Returns:
            Formatted message for the report, or None if no CC was done
        """
        if extra_exclude is None:
            extra_exclude = []

        # Get players with the minimum CC contribution
        i_players, min_cc, total_cc = Analyzer.get_min_value(self.player_list, self.get_cc_boss, exclude=extra_exclude)

        # If no players did CC, do not generate a message
        if total_cc == 0:
            return None

        # Add these players to the MVP list
        self.add_mvps(i_players)

        # Prepare variables for the message
        mvp_names = self.players_to_string(i_players)
        cc_ratio = min_cc / total_cc * 100
        number_mvp = len(i_players)

        if min_cc == 0:
            if number_mvp == 1:
                return language_config.selected_language["MVP BOSS 0 CC S"].format(mvp_names=mvp_names)
            else:
                return language_config.selected_language["MVP BOSS 0 CC P"].format(mvp_names=mvp_names)
        else:
            if number_mvp == 1:
                return language_config.selected_language["MVP BOSS CC S"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            else:
                return language_config.selected_language["MVP BOSS CC P"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)

    def get_mvp_cc_total(self, extra_exclude: List[Callable[[int], bool]] = None) -> Optional[str]:
        """
        Identifies and rewards players with the best contribution to total control (CC).

        Finds the players who contributed the minimum CC value in total (boss + adds),
        adds them to the MVP list, and generates a formatted message for the report.

        Args:
            extra_exclude: List of additional filtering functions to exclude certain players

        Returns:
            Formatted message for the report, or None if no CC was done
        """
        if extra_exclude is None:
            extra_exclude = []

        # Get players with the minimum total CC contribution
        i_players, min_cc, total_cc = Analyzer.get_min_value(self.player_list, self.get_cc_total, exclude=extra_exclude)

        # If no players did CC, do not generate a message
        if total_cc == 0:
            return None

        # Add these players to the MVP list
        self.add_mvps(i_players)

        # Prepare variables for the message
        mvp_names = self.players_to_string(i_players)
        cc_ratio = min_cc / total_cc * 100
        number_mvp = len(i_players)

        if min_cc == 0:
            if number_mvp == 1:
                return language_config.selected_language["MVP TOTAL 0 CC S"].format(mvp_names=mvp_names)
            else:
                return language_config.selected_language["MVP TOTAL 0 CC P"].format(mvp_names=mvp_names)
        else:
            if number_mvp == 1:
                return language_config.selected_language["MVP TOTAL CC S"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            else:
                return language_config.selected_language["MVP TOTAL CC P"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)

    def get_bad_dps(self, extra_exclude: List[Callable[[int], bool]] = None) -> Optional[str]:
        """
        Identifies DPS players who deal less damage than a support player.

        This method looks for the support players who dealt the most damage,
        then identifies DPS players whose damage is lower than that of the support.
        These DPS players are considered underperforming and are added to the MVP list
        (ironically) to highlight their need for improvement.

        Args:
            extra_exclude: List of additional filtering functions to exclude certain players

        Returns:
            Formatted message for the report, or None if no DPS are underperforming
        """
        if extra_exclude is None:
            extra_exclude = []

        # Find the support player with the highest damage
        i_sup, sup_max_dmg, _ = Analyzer.get_max_value(
            self.player_list,
            self.get_dmg_boss,
            exclude=[self.is_dps, self.is_bannerslave]
        )

        sup_name = self.players_to_string(i_sup)
        bad_dps = []

        # Identify DPS players who deal less damage than the best support
        for i in self.player_list:
            # Exclude players who are not relevant to this analysis
            should_exclude = (
                    (extra_exclude and any(filter_func(i) for filter_func in extra_exclude)) or
                    self.is_dead(i) or
                    self.is_support(i) or
                    self.is_bannerslave(i)
            )

            if should_exclude:
                continue

            dps = self.get_dmg_boss(i)

            # Check if this DPS does less damage than the best support
            if dps < sup_max_dmg:
                # Special exception for Spellbreakers on the QUOIDIMM boss
                if not (self.name == "QUOIDIMM" and self.get_player_spe(i) == "Spellbreaker"):
                    bad_dps.append(i)

        # If there are underperforming DPS, generate a message
        if bad_dps:
            self.add_mvps(bad_dps)
            bad_dps_name = self.players_to_string(bad_dps)

            if len(bad_dps) == 1:
                return language_config.selected_language["MVP BAD DPS S"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)
            else:
                return language_config.selected_language["MVP BAD DPS P"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)

        return None