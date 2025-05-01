from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class KANAXAI(Boss):
    """
    KANAXAI from fractals.
    """

    last = None
    name = "KANAXAI"
    boss_id = 25577
    wing = "FRAC"

    def __init__(self, log: Log):
        """
        Initializes an instance of KANAXAI.

        Args:
            log (Log): Object containing the combat log data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        KANAXAI.last = self

    def get_mvp(self):
        """
        Retrieves the message for the most valuable player.

        Returns:
            str: Message for the top-performing player or None
        """
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return None

    def get_lvp(self):
        """
        Retrieves the message for the player with the most damage.

        Returns:
            str: Message for the player with the most damage specific to KANAXAI
        """
        return self.get_lvp_dps()

    def get_lvp_dps(self):
        """
        Retrieves the specific message for the player with the most damage on KANAXAI.
        Includes the number of links if present.

        Returns:
            str: Formatted message for the player with the most damage
        """
        i_players, max_dmg, tot_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)
        lvp_dps_name = self.players_to_string(i_players)
        link_count = self.get_links(i_players[0])
        dmg_ratio = max_dmg / tot_dmg * 100
        dps = max_dmg / self.duration_ms

        if link_count:
            return language_config.selected_language["KANAXAI LVP DPS"].format(
                lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps, linkCount=link_count
            )
        else:
            return language_config.selected_language["LVP DPS"].format(
                lvp_dps_name=lvp_dps_name, dmg_ratio=dmg_ratio, dps=dps
            )

    def get_links(self, i_player: int):
        """
        Calculates the number of links for a specific player during combat phases.

        Args:
            i_player (int): Index of the player to analyze

        Returns:
            int: Number of links detected
        """
        link_id = 69206
        start1, end1 = self.get_phase_timers("Phase 1", in_milliseconds=True)
        start2, end2 = self.get_phase_timers("Phase 2", in_milliseconds=True)
        start3, end3 = self.get_phase_timers("Phase 3", in_milliseconds=True)
        buff_uptimes = self.log.pjcontent["players"][i_player]["buffUptimes"]
        link_count = 0

        # Adjust phase timings
        start2 += 8000
        start3 += 8000
        end1 -= 8000
        end2 -= 8000

        for buff in buff_uptimes:
            if buff["id"] == link_id:
                for state in buff["states"]:
                    buff_time = state[0]
                    if (
                            state[1] == 1 and
                            ((buff_time > start1 and buff_time < end1) or
                             (buff_time > start2 and buff_time < end2) or
                             (buff_time > start3 and buff_time < end3))
                    ):
                        link_count += 1

        return link_count
