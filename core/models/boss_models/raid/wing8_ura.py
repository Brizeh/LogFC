from core.models.boss import Boss


class URA(Boss):
    """
    Keeper of Chaos (Ura) from the eighth raid wing.
    """

    last = None
    name = "URA"
    wing = 8
    boss_id = 26712

    def __init__(self, log):
        """
        Initializes a URA instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        URA.last = self  # Correction of the variable used (GREER.last → URA.last)

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Ura fight.

        For Ura, the MVP is based solely on players with significantly low DPS.

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
        """
        return self.get_bad_dps()

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the Ura fight.

        For Ura, the LVP is based solely on players with high DPS.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        return self.get_lvp_dps()