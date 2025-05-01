from typing import Optional, List, ClassVar

from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class GORS(Boss):
    """
    Gorseval
    """

    # Class attributes
    last: Optional['GORS'] = None  # Reference to the last created instance
    name: ClassVar[str] = "GORSEVAL"
    wing: ClassVar[int] = 1
    boss_id: ClassVar[int] = 15429
    real_phase: ClassVar[str] = "Full Fight"

    def __init__(self, log: Log) -> None:
        """
        Initializes a Gorseval object.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        GORS.last = self  # Updates the reference to the last instance

    def get_mvp(self) -> Optional[str]:
        """
        Determines the MVP player for Gorseval.
        Priority: egged players > damage in split phases > bad DPS

        Returns:
            MVP reward message or None if no player stands out
        """
        # First, check if players have been "egged"
        msg_egg = self.mvp_egg()
        if msg_egg:
            return msg_egg

        # Then, check for damage in split phases
        msg_dmg_split = self.mvp_dmg_split()
        if msg_dmg_split:
            return msg_dmg_split

        # Finally, check for underperforming DPS
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self) -> str:
        """
        Determines the LVP player for Gorseval, based on damage in split phases.

        Returns:
            LVP penalty message
        """
        return self.lvp_dmg_split()

    ################################ MVP ################################

    def mvp_dmg_split(self) -> Optional[str]:
        """
        Identifies players who did the least damage during split phases.
        These players are considered MVP because they focused on mechanics.

        Returns:
            MVP message for good damage during split phases or None if no one stands out
        """
        # Get the players who did the least damage during the split phases
        i_players, min_dmg, total_dmg = Analyzer.get_min_value(
            self.player_list,
            self.get_dmg_split,
            exclude=[self.is_support]
        )

        # Calculate the total damage from DPS players
        dps_total_dmg = Analyzer.get_tot_value(
            self.player_list,
            self.get_dmg_split,
            exclude=[self.is_support]
        )

        # If the damage is significantly low (less than 75% of the expected share)
        if min_dmg / dps_total_dmg < 1 / 6 * 0.75:
            # Add these players to the MVP list
            self.add_mvps(i_players)

            # Prepare the variables for the message
            mvp_names = self.players_to_string(i_players)
            dmg_ratio = min_dmg / total_dmg * 100

            # Generate the message
            return language_config.selected_language["GORS MVP SPLIT"].format(
                mvp_names=mvp_names,
                min_dmg=min_dmg,
                dmg_ratio=dmg_ratio
            )

        return None

    def mvp_egg(self) -> Optional[str]:
        """
        Identifies players who were "egged" during the fight.
        This mechanic is important and deserves recognition.

        Returns:
            MVP message for egged players or None if no one was egged
        """
        # Get the list of players who were "egged"
        i_players = self.get_egged()

        if i_players:
            # Add these players to the MVP list
            self.add_mvps(i_players)

            # Prepare the message
            mvp_names = self.players_to_string(i_players)

            # Select the appropriate message based on the number of players
            if len(i_players) == 1:
                return language_config.selected_language["GORS MVP EGG S"].format(mvp_names=mvp_names)
            else:
                return language_config.selected_language["GORS MVP EGG P"].format(mvp_names=mvp_names)

        return None

    ################################ LVP ################################

    def lvp_dmg_split(self) -> str:
        """
        Identifies players who did the most damage during split phases.
        These players are considered LVP because they focused on damage
        at the expense of mechanics.

        Returns:
            LVP message for players with the highest damage during split phases
        """
        # Get the players who did the most damage during the split phases
        i_players, max_dmg, total_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_split)

        # Prepare the variables for the message
        lvp_names = self.players_to_string(i_players)
        dmg_ratio = max_dmg / total_dmg * 100

        # Add these players to the LVP list
        self.add_lvps(i_players)

        # Generate the message
        return language_config.selected_language["GORS LVP SPLIT"].format(
            lvp_names=lvp_names,
            max_dmg=max_dmg,
            dmg_ratio=dmg_ratio
        )

    ################################ CONDITIONS ###############################

    def got_egged(self, i_player: int) -> bool:
        """
        Checks if a player was affected by the "Egged" mechanic.

        Args:
            i_player: Player index

        Returns:
            True if the player was affected by the mechanic, False otherwise
        """
        return self.get_mech_value(i_player, "Egged") > 0

    ################################ DATA MECHAS ################################

    def get_dmg_split(self, i_player: int) -> int:
        """
        Calculates the total damage done by a player during split phases.

        Args:
            i_player: Player index

        Returns:
            Total damage done during split phases
        """
        dmg_split = 0

        try:
            # Get the damage stats for the two split phases
            dmg_split_1 = self.log.jcontent['phases'][3]['dpsStatsTargets'][i_player]
            dmg_split_2 = self.log.jcontent['phases'][6]['dpsStatsTargets'][i_player]

            # Add up the damage from all targets in both phases
            for add_split1, add_split2 in zip(dmg_split_1, dmg_split_2):
                dmg_split += add_split1[0] + add_split2[0]

        except (IndexError, KeyError, TypeError):
            # Handle errors accessing data
            return 0

        return dmg_split

    def get_egged(self) -> List[int]:
        """
        Identifies all players affected by the "Egg" mechanic.

        Returns:
            List of indices of players who were egged
        """
        egged = []

        for i in self.player_list:
            if self.got_egged(i):
                egged.append(i)

        return egged
