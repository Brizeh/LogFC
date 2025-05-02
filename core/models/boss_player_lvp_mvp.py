from core.models.boss_encounter import BossEncounterMixin
from core.models.boss_player_gameplay import PlayerGameplayMixin
from core.models.boss_player_role import PlayerRoleMixin
from core.models.boss_utils import BossUtilsMixin


class PlayerDamageMixin(PlayerRoleMixin, PlayerGameplayMixin, BossUtilsMixin, BossEncounterMixin):

    def get_dmg_boss(self, i_player: int) -> int:
        """
        Retrieves the damage dealt to the boss by the player.

        Args:
            i_player: Player index

        Returns:
            Damage dealt to the boss
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return 0

        dps_targets = players[i_player].get('dpsTargets', [[]])
        if not dps_targets or not dps_targets[0]:
            return 0

        if self.real_phase_id >= len(dps_targets[0]):
            return 0

        return dps_targets[0][self.real_phase_id].get('damage', 0)