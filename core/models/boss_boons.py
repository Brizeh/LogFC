from typing import ClassVar

from core.models.boss_encounter import BossEncounterMixin


class BoonsMixin(BossEncounterMixin):
    """
    Mixin pour les fonctionnalités liées aux bonus.
    Hérite de DataAccessMixin pour l'accès aux données.
    """

    # Constants for buff and mechanic IDs
    ALAC_ID: ClassVar[int] = 30328
    QUICK_ID: ClassVar[int] = 1187

    def quickness(self, i_player: int) -> int:
        return self.get_boon_value(i_player, self.QUICK_ID)

    def alacrity(self, i_player: int) -> int:
        return self.get_boon_value(i_player, self.ALAC_ID)

    def get_boon_value(self, i_player: int, boon_id: int) -> int:
        boon_path = self.log.pjcontent.get('players', [])[i_player].get("groupBuffsActive", [])
        player_quick_contrib = 0

        if boon_path:
            for boon in boon_path:
                if boon.get("id") == boon_id:
                    buff_data = boon.get("buffData", {})
                    if self.real_phase_id in buff_data:
                        player_quick_contrib = buff_data[self.real_phase_id].get("generation", 0)
                    break
        return player_quick_contrib
        # players = self.log.pjcontent.get('players', [])
        #
        # # Check to avoid IndexError
        # if i_player >= len(players):
        #     return 0
        #
        # # Boons information for the current player
        # boon_path = players[i_player].get("groupBuffsActive", [])
        #
        # # Look for the boon
        # boon = next((boon for boon in boon_path if boon.get("id") == boon_id), None)
        #
        # if boon:
        #     buff_data = boon.get("buffData", {})
        #     return buff_data.get(self.real_phase_id, {}).get("generation", 0)
        #
        # return 0