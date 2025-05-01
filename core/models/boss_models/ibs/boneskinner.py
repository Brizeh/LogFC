from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class BONESKINNER(Boss):
    """
    Boneskinner from the Icebrood Saga.
    """

    last = None
    name = "BONESKINNER"
    boss_id = 22521
    wing = "IBS"
    sak_id = 60501

    def __init__(self, log: Log):
        """
        Initializes a Boneskinner instance.

        Args:
            log (Log): Object containing combat log data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        BONESKINNER.last = self

    def get_mvp(self):
        """
        Retrieves the message for the most valuable player.

        Returns:
            str: Message for the top-performing player, or None
        """
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return None

    def get_lvp(self):
        """
        Retrieves the message for the least valuable player.
        First checks for players with SAK stats, then falls back to standard DPS.

        Returns:
            str: Message for the least effective player
        """
        msg_sak = self.get_lvp_sak()
        if msg_sak:
            return msg_sak
        return self.get_lvp_dps()

    def get_lvp_sak(self):
        """
        Calculates LVP based on SAK (Shatter Assault Kill) statistics.

        Returns:
            str: Formatted LVP message based on SAK stats, or None
        """
        i_players, max_dmg, tot_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)
        sak_dmg = self.get_sak_dmg(i_players[0])
        sak_count = self.get_sak_count(i_players[0])
        lvp_dps_name = self.players_to_string(i_players)
        dps = max_dmg / self.duration_ms
        dmg_ratio = max_dmg / tot_dmg * 100
        self.add_lvps(i_players)

        if sak_count:
            sak_ratio = sak_dmg / max_dmg * 100
            return language_config.selected_language["FRAENIR LVP SAK"].format(
                lvp_dps_name=lvp_dps_name,
                sak_count=sak_count,
                sak_ratio=sak_ratio,
                dps=dps,
                dmg_ratio=dmg_ratio
            )
        return None

    def get_sak_dmg(self, i_player: int):
        """
        Retrieves the damage dealt by the Shatter Assault Kill attack.

        Args:
            i_player (int): Index of the player in the data

        Returns:
            int: Total damage dealt with SAK
        """
        dmgPath = self.log.pjcontent["players"][i_player]["targetDamageDist"][0][0]
        for dmg in dmgPath:
            if dmg["id"] == BONESKINNER.sak_id:
                return dmg["totalDamage"]
        return 0

    def get_sak_count(self, i_player: int):
        """
        Retrieves the number of times the Shatter Assault Kill attack was used.

        Args:
            i_player (int): Index of the player in the data

        Returns:
            int: Number of SAK usages
        """
        rota = self.get_player_rotation(i_player)
        for spell in rota:
            if spell["id"] == BONESKINNER.sak_id:
                return len(spell["skills"])
        return 0
