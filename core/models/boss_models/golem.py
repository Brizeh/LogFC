"""
Module containing the GOLEM class for analyzing training Golem boss logs.
"""

from core.models.boss import Boss


class GOLEM(Boss):
    """
    Training Golem.
    """

    last = None
    name = "GOLEM CHAT STANDARD"
    boss_id = 16199

    def __init__(self, log):
        """
        Initializes a GOLEM instance with a specific log.

        Args:
            log: The Log object containing the combat data
        """
        super().__init__(log)
        GOLEM.last = self