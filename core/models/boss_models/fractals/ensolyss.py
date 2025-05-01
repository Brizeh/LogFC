from core.models.boss import Boss
from core.models.log import Log


class ENSOLYSS(Boss):
    """
    ENSOLYSS from fractals.
    """

    last = None
    name = "ENSOLYSS"
    boss_id = 16948
    wing = "FRAC"

    def __init__(self, log: Log):
        """
        Initializes an instance of ENSOLYSS.

        Args:
            log (Log): Object containing the combat log data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        ENSOLYSS.last = self

    def get_mvp(self):
        """
        Retrieves the message for the most valuable player.

        Returns:
            str: Message for the top-performing player or None
        """
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return None

    def get_lvp(self):
        """
        Retrieves the message for the player with the most damage.

        Returns:
            str: Message for the least valuable player
        """
        return self.get_lvp_dps()
