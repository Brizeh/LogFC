from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class WOJ(Boss):
    """
    Voice of the Fallen (WOJ)
    """

    last = None
    name = "WOJ"
    boss_id = 22711
    wing = "IBS"

    def __init__(self, log: Log):
        """
        Initializes an instance of Voice of the Fallen (WOJ).

        Args:
            log (Log): Object containing the combat log data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        WOJ.last = self

    def get_mvp(self):
        """
        Retrieves the message for the most effective player.
        First checks chain damage, then players with poor DPS.

        Returns:
            str: Message for the most effective player or None
        """
        msg_chains = self.get_chain_mvp()
        if msg_chains:
            return msg_chains
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return None

    def get_lvp(self):
        """
        Retrieves the message for the player with the most damage.

        Returns:
            str: Message for the player with the most damage
        """
        return self.get_lvp_dps()

    def get_chain_mvp(self):
        """
        Determines the MVP based on chain damage taken.

        Returns:
            str: Formatted message for the chain MVP or None
        """
        i_players, max_dmg, tot_dmg = Analyzer.get_max_value(self.player_list, self.get_chain_damage)
        mvp_name = self.players_to_string(i_players)
        ratio = max_dmg / tot_dmg * 100
        self.add_mvps(i_players)

        if max_dmg > 10000:
            return language_config.selected_language["WOJ MVP CHAINS"].format(
                mvp_name=mvp_name, max_dmg=max_dmg, ratio=ratio
            )
        return None

    def get_chain_damage(self, i_player: int):
        """
        Retrieves the damage taken by a player from chains.

        Args:
            i_player (int): Player index in the data

        Returns:
            int: Total damage taken from chains
        """
        chain_id = 59159
        dmgTaken = self.log.pjcontent['players'][i_player]["totalDamageTaken"][0]
        for dmg in dmgTaken:
            if dmg["id"] == chain_id:
                return dmg["totalDamage"]
        return 0