from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable, Tuple, ClassVar, TypeVar

import pytz

from config.settings import BOSS_DICT, CUSTOM_NAMES, ALL_PLAYERS, DATE_FORMAT, PARIS_TIMEZONE
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config
from utils.formatters import time_to_index

# Type for player filtering functions
PlayerFilter = Callable[[int], bool]
# Type for the return values of get_value functions
T = TypeVar('T', int, float)

class Boss:
    """
    Base class representing a boss encounter in Guild Wars 2.

    This class encapsulates common logic for all boss encounters,
    including log parsing, player tracking, and performance evaluation.

    Attributes:
        name (str): Boss name (must be defined by subclasses)
        wing (int): Wing number where the boss is located (for raids)
        boss_id (int): Unique identifier of the boss in the game
        real_phase (str): Main phase to analyze for statistics
    """

    # Default class attributes, meant to be overridden in subclasses
    name: ClassVar[Optional[str]] = None
    wing: ClassVar[int] = 0
    boss_id: ClassVar[int] = -1
    real_phase: ClassVar[str] = "Full Fight"

    # Constants for buff and mechanic IDs
    QUICK_ID: ClassVar[int] = 1187
    ALAC_ID: ClassVar[int] = 30328
    BANNER_IDS: ClassVar[List[int]] = [14449, 14417]
    FOOD_SWAP_ICON: ClassVar[str] = "https://wiki.guildwars2.com/images/d/d6/Champion_of_the_Crown.png"

    # Threshold values
    MIN_QUICK_CONTRIB: ClassVar[float] = 30
    MIN_ALAC_CONTRIB: ClassVar[float] = 30
    BUYER_DEATH_THRESHOLD: ClassVar[int] = 20000  # ms
    INSTANT_DEATH_TIME_DIFF: ClassVar[int] = 8000  # ms

    def __init__(self, log: Log) -> None:
        """
        Initializes a boss encounter from a Log object.

        Args:
            log: The Log object containing the encounter data
        """
        self.log: Log = log
        self.cm: bool = self.is_cm()
        self.logName: str = self.get_log_name()
        self.mechanics: List[Dict[str, Any]] = self.get_mechanics()
        self.duration_ms: int = self.get_duration_ms()
        self.start_date: datetime = self.get_start_date()
        self.end_date: datetime = self.get_end_date()
        self.player_list: List[int] = self.get_player_list()
        self.wingman_time: Optional[List[int]] = self.get_wingman_time()
        self.wingman_percentile: Optional[float] = self.get_wingman_percentile()
        self.real_phase_id: int = self.get_phase_id(self.real_phase)
        self.time_base: int = self.get_time_base()

        # Lists to track MVP and LVP players
        self.mvp_accounts: List[str] = []
        self.lvp_accounts: List[str] = []

        # Initialize players in the global dictionary
        self._initialize_players()

    def _initialize_players(self) -> None:
        """
        Initializes the players involved in this encounter in the global dictionary.

        For each player, if they already exist in the ALL_PLAYERS dictionary,
        add this boss to their history. Otherwise, create a new player.
        """
        for i in self.player_list:
            account = self.get_player_account(i)
            player = ALL_PLAYERS.get(account)

            if not player:
                # Create a new player if not already present
                from core.models.player import Player
                new_player = Player(self, account)
                ALL_PLAYERS[account] = new_player
            else:
                # Add this boss to the player's history
                player.add_boss(self)

    def __repr__(self) -> str:
        """
        String representation of the boss for debugging.

        Returns:
            Log URL
        """
        return self.log.url

    # -------------------------------------------------------------------------
    # Methods to retrieve boss attributes
    # -------------------------------------------------------------------------

    def is_cm(self) -> bool:
        """
        Determines whether this encounter is in challenge mode (CM).

        Returns:
            True if the fight is in CM, False otherwise
        """
        return self.log.pjcontent.get('isCM', False)

    def get_log_name(self) -> str:
        """
        Retrieves the official name of the encounter from the log.

        Returns:
            Name of the encounter
        """
        return self.log.pjcontent.get('fightName', 'Unknown')

    def get_mechanics(self) -> List[Dict[str, Any]]:
        """
        Retrieves the player-related mechanics of the fight.

        Returns:
            List of mechanics affecting players during the fight
        """
        mechanics = []
        mechanic_map = self.log.jcontent.get('mechanicMap', [])

        for mechanic in mechanic_map:
            is_player_mechanic = mechanic.get('playerMech', False)
            if is_player_mechanic:
                mechanics.append(mechanic)

        return mechanics

    def get_duration_ms(self) -> int:
        """
        Retrieves the total duration of the fight in milliseconds.

        Returns:
            Duration of the fight in ms
        """
        return self.log.pjcontent.get('durationMS', 0)

    def get_start_date(self) -> datetime:
        """
        Retrieves the start date and time of the fight.

        Converts the start timestamp to a datetime object,
        and adjusts it to the Paris timezone.

        Returns:
            Datetime in Paris timezone
        """
        start_date_text = self.log.pjcontent.get('timeStartStd', '')
        if not start_date_text:
            return datetime.now(PARIS_TIMEZONE)

        try:
            start_date = datetime.strptime(start_date_text, DATE_FORMAT)
            return start_date.astimezone(PARIS_TIMEZONE)
        except ValueError:
            # In case of parsing error
            return datetime.now(PARIS_TIMEZONE)

    def get_end_date(self) -> datetime:
        """
        Retrieves the end date and time of the fight.

        Converts the end timestamp to a datetime object,
        and adjusts it to the Paris timezone.

        Returns:
            Datetime in Paris timezone
        """
        end_date_text = self.log.pjcontent.get('timeEndStd', '')
        if not end_date_text:
            return datetime.now(PARIS_TIMEZONE)

        date_format = "%Y-%m-%d %H:%M:%S %z"
        try:
            end_date = datetime.strptime(end_date_text, date_format)
            return end_date.astimezone(PARIS_TIMEZONE)
        except ValueError:
            # In case of parsing error
            start_date = self.get_start_date()
            return start_date + timedelta(milliseconds=self.duration_ms)

    def get_wingman_time(self) -> Optional[List[int]]:
        """
        Retrieves Wingman reference times for this boss.

        Queries the Wingman API to get median and top benchmark durations
        for this boss, depending on its ID and mode (CM or normal).

        Returns:
            List containing [median_time, top_time] or None if an error occurs
        """
        from services.api.wingman import WingmanAPI
        return WingmanAPI.get_boss_benchmark(self.boss_id, self.cm)

    def get_player_list(self) -> List[int]:
        """
        Retrieves the list of player indices participating in the fight.

        Filters out players in special groups (50+) and those detected as buyers
        (for raid selling purposes).

        Returns:
            List of actual participant player indices
        """
        real_players = []
        players = self.log.pjcontent.get('players', [])

        for i_player, player in enumerate(players):
            if (player.get('group', 0) < 50 and
                    not self.is_buyer(i_player)):
                real_players.append(i_player)

        return real_players

    def get_wingman_percentile(self) -> Optional[float]:
        """
        Retrieves the Wingman percentile for this fight.

        Queries the Wingman API to get the percentile of the current fight
        compared to global statistics for this boss.

        Returns:
            Fight percentile or None if not available
        """
        from services.api.wingman import WingmanAPI
        time_stamp = int(self.get_start_date().timestamp())
        return WingmanAPI.get_percentile(self.boss_id, self.cm, self.duration_ms, time_stamp)

    # -------------------------------------------------------------------------
    # Methods to identify player roles
    # -------------------------------------------------------------------------

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
        boon_path = self.log.pjcontent.get('players', [])[i_player].get("groupBuffsActive", [])
        player_quick_contrib = 0

        if boon_path:
            for boon in boon_path:
                if boon.get("id") == self.QUICK_ID:
                    buff_data = boon.get("buffData", {})
                    if self.real_phase_id in buff_data:
                        player_quick_contrib = buff_data[self.real_phase_id].get("generation", 0)
                    break

        return player_quick_contrib >= self.MIN_QUICK_CONTRIB

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
        boon_path = self.log.pjcontent.get('players', [])[i_player].get("groupBuffsActive", [])
        player_alac_contrib = 0

        if boon_path:
            for boon in boon_path:
                if boon.get("id") == self.ALAC_ID:
                    buff_data = boon.get("buffData", {})
                    if self.real_phase_id in buff_data:
                        player_alac_contrib = buff_data[self.real_phase_id].get("generation", 0)
                    break

        return player_alac_contrib >= self.MIN_ALAC_CONTRIB

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

    def is_buyer(self, i_player: int) -> bool:
        """
        Checks if the player is a buyer (raid sale).

        A player is considered a buyer if they:
        - Die within the first 20 seconds of the fight
        - Have no rotation data

        Args:
            i_player: Index of the player to check

        Returns:
            True if the player is a buyer, False otherwise
        """
        player_name = self.get_player_name(i_player)
        mechanics = self.log.pjcontent.get('mechanics', [])

        if mechanics:
            death_history = [
                death for mech in mechanics
                if mech.get('name') == "Dead"
                for death in mech.get('mechanicsData', [])
            ]

            for death in death_history:
                if (death.get('time', 0) < self.BUYER_DEATH_THRESHOLD and
                        death.get('actor') == player_name):
                    return True

        try:
            rotation = self.get_player_rotation(i_player)
            if not rotation:
                return True
        except (KeyError, IndexError):
            return True

        return False
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
        buffmap = self.log.pjcontent.get('buffMap', {})
        buff_id = None

        # Find the buff ID based on its name
        for id_str, buff in buffmap.items():
            if buff.get('name') == buff_name:
                # Buff IDs in buffMap start with 'b', so remove the 'b'
                try:
                    buff_id = int(id_str[1:])
                    break
                except ValueError:
                    continue

        if buff_id is None:
            return False

        # Find the buff data for this player
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return False

        buffs = players[i_player].get('buffUptimes', [])
        buff_data = None

        for buff in buffs:
            if buff.get('id') == buff_id:
                buff_data = buff.get('states', [])
                break

        if not buff_data:
            return False

        # Extract the time coordinates and buff states
        xbuffplot = [pos[0] for pos in buff_data]
        ybuffplot = [pos[1] for pos in buff_data]

        # Find the buff state at the target time
        left_value = None
        for time in xbuffplot:
            if time <= target_time:
                left_value = time
            else:
                break

        if left_value is None:
            return False

        left_index = xbuffplot.index(left_value)
        return bool(ybuffplot[left_index])

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

    # -------------------------------------------------------------------------
    # Methods to access player data
    # -------------------------------------------------------------------------

    def get_player_name(self, i_player: int) -> str:
        """
        Retrieves the name of the player.

        Args:
            i_player: Player index

        Returns:
            Player's name
        """
        return self.log.jcontent.get('players', [])[i_player].get('name', 'Unknown')

    def get_player_account(self, i_player: int) -> str:
        """
        Retrieves the player's account name.

        Args:
            i_player: Player index

        Returns:
            Player's account name (format: name.1234)
        """
        return self.log.pjcontent.get('players', [])[i_player].get('account', 'Unknown')

    def get_player_pos(self, i_player: int, start: int = 0, end: Optional[int] = None) -> List[List[float]]:
        """
        Retrieves the player's positions during the fight.

        Args:
            i_player: Player index
            start: Start index for positions
            end: End index for positions (None = until the end)

        Returns:
            List of [x, y, z] positions for the player
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return []

        combat_data = players[i_player].get('combatReplayData', {})
        positions = combat_data.get('positions', [])

        return positions[start:end]

    def get_cc_boss(self, i_player: int) -> float:
        """
        Retrieves the defiance bar damage dealt to the boss by the player.

        Args:
            i_player: Player index

        Returns:
            Defiance bar damage to the boss
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return 0

        dps_targets = players[i_player].get('dpsTargets', [[]])
        if not dps_targets or not dps_targets[0]:
            return 0

        return dps_targets[0][0].get('breakbarDamage', 0)

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

    def get_cc_total(self, i_player: int) -> float:
        """
        Retrieves the total defiance bar damage dealt by the player.

        Args:
            i_player: Player index

        Returns:
            Total defiance bar damage
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return 0

        dps_all = players[i_player].get('dpsAll', [{}])
        if not dps_all:
            return 0

        return dps_all[0].get('breakbarDamage', 0)

    def get_player_id(self, name: str) -> Optional[int]:
        """
        Retrieves the index of a player by their name.

        Args:
            name: Player name to search

        Returns:
            Player index or None if not found
        """
        players = self.log.pjcontent.get('players', [])

        for i_player, player in enumerate(players):
            if player.get('name') == name:
                return i_player

        return None

    def get_player_spe(self, i_player: int) -> str:
        """
        Retrieves the player's specialization.

        Args:
            i_player: Player index

        Returns:
            Name of the specialization
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return "Unknown"

        return players[i_player].get('profession', 'Unknown')

    def get_player_mech_history(self, i_player: int, mechs: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Retrieves the mechanic history for a player.

        Collects all mechanic events that affected the player during the fight,
        with optional filtering by specific mechanic names.

        Args:
            i_player: Player index
            mechs: List of mechanic names to filter (None = all)

        Returns:
            List of mechanic events for the player, sorted by time
        """
        history = []
        player_name = self.get_player_name(i_player)
        mech_history = self.log.pjcontent.get('mechanics', [])

        if mechs is None:
            mechs = []

        for mech in mech_history:
            mech_name = mech.get('name', '')

            for data in mech.get('mechanicsData', []):
                if data.get('actor') == player_name:
                    if not mechs or mech_name in mechs:
                        history.append({
                            "name": mech_name,
                            "time": data.get('time', 0)
                        })

        history.sort(key=lambda event: event.get("time", 0))
        return history

    def players_to_string(self, i_players: List[int]) -> str:
        """
        Converts a list of player indices into a formatted string with their names.

        Uses custom names if available, otherwise falls back to the player's log name.
        The result is formatted in Markdown for display.

        Args:
            i_players: List of player indices

        Returns:
            Formatted string of player names
        """
        name_list = []

        for i in i_players:
            account = self.get_player_account(i)
            custom_name = CUSTOM_NAMES.get(account)

            if custom_name:
                name_list.append(custom_name)
            else:
                name_list.append(self.get_player_name(i))

        return "__" + '__ / __'.join(name_list) + "__"

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

    def get_player_rotation(self, i_player: int) -> List[Dict[str, Any]]:
        """
        Retrieves the player's skill rotation during the fight.

        Args:
            i_player: Player index

        Returns:
            List of skills used by the player
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return []

        return players[i_player].get('rotation', [])

    def time_entered_area(self, i_player: int, center: List[float], radius: float) -> Optional[int]:
        """
        Determines when the player entered a circular area.

        Args:
            i_player: Player index
            center: Coordinates [x, y, z] of the center of the area
            radius: Radius of the area

        Returns:
            Time in ms since the start of the fight, or None if never entered
        """
        from utils.maths import get_dist

        poses = self.get_player_pos(i_player)
        if not poses:
            return None

        position_interval = 150

        for i, pos in enumerate(poses):
            if get_dist(pos, center) < radius:
                return i * position_interval

        return None

    def time_exited_area(self, i_player: int, center: List[float], radius: float) -> Optional[int]:
        """
        Determines when the player exited a circular area after entering it.

        Args:
            i_player: Player index
            center: Coordinates [x, y, z] of the center of the area
            radius: Radius of the area

        Returns:
            Time in ms since the start of the fight, or None if never exited
        """
        from utils.maths import get_dist

        time_enter = self.time_entered_area(i_player, center, radius)
        if time_enter is None:
            return None

        # Delay between each position (ms)
        position_interval = 150
        i_enter = int(time_enter / position_interval)

        poses = self.get_player_pos(i_player, start=i_enter)
        if not poses:
            return None

        for i, pos in enumerate(poses):
            if get_dist(pos, center) > radius:
                return (i + i_enter) * position_interval

        return None

    def add_mvps(self, players: List[int]) -> None:
        """
        Adds players to the MVP (Most Valuable Player) list for this fight.

        Also increments the MVP count for each player in the global dictionary.

        Args:
            players: List of player indices to mark as MVP
        """
        self.mvp_accounts = [self.get_player_account(i) for i in players]

        for i in players:
            account = self.get_player_account(i)
            player = ALL_PLAYERS.get(account)
            if player:
                player.mvps += 1

    def add_lvps(self, players: List[int]) -> None:
        """
        Adds players to the LVP (Least Valuable Player) list for this fight.

        Also increments the LVP count for each player in the global dictionary.

        Args:
            players: List of player indices to mark as LVP
        """
        self.lvp_accounts = [self.get_player_account(i) for i in players]

        for i in players:
            account = self.get_player_account(i)
            player = ALL_PLAYERS.get(account)
            if player:
                player.lvps += 1

    def _get_dps_contrib(self, exclude: List[PlayerFilter] = None) -> Dict[str, float]:
        """
        Computes each player's DPS contribution, normalized on a scale from 0 to 20.

        This method gives a relative performance measure in terms of damage dealt,
        with the top DPS player scoring 20 points and others proportionally less.

        Args:
            exclude: List of filtering functions to exclude certain players

        Returns:
            Dictionary mapping player accounts to their normalized contribution
        """
        if exclude is None:
            exclude = []

        dps_ranking = {}
        max_dps = 0

        for i in self.player_list:
            if any(filter_func(i) for filter_func in exclude):
                continue

            try:
                player_dps = self.get_dmg_boss(i)

                if player_dps > max_dps:
                    max_dps = player_dps

                dps_ranking[self.get_player_account(i)] = player_dps
            except (KeyError, IndexError):
                continue

        if max_dps > 0:
            for player in dps_ranking:
                dps_ranking[player] = 20.0 * dps_ranking[player] / max_dps

        return dps_ranking

    def get_dps_ranking(self) -> Dict[str, float]:
        """
        Retrieves the DPS ranking of players based on damage contribution.

        Support players are excluded from this ranking.

        Returns:
            Dictionary mapping player accounts to their normalized contribution
        """
        return self._get_dps_contrib([self.is_support])

    def get_player_group(self, i_player: int) -> int:
        """
        Retrieves the group number the player belongs to.

        Args:
            i_player: Player index

        Returns:
            Group number
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return 0

        return players[i_player].get('group', 0)

    def get_foodswap_count(self, i_player: int) -> int:
        """
        Counts how many times the player changed food during the fight.

        Detects food buff changes by identifying a specific icon.

        Args:
            i_player: Player index

        Returns:
            Number of food swaps
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return 0

        buff_map = self.log.pjcontent.get('buffMap', {})
        buff_uptimes = players[i_player].get('buffUptimes', [])

        food_swap_ids = []

        for buff_name, data in buff_map.items():
            if data.get('icon') == self.FOOD_SWAP_ICON:
                try:
                    food_swap_ids.append(int(buff_name[1:]))  # Remove 'b' prefix
                except ValueError:
                    continue

        food_swap_count = 0

        for buff in buff_uptimes:
            if buff.get('id') in food_swap_ids:
                states = buff.get('states', [])
                for state in states:
                    if len(state) > 1 and state[1] == 1:
                        food_swap_count += 1

        return food_swap_count

    # -------------------------------------------------------------------------
    # "MVP"
    # -------------------------------------------------------------------------

    def get_mvp_cc_boss(self, extra_exclude: List[Callable[[int], bool]] = None) -> Optional[str]:
        """
        Identifies and rewards players with the best contribution to boss control (CC).

        Finds the players who contributed the minimum CC value on the main boss,
        adds them to the MVP list, and generates a formatted message for the report.

        Args:
            extra_exclude: List of additional filtering functions to exclude certain players

        Returns:
            Formatted message for the report, or None if no CC was done
        """
        if extra_exclude is None:
            extra_exclude = []

        # Get players with the minimum CC contribution
        i_players, min_cc, total_cc = Analyzer.get_min_value(self.player_list, self.get_cc_boss, exclude=extra_exclude)

        # If no players did CC, do not generate a message
        if total_cc == 0:
            return None

        # Add these players to the MVP list
        self.add_mvps(i_players)

        # Prepare variables for the message
        mvp_names = self.players_to_string(i_players)
        cc_ratio = min_cc / total_cc * 100
        number_mvp = len(i_players)

        if min_cc == 0:
            if number_mvp == 1:
                return language_config.selected_language["MVP BOSS 0 CC S"].format(mvp_names=mvp_names)
            else:
                return language_config.selected_language["MVP BOSS 0 CC P"].format(mvp_names=mvp_names)
        else:
            if number_mvp == 1:
                return language_config.selected_language["MVP BOSS CC S"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            else:
                return language_config.selected_language["MVP BOSS CC P"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)

    def get_mvp_cc_total(self, extra_exclude: List[Callable[[int], bool]] = None) -> Optional[str]:
        """
        Identifies and rewards players with the best contribution to total control (CC).

        Finds the players who contributed the minimum CC value in total (boss + adds),
        adds them to the MVP list, and generates a formatted message for the report.

        Args:
            extra_exclude: List of additional filtering functions to exclude certain players

        Returns:
            Formatted message for the report, or None if no CC was done
        """
        if extra_exclude is None:
            extra_exclude = []

        # Get players with the minimum total CC contribution
        i_players, min_cc, total_cc = Analyzer.get_min_value(self.player_list, self.get_cc_total, exclude=extra_exclude)

        # If no players did CC, do not generate a message
        if total_cc == 0:
            return None

        # Add these players to the MVP list
        self.add_mvps(i_players)

        # Prepare variables for the message
        mvp_names = self.players_to_string(i_players)
        cc_ratio = min_cc / total_cc * 100
        number_mvp = len(i_players)

        if min_cc == 0:
            if number_mvp == 1:
                return language_config.selected_language["MVP TOTAL 0 CC S"].format(mvp_names=mvp_names)
            else:
                return language_config.selected_language["MVP TOTAL 0 CC P"].format(mvp_names=mvp_names)
        else:
            if number_mvp == 1:
                return language_config.selected_language["MVP TOTAL CC S"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            else:
                return language_config.selected_language["MVP TOTAL CC P"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)

    def get_bad_dps(self, extra_exclude: List[Callable[[int], bool]] = None) -> Optional[str]:
        """
        Identifies DPS players who deal less damage than a support player.

        This method looks for the support players who dealt the most damage,
        then identifies DPS players whose damage is lower than that of the support.
        These DPS players are considered underperforming and are added to the MVP list
        (ironically) to highlight their need for improvement.

        Args:
            extra_exclude: List of additional filtering functions to exclude certain players

        Returns:
            Formatted message for the report, or None if no DPS are underperforming
        """
        if extra_exclude is None:
            extra_exclude = []

        # Find the support player with the highest damage
        i_sup, sup_max_dmg, _ = Analyzer.get_max_value(
            self.player_list,
            self.get_dmg_boss,
            exclude=[self.is_dps, self.is_bannerslave]
        )

        sup_name = self.players_to_string(i_sup)
        bad_dps = []

        # Identify DPS players who deal less damage than the best support
        for i in self.player_list:
            # Exclude players who are not relevant to this analysis
            should_exclude = (
                    (extra_exclude and any(filter_func(i) for filter_func in extra_exclude)) or
                    self.is_dead(i) or
                    self.is_support(i) or
                    self.is_bannerslave(i)
            )

            if should_exclude:
                continue

            dps = self.get_dmg_boss(i)

            # Check if this DPS does less damage than the best support
            if dps < sup_max_dmg:
                # Special exception for Spellbreakers on the QUOIDIMM boss
                if not (self.name == "QUOIDIMM" and self.get_player_spe(i) == "Spellbreaker"):
                    bad_dps.append(i)

        # If there are underperforming DPS, generate a message
        if bad_dps:
            self.add_mvps(bad_dps)
            bad_dps_name = self.players_to_string(bad_dps)

            if len(bad_dps) == 1:
                return language_config.selected_language["MVP BAD DPS S"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)
            else:
                return language_config.selected_language["MVP BAD DPS P"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)

        return None

    # -------------------------------------------------------------------------
    # "LVP"
    # -------------------------------------------------------------------------

    def get_lvp_cc_boss(self) -> Optional[str]:
        """
        Identifies and penalizes players with the worst contribution to boss control (CC).

        Finds the players who contributed the maximum CC value on the main boss,
        adds them to the LVP list, and generates a formatted message for the report.

        Returns:
            Formatted message for the report, or None if no CC was done
        """
        # Get players with the maximum CC contribution
        i_players, max_cc, total_cc = Analyzer.get_max_value(self.player_list, self.get_cc_boss)

        # If no players did CC, do not generate a message
        if total_cc == 0:
            return None

        # Add these players to the LVP list
        self.add_lvps(i_players)

        # Prepare variables for the message
        lvp_names = self.players_to_string(i_players)
        cc_ratio = max_cc / total_cc * 100

        # Generate the message
        return language_config.selected_language["LVP BOSS CC"].format(lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)

    def get_lvp_cc_total(self) -> Optional[str]:
        """
        Identifies and penalizes players with the worst contribution to total control (CC).

        Finds the players who contributed the maximum CC value in total (boss + adds),
        adds them to the LVP list, and generates a formatted message for the report.

        Returns:
            Formatted message for the report, or None if no CC was done
        """
        # Get players with the maximum total CC contribution
        i_players, max_cc, total_cc = Analyzer.get_max_value(self.player_list, self.get_cc_total)

        # If no players did CC, do not generate a message
        if total_cc == 0:
            return None

        # Add these players to the LVP list
        self.add_lvps(i_players)

        # Prepare variables for the message
        lvp_names = self.players_to_string(i_players)
        cc_ratio = max_cc / total_cc * 100

        # Generate the message
        return language_config.selected_language["LVP TOTAL CC"].format(lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)

    def get_lvp_dps(self) -> str:
        """
        Identifies and penalizes players with the worst damage contribution.

        Finds the players who dealt the most damage to the boss,
        adds them to the LVP list, and generates a formatted message for the report.
        This method also checks if the player frequently changed food,
        which could explain their poor performance.

        Returns:
            Formatted message for the report
        """
        # Get players with the maximum damage
        i_players, max_dmg, total_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)

        # Calculate additional statistics
        dmg_ratio = max_dmg / total_dmg * 100 if total_dmg > 0 else 0
        lvp_dps_name = self.players_to_string(i_players)
        dps = max_dmg / self.duration_ms if self.duration_ms > 0 else 0

        # Check for food changes
        food_swap_count = self.get_foodswap_count(i_players[0]) if i_players else 0

        # Add these players to the LVP list
        self.add_lvps(i_players)

        if food_swap_count:
            return language_config.selected_language["LVP DPS FOODSWAP"].format(
                lvp_dps_name=lvp_dps_name,
                max_dmg=max_dmg,
                dmg_ratio=dmg_ratio,
                dps=dps,
                foodSwapCount=food_swap_count
            )
        else:
            return language_config.selected_language["LVP DPS"].format(
                lvp_dps_name=lvp_dps_name,
                max_dmg=max_dmg,
                dmg_ratio=dmg_ratio,
                dps=dps
            )
    # -------------------------------------------------------------------------
    # Boss-related data
    # -------------------------------------------------------------------------

    def get_pos_boss(self, start: int = 0, end: Optional[int] = None) -> List[List[float]]:
        """
        Retrieves the main boss's positions during the fight.

        Iterates through the targets to find one that matches a known boss
        and returns its positions.

        Args:
            start: Starting index for positions (default = 0)
            end: Ending index for positions (None = until the end)

        Returns:
            List of [x, y, z] positions of the boss

        Raises:
            ValueError: If no boss is found among the targets
        """
        targets = self.log.pjcontent.get('targets', [])

        for target in targets:
            target_id = target.get('id')
            if target_id in BOSS_DICT:
                combat_data = target.get('combatReplayData', {})
                positions = combat_data.get('positions', [])
                return positions[start:end]

        raise ValueError('No Boss found in targets')

    def get_phase_timers(self, target_phase: str, in_milliseconds: bool = False) -> Tuple[int, int]:
        """
        Retrieves the start and end times of a specific fight phase.

        Args:
            target_phase: Name of the phase to look for
            in_milliseconds: If True, returns times in milliseconds;
                             otherwise, in position indices

        Returns:
            Tuple (start, end) representing the phase times or indices

        Raises:
            ValueError: If the phase is not found
        """
        phases = self.log.pjcontent.get('phases', [])

        for phase in phases:
            if phase.get('name') == target_phase:
                start = phase.get('start', 0)
                end = phase.get('end', 0)

                if in_milliseconds:
                    return start, end

                # Convert to position indices
                return time_to_index(start, self.time_base), time_to_index(end, self.time_base)

        raise ValueError(f'Phase "{target_phase}" not found')

    def get_mech_value(self, i_player: int, mech_name: str, phase: str = "Full Fight") -> int:
        """
        Retrieves the number of occurrences of a mechanic for a player during a specific phase.

        Args:
            i_player: Player index
            mech_name: Name of the mechanic to look for
            phase: Name of the phase (default = "Full Fight")

        Returns:
            Number of mechanic occurrences for this player
        """
        phase_id = self.get_phase_id(phase)

        # Create the list of mechanic names
        mechs_list = []
        for mech in self.mechanics:
            mechs_list.append(mech.get('name', ''))

        # Check if the mechanic exists
        if mech_name in mechs_list:
            i_mech = mechs_list.index(mech_name)

            try:
                # Access mechanic stats with index checks
                phases = self.log.jcontent.get('phases', [])
                if phase_id < len(phases):
                    mech_stats = phases[phase_id].get('mechanicStats', [])

                    if i_player < len(mech_stats) and i_mech < len(mech_stats[i_player]):
                        return mech_stats[i_player][i_mech][0]
            except (IndexError, KeyError, TypeError):
                # Return 0 in case of any error
                pass

        return 0

    def boss_hp_to_time(self, hp: float) -> Optional[int]:
        """
        Converts a boss HP percentage to the time elapsed since the start of the fight.

        This method finds the first moment when the boss's HP fell below the given percentage.

        Args:
            hp: Boss health percentage (0-100)

        Returns:
            Time in ms when the boss had this HP percentage, or None if not found
        """
        targets = self.log.pjcontent.get('targets', [])
        if not targets:
            return None

        hp_percents = targets[0].get('healthPercents', [])

        for timer in hp_percents:
            # Ensure timer is a list with at least 2 elements
            if isinstance(timer, list) and len(timer) > 1:
                if timer[1] < hp:
                    return timer[0]

        return None

    def get_mechanic_history(self, name: str) -> List[Dict[str, Any]]:
        """
        Retrieves the full history of a specific mechanic during the fight.

        Args:
            name: Full name of the mechanic

        Returns:
            List of occurrences of the mechanic, or an empty list if not found
        """
        mechanics = self.log.pjcontent.get('mechanics', [])

        for mech in mechanics:
            if mech.get('fullName') == name:
                return mech.get('mechanicsData', [])

        return []

    def get_phase_id(self, name: str) -> int:
        """
        Retrieves the ID of a fight phase by its name.

        Args:
            name: Name of the phase

        Returns:
            Phase ID, or 0 if not found
        """
        phases = self.log.pjcontent.get('phases', [])

        for i, phase in enumerate(phases):
            if phase.get('name') == name:
                return i

        return 0

    def get_time_base(self) -> int:
        """
        Calculates the time interval between each recorded position.

        This value is used to convert position indices to timestamps.
        It represents the ratio between the total fight duration and the number of recorded positions.

        Returns:
            Time interval in milliseconds
        """
        players = self.log.pjcontent.get('players', [])
        if not players:
            return 150  # Default value

        # Access the first player's replay data
        combat_data = players[0].get('combatReplayData', {})
        start = combat_data.get('start', 0)
        end = combat_data.get('end', 0)
        positions = combat_data.get('positions', [])

        if not positions or end <= start:
            return 150  # Default value

        # Calculate the interval by dividing total duration by number of positions
        delta = end - start
        return int(delta / len(positions))
