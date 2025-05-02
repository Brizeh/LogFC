from datetime import datetime
from typing import ClassVar, List

import pytz

from core.models.boss_boons import BoonsMixin


class PlayerRoleMixin(BoonsMixin):

    # Threshold values
    MIN_QUICK_CONTRIB: ClassVar[float] = 30
    MIN_ALAC_CONTRIB: ClassVar[float] = 30
    BUYER_DEATH_THRESHOLD: ClassVar[int] = 20000  # ms
    INSTANT_DEATH_TIME_DIFF: ClassVar[int] = 8000  # ms

    # Constants for buff and mechanic IDs
    BANNER_IDS: ClassVar[List[int]] = [14449, 14417]


    def is_quick(self, i_player: int) -> bool:
        """
        Checks if the player provides sufficient quickness uptime.

        A player is considered a quickness provider if they generate
        at least MIN_QUICK_CONTRIB % uptime during the main phase.

        Args:
            i_player: Index of the player to check

        Returns:
            True if the player provides quickness, False otherwise
        """
        return self.quickness(i_player) >= self.MIN_QUICK_CONTRIB

    def is_alac(self, i_player: int) -> bool:
        """
        Checks if the player provides sufficient alacrity uptime.

        A player is considered an alacrity provider if they generate
        at least MIN_ALAC_CONTRIB % uptime during the main phase.

        Args:
            i_player: Index of the player to check

        Returns:
            True if the player provides alacrity, False otherwise
        """
        return self.alacrity(i_player) >= self.MIN_ALAC_CONTRIB

    def is_support(self, i_player: int) -> bool:
        """
        Checks if the player is playing a support role.

        A player is considered support if they:
        - Provide quickness
        - Provide alacrity
        - Are a Druid (before the 07/17/2022 patch)
        - Are a Bannerslave (before the 07/17/2022 patch)

        Args:
            i_player: Index of the player to check

        Returns:
            True if the player is support, False otherwise
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return False

        prof = players[i_player].get('profession', '')

        is_druid_supp = False
        pre_patch_date = datetime(2022, 7, 17, 23, 0, 0, tzinfo=pytz.FixedOffset(60))
        if prof == "Druid" and self.start_date < pre_patch_date:
            is_druid_supp = True

        return (self.is_quick(i_player) or
                self.is_alac(i_player) or
                is_druid_supp or
                self.is_bannerslave(i_player))

    def is_bannerslave(self, i_player: int) -> bool:
        """
        Checks if the player is playing a Warrior/Berserker bannerslave.

        This is only applicable before the patch on 17/07/2022.

        Args:
            i_player: Index of the player to check

        Returns:
            True if the player is bannerslave, False otherwise
        """
        pre_patch_date = datetime(2022, 7, 17, 23, 0, 0, tzinfo=pytz.FixedOffset(60))

        # Check if the combat took place before the patch
        if self.start_date >= pre_patch_date:
            return False

        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return False

        prof = players[i_player].get('profession', '')

        # Check if the player is a Warrior/Berserker
        if prof not in ["Warrior", "Berserker"]:
            return False

        # Check if they provided banner buffs
        group_buffs = players[i_player].get('groupBuffs', [])
        for buff in group_buffs:
            if buff.get('id') in self.BANNER_IDS:
                return True

        return False

    def is_dps(self, i_player: int) -> bool:
        """
        Checks if the player is playing a DPS (damage) role.

        A player is considered DPS if they are not a support.

        Args:
            i_player: Index of the player to check

        Returns:
            True if the player is a DPS, False otherwise
        """
        return not self.is_support(i_player)

    def is_tank(self, i_player: int) -> bool:
        """
        Checks if the player is playing a tank role.

        A player is considered a tank if they have toughness.

        Args:
            i_player: Index of the player to check

        Returns:
            True if the player is a tank, False otherwise
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return False

        return players[i_player].get('toughness', 0) > 0

    def is_heal(self, i_player: int) -> bool:
        """
        Checks if the player is playing a healer role.

        A player is considered a healer if they have healing power.

        Args:
            i_player: Index of the player to check

        Returns:
            True if the player is a healer, False otherwise
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return False

        return players[i_player].get('healing', 0) > 0