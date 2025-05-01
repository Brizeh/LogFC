from core.models.boss import Boss


class SABIR(Boss):
    """
    Cardinal Sabir
    """

    last = None
    name = "SABIR"
    wing = 7
    boss_id = 21964

    def __init__(self, log):
        """
        Initializes a SABIR instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SABIR.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Sabir fight.

        For Sabir, the MVP is based solely on players with low CC.

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
        """
        return self.get_mvp_cc_boss()

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the Sabir fight.

        For Sabir, the LVP is based solely on players with high CC.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        return self.get_lvp_cc_boss()