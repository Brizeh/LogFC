from core.models.boss import Boss


class HT(Boss):
    """
    Harvest Temple (HT) from End of Dragons.
    """

    last = None
    name = "HT"
    boss_id = 24375
    wing = "EOD"

    def __init__(self, log):
        """
        Initializes an instance of HT with a specific log.

        Args:
            log: The Log object containing combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        HT.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the fight against Harvest Temple.

        For Harvest Temple, the MVP is based only on players with significantly low DPS.

        Returns:
            str: Formatted message indicating the MVP and the reason, or None if no MVP
        """
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the fight against Harvest Temple.

        Returns:
            str: Formatted message indicating the LVP and the reason, or None if no LVP
        """
        return self.get_lvp_dps()
