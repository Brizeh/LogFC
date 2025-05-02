from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, ClassVar

from config.settings import PARIS_TIMEZONE, DATE_FORMAT
from core.models.boss_data_access import DataAccessMixin
from core.models.log import Log


class BossEncounterMixin(DataAccessMixin):

    # Default class attributes, meant to be overridden in subclasses
    name: ClassVar[Optional[str]] = None
    wing: ClassVar[int] = 0
    boss_id: ClassVar[int] = -1
    real_phase: ClassVar[str] = "Full Fight"

    def __init__(self, log: Log) -> None:
        """
        Initializes a boss encounter from a Log object.

        Args:
            log: The Log object containing the encounter data
        """
        super().__init__(log)
        self.cm: bool = self.is_cm()
        self.logName: str = self.get_log_name()
        self.mechanics: List[Dict[str, Any]] = self.get_mechanics()
        self.duration_ms: int = self.get_duration_ms()
        self.start_date: datetime = self.get_start_date()
        self.end_date: datetime = self.get_end_date()
        self.wingman_time: Optional[List[int]] = self.get_wingman_time()
        self.wingman_percentile: Optional[float] = self.get_wingman_percentile()
        self.real_phase_id: int = self.get_phase_id(self.real_phase)
        self.time_base: int = self.get_time_base()

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
            # In case of a parsing error
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
            # In case of a parsing error
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
