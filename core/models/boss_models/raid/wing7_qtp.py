from core.models.boss import Boss


class QTP(Boss):
    """
    Qadim the Peerless (QTP)
    """

    last = None
    name = "QTP"
    wing = 7
    boss_id = 22000

    def __init__(self, log):
        """
        Initializes a QTP instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        QTP.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the QTP fight.

        First checks players with low DPS (excluding pylon players),
        then those with low CC (also excluding pylon players).

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
        """
        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_pylon])
        if msg_bad_dps:
            return msg_bad_dps

        msg_cc = self.get_mvp_cc_total(extra_exclude=[self.is_pylon])
        if msg_cc:
            return msg_cc

        return None

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the QTP fight.

        First checks players with high CC, then those with high DPS.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        msg_cc = self.get_lvp_cc_total()
        if msg_cc:
            return msg_cc

        return self.get_lvp_dps()

    def is_alac(self, i_player: int):
        """
        Checks if a player provides enough alacrity to their subgroup.

        This method takes into account the number of pylon players
        in the subgroup to adjust the alacrity generation requirement.

        Args:
            i_player (int): Index of the player to check

        Returns:
            bool: True if the player provides enough alacrity, False otherwise
        """
        min_alac_contrib = 30
        alac_id = 30328
        boon_path = self.log.pjcontent['players'][i_player].get("groupBuffsActive")
        player_alac_contrib = 0
        pylon_players_in_sub = []

        if boon_path:
            for boon in boon_path:
                if boon["id"] == alac_id:
                    player_alac_contrib = boon["buffData"][self.real_phase_id]["generation"]
            pylon_players_in_sub = [i for i in self.player_list if
                                    self.is_pylon(i) and self.get_player_group(i_player) == self.get_player_group(i)]

        corrected_uptime = player_alac_contrib * 5 / (4 - len(pylon_players_in_sub))
        return corrected_uptime >= min_alac_contrib

    def is_quick(self, i_player: int):
        """
        Checks if a player provides enough quickness to their subgroup.

        This method takes into account the number of pylon players
        in the subgroup to adjust the quickness generation requirement.

        Args:
            i_player (int): Index of the player to check

        Returns:
            bool: True if the player provides enough quickness, False otherwise
        """
        min_quick_contrib = 30
        quick_id = 1187
        boon_path = self.log.pjcontent['players'][i_player].get("groupBuffsActive")
        player_quick_contrib = 0
        pylon_players_in_sub = []

        if boon_path:
            for boon in boon_path:
                if boon["id"] == quick_id:
                    player_quick_contrib = boon["buffData"][self.real_phase_id]["generation"]
            pylon_players_in_sub = [i for i in self.player_list if
                                    self.is_pylon(i) and self.get_player_group(i_player) == self.get_player_group(i)]

        corrected_uptime = player_quick_contrib * 5 / (4 - len(pylon_players_in_sub))
        return corrected_uptime >= min_quick_contrib

    def get_dps_ranking(self):
        """
        Calculates the DPS ranking of players for QTP excluding supports and pylon players.

        Returns:
            dict: Dictionary associating players with their DPS score
        """
        return self._get_dps_contrib([self.is_support, self.is_pylon])

    ################################ CONDITIONS ################################

    def is_pylon(self, i_player: int):
        """
        Checks if a player is a 'pylon player' (caught more than one orb).

        Args:
            i_player (int): Index of the player to check

        Returns:
            bool: True if the player caught more than one orb, False otherwise
        """
        return self.get_orb_caught(i_player) > 1

    ################################ DATA MECHAS ################################

    def get_orb_caught(self, i_player: int):
        """
        Retrieves the number of orbs (Critical Mass) caught by a player.

        Args:
            i_player (int): Player index

        Returns:
            int: Number of orbs caught
        """
        return self.get_mech_value(i_player, "Critical Mass")