from core.models.boss import Boss


class CA(Boss):
    """
    Conjured Amalgamate (CA)
    """

    last = None
    name = "CA"
    wing = 6
    boss_id = 43974

    def __init__(self, log):
        """
        Initializes a CA instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        CA.last = self

    def get_mvp(self):
        """
        Determines the MVP (Most Valuable Player) for the Conjured Amalgamate fight.

        For CA, the MVP is based solely on players with significantly low DPS.

        Returns:
            str: Formatted message indicating the MVP and reason, or None if no MVP
        """
        return self.get_bad_dps()

    def get_lvp(self):
        """
        Determines the LVP (Least Valuable Player) for the Conjured Amalgamate fight.

        Returns:
            str: Formatted message indicating the LVP and reason, or None if no LVP
        """
        return self.get_lvp_dps()

    ################################ MVP ################################

    ################################ LVP ################################

    ################################ CONDITIONS ################################

    ################################ DATA MECHAS ################################
