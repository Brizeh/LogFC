from core.models.boss import Boss


class GREER(Boss):
    """
    Voice of the Fallen (Greer)
    """

    last = None
    name = "GREER"
    wing = 8
    boss_id = 26725

    def __init__(self, log):
        """
        Initializes a GREER instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        GREER.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Greer fight.

        For Greer, the MVP is based solely on players with significantly low DPS.

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
        """
        return self.get_bad_dps()

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the Greer fight.

        For Greer, the LVP is based solely on players with high DPS.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        return self.get_lvp_dps()