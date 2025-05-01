from core.models.boss import Boss


class XJ(Boss):
    """
    Ankka from End of Dragons.
    """

    last = None
    name = "ANKKA"
    boss_id = 23957
    wing = "EOD"

    def __init__(self, log):
        """
        Initializes an instance of XJ with a specific log.

        Args:
            log: The Log object containing combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        XJ.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the fight against Ankka.

        First checks players with low CC, then those with significantly low DPS.

        Returns:
            str: Formatted message indicating the MVP and the reason, or None if no MVP
        """
        msg_cc = self.get_mvp_cc_total()
        if msg_cc:
            return msg_cc

        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the fight against Ankka.

        Returns:
            str: Formatted message indicating the LVP and the reason, or None if no LVP
        """
        return self.get_lvp_dps()
