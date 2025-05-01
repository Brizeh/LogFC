from core.models.boss import Boss
from core.models.log import Log


class ICE(Boss):
    """
    Icebrood Construct from the Icebrood Saga.
    """

    last = None
    name = "ICEBROOD"
    boss_id = 22154
    wing = "IBS"

    def __init__(self, log: Log):
        """
        Initializes an instance of Icebrood Construct.

        Args:
            log (Log): Object containing the combat log data
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        ICE.last = self

    def get_mvp(self):
        """
        Retrieves the message for the most effective player.

        Returns:
            str: Message for the most effective player or None
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