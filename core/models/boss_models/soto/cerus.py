from core.models.boss import Boss
from core.models.log import Log


class CERUS(Boss):
    """
    Cerus from Secrets of the Obscure.
    """

    last = None
    name = "CERUS"
    boss_id = 25989
    wing = "SOTO"

    def __init__(self, log: Log):
        """
        Initializes a Cerus instance.

        Args:
            log (Log): Object containing the combat log data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        CERUS.last = self  # Correction from DAGDA.last to CERUS.last

    def get_mvp(self):
        """
        Retrieves the message for the best performing player.

        Returns:
            str: Message for the best performing player or None
        """
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