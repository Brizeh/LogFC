from typing import Optional

from core.models.boss_player_info import PlayerInfoMixin


class PlayerGameplayMixin(PlayerInfoMixin):


    def is_condi(self, i_player: int) -> bool:
        """
        Checks if the player is playing a condition damage build.

        A player is considered condi if their condition damage is higher
        than their direct damage.

        Args:
            i_player: Index of the player to check

        Returns:
            True if the player is condi, False otherwise
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return False

        dps_all = players[i_player].get('dpsAll', [{}])
        if not dps_all:
            return False

        power_dmg = dps_all[0].get('powerDamage', 0)
        condi_dmg = dps_all[0].get('condiDamage', 0)

        return condi_dmg > power_dmg

    def is_power(self, i_player: int) -> bool:
        """
        Checks if the player is playing a power damage build.

        Args:
            i_player: Index of the player to check

        Returns:
            True if the player is power, False otherwise
        """
        return not self.is_condi(i_player)

    def is_dead(self, i_player: int) -> bool:
        """
        Checks if the player died during the encounter.

        Args:
            i_player: Index of the player to check

        Returns:
            True if the player died, False otherwise
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return False

        defenses = players[i_player].get('defenses', [{}])
        if not defenses:
            return False

        return defenses[0].get('deadCount', 0) > 0

    def is_buff_up(self, i_player: int, target_time: int, buff_name: str) -> bool:
        """
        Checks if a specific buff was active on a player at a given time.

        Args:
            i_player: Index of the player to check
            target_time: Time (in ms) at which to check the buff
            buff_name: Name of the buff to check

        Returns:
            True if the buff was active, False otherwise
        """
        # Get the players list and validate player index
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return False

        # Find the buff ID based on its name using dictionary comprehension
        buffmap = self.log.pjcontent.get('buffMap', {})
        buff_id = next((int(id_str[1:]) for id_str, buff in buffmap.items()
                        if buff.get('name') == buff_name and id_str.startswith('b')), None)

        if buff_id is None:
            return False

        # Find the buff data for this player using a generator expression
        buffs = players[i_player].get('buffUptimes', [])
        buff_data = next((buff.get('states', []) for buff in buffs
                          if buff.get('id') == buff_id), None)

        if not buff_data or not buff_data:
            return False

        # Find the most recent buff state at or before the target time
        # Use binary search for efficiency when dealing with large datasets
        left, right = 0, len(buff_data) - 1
        closest_index = None

        while left <= right:
            mid = (left + right) // 2
            mid_time = buff_data[mid][0]

            if mid_time <= target_time:
                closest_index = mid
                left = mid + 1
            else:
                right = mid - 1

        # If no state is found before target_time, the buff was not active
        if closest_index is None:
            return False

        # Return the state value (1 = active, 0 = inactive)
        return bool(buff_data[closest_index][1])

    def is_dead_instant(self, i_player: int) -> bool:
        """
        Checks if the player died instantly (without being knocked down first).

        A player is considered to have died instantly if:
        - They died without being knocked down first
        - They were knocked down but died more than 8 seconds later

        Args:
            i_player: Index of the player to check

        Returns:
            True if the player died instantly, False otherwise
        """
        downs_deaths = self.get_player_mech_history(i_player, ["Downed", "Dead"])

        if not downs_deaths:
            return False

        # Check if the last event was a death
        if downs_deaths[-1].get('name') == "Dead":
            # Died without being knocked down
            if len(downs_deaths) == 1:
                return True

            # Died long after being knocked down
            if len(downs_deaths) > 1:
                time_diff = downs_deaths[-1].get('time', 0) - downs_deaths[-2].get('time', 0)
                if time_diff > self.INSTANT_DEATH_TIME_DIFF:
                    return True

        return False

    def get_player_death_timer(self, i_player: int) -> Optional[int]:
        """
        Retrieves the moment when the player died during the fight.

        Args:
            i_player: Player index

        Returns:
            Death time in ms since start of the fight, or None if not dead
        """
        if not self.is_dead(i_player):
            return None

        mech_history = self.get_player_mech_history(i_player, ["Dead"])

        if mech_history:
            return mech_history[-1].get('time')

        return None
