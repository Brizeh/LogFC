from core.models.boss import Boss


class DECIMA(Boss):
    """
    Keeper of Order (Decima)
    """

    last = None
    name = "DECIMA"
    wing = 8
    boss_id = 26774

    def __init__(self, log):
        """
        Initializes a DECIMA instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        DECIMA.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Decima fight.

        For Decima, the MVP is based solely on players with significantly low DPS.

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
        """
        return self.get_bad_dps()

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the Decima fight.

        For Decima, the LVP is based solely on players with high DPS.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        return self.get_lvp_dps()