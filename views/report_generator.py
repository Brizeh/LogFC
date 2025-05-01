from datetime import timedelta

from config.settings import CUSTOM_NAMES, EMOTE_WINGMAN, ALL_PLAYERS
from i18n.languages import language_config
from utils.formatters import disp_time


class ReportGenerator:
    """
    Class that generates formatted raid reports from logs and player data.

    This class transforms raw combat log data and player statistics
    into a Markdown-formatted report that can be shared in a Discord chat or elsewhere.

    Attributes:
        logs (list): List of boss logs to include in the report
        players (dict): Dictionary of players participating in the raid
        titre (str): Report title (default: "Run")
        cutting_text_limit (int): Character limit for message splitting (default: 1700)
    """

    def __init__(self, logs: list, players: dict, titre: str = "Run"):
        """
        Initializes a report generator with logs, players, and an optional title.

        Args:
            logs (list): List of boss logs to include in the report
            players (dict): Dictionary of players participating in the raid
            titre (str, optional): Report title. Default "Run"
        """
        self.logs = logs
        self.players = players
        self.titre = titre
        self.cutting_text_limit = 1700
        self.split_message = []
        self.mvp = []
        self.lvp = []
        self.mvp_names = []
        self.lvp_names = []
        self.max_mvp_score = 1
        self.max_lvp_score = 1

    def generate(self) -> list:
        """
        Generates the complete report and returns it as a list of messages.

        The report includes details about each wing and each boss, as well as
        MVPs, LVPs, and other statistics if available.

        Returns:
            list: List of Markdown-formatted strings,
                 each respecting the defined character limit
        """
        if not self.logs:
            print("No boss found")
            return []

        # Determine MVPs and LVPs
        self._calculate_mvp_lvp()

        # Sort logs by start date
        self.logs.sort(key=lambda log: log.start_date, reverse=False)

        # Organize logs by wing
        wings = self._group_logs_by_wing()

        # General raid information
        run_date = self.logs[0].start_date.strftime("%d/%m/%Y")
        run_duration = disp_time(self.logs[-1].end_date - self.logs[0].start_date)
        number_boss = len(self.logs)

        # Initialize the message with title and date
        run_message = f"# {self.titre}\n" if number_boss > 2 else ""
        run_message += f"# {run_date}\n"

        # Generate details for each wing
        run_message, wingman_stats = self._generate_wing_details(wings, run_message)

        # Add summary if necessary
        if number_boss > 2:
            run_message = self._add_summary(run_message, run_duration, wingman_stats)

        # Add the last message if it's not empty
        if run_message:
            self.split_message.append(run_message)

        # Clean up data to free memory
        logs_copy = self.split_message.copy()
        self.logs.clear()
        self.players.clear()
        self.split_message.clear()

        return logs_copy

    def _cut_text(self, text: str) -> str:
        """
        Cuts the text if its length exceeds the defined limit.

        When the text exceeds the limit, the current portion is added to
        split_message and a new empty string is returned.

        Args:
            text (str): The text to check and potentially cut

        Returns:
            str: The original text or an empty string if the text has been cut
        """
        if len(text) >= self.cutting_text_limit:
            self.split_message.append(text)
            return ""
        return text

    def _group_logs_by_wing(self) -> dict:
        """
        Groups logs by wing.

        Returns:
            dict: Dictionary where keys are wing names/numbers and values
                 are lists of corresponding logs
        """
        wings = {}
        for log in self.logs:
            wing = log.wing
            if wings.get(wing):
                wings[wing].append(log)
            else:
                wings[wing] = [log]
        return wings

    def _calculate_mvp_lvp(self) -> None:
        """
        Calculates the MVPs (Most Valuable Players) and LVPs (Least Valuable Players) of the raid.

        This method determines the players with the highest number of MVPs and LVPs,
        and stores their names (customized if available) in mvp_names and lvp_names.
        """
        # Find players with the highest number of MVPs
        for player in self.players.values():
            if player.mvps > self.max_mvp_score:
                self.max_mvp_score = player.mvps
                self.mvp = [player]
            elif player.mvps == self.max_mvp_score:
                self.mvp.append(player)

            # Find players with the highest number of LVPs
            if player.lvps > self.max_lvp_score:
                self.max_lvp_score = player.lvps
                self.lvp = [player]
            elif player.lvps == self.max_lvp_score:
                self.lvp.append(player)

        # Extract MVP names (with custom names if available)
        for player in self.mvp:
            account = player.account
            custom_name = CUSTOM_NAMES.get(account)
            self.mvp_names.append(custom_name if custom_name else player.name)

        # Extract LVP names (with custom names if available)
        for player in self.lvp:
            account = player.account
            custom_name = CUSTOM_NAMES.get(account)
            self.lvp_names.append(custom_name if custom_name else player.name)

    def _generate_wing_details(self, wings: dict, run_message: str) -> tuple:
        """
        Generates details for each wing and corresponding bosses.

        Args:
            wings (dict): Dictionary of wings and their associated logs
            run_message (str): Message under construction

        Returns:
            tuple: (updated message, (total_wingman_score, notes_nb))
        """
        total_wingman_score = 0
        notes_nb = 0

        for wingname, wing in wings.items():
            # Calculate wing duration
            wing_first_log = wing[0]
            wing_last_log = wing[-1]
            wing_duration = disp_time(wing_last_log.end_date - wing_first_log.start_date)

            # Add wing header to the message
            run_message = self._format_wing_header(wingname, wing_duration, wing, run_message)

            # Process each boss in the wing
            for boss in wing:
                # Format boss information
                boss_name = boss.name + (" CM" if boss.cm else "")
                boss_duration = disp_time(timedelta(seconds=boss.duration_ms / 1000))
                boss_url = boss.log.url
                boss_percentil = boss.wingman_percentile

                # Add boss details to the message
                if boss_percentil is not None:
                    notes_nb += 1
                    total_wingman_score += boss_percentil
                    run_message += f"* **[{boss_name}]({boss_url})** **{boss_duration} ({boss_percentil}%{EMOTE_WINGMAN})**\n"
                else:
                    run_message += f"* **[{boss_name}]({boss_url})** **{boss_duration}**\n"
                run_message = self._cut_text(run_message)

                # Add boss MVP/LVP if they exist
                if boss.mvp:
                    run_message += boss.mvp + "\n"
                    run_message = self._cut_text(run_message)
                if boss.lvp:
                    run_message += boss.lvp + "\n"
                    run_message = self._cut_text(run_message)

                # Update DPS statistics for players (except for ESCORT)
                if boss.name != "ESCORT":
                    for player_account, dps_mark in boss.get_dps_ranking().items():
                        ALL_PLAYERS[player_account].add_mark(dps_mark)

            # Add an empty line after each wing
            run_message += "\n"

        return run_message, (total_wingman_score, notes_nb)

    def _format_wing_header(self, wingname, wing_duration: str, wing: list, run_message: str) -> str:
        """
        Formats a wing header based on its type.

        Args:
            wingname: Wing name or number
            wing_duration (str): Formatted wing duration
            wing (list): List of wing logs
            run_message (str): Message under construction

        Returns:
            str: Message with the wing header added
        """
        # Format differently depending on whether the wing name is a number or a string
        if isinstance(wingname, int):
            if wingname == 1:
                run_message += language_config.selected_language["W1"].format(wing_duration=wing_duration)
            elif wingname == 3:
                escort_in_run = any(boss.name == "ESCORT" for boss in wing)
                if escort_in_run:
                    run_message += f"## W3 - *{wing_duration}*\n"
                else:
                    run_message += language_config.selected_language["W3"].format(wing_duration=wing_duration)
            elif wingname == 7:
                run_message += language_config.selected_language["W7"].format(wing_duration=wing_duration)
            else:
                run_message += f"## W{wingname} - *{wing_duration}*\n"
        else:
            # For wings with special names, use the translation dictionary
            run_message += language_config.selected_language[wingname].format(wing_duration=wing_duration)

        return run_message

    def _add_summary(self, run_message: str, run_duration: str, wingman_stats: tuple) -> str:
        """
        Adds a summary to the report with MVPs, LVPs, and global statistics.

        Args:
            run_message (str): Message under construction
            run_duration (str): Formatted total raid duration
            wingman_stats (tuple): Tuple containing (total_wingman_score, notes_nb)

        Returns:
            str: Message with the summary added
        """
        total_wingman_score, notes_nb = wingman_stats

        # Prepare strings for MVPs and LVPs
        mvps = ', '.join(self.mvp_names)
        lvps = ', '.join(self.lvp_names)

        # Calculate average Wingman score
        note_wingman = total_wingman_score / notes_nb if notes_nb > 0 else 0

        # Add MVPs if there's more than one
        if self.max_mvp_score > 1:
            run_message += language_config.selected_language["MVP"].format(mvps=mvps, max_mvp_score=self.max_mvp_score)

        # Add LVPs if there's more than one
        if self.max_lvp_score > 1:
            run_message += language_config.selected_language["LVP"].format(lvps=lvps, max_lvp_score=self.max_lvp_score)

        # Add total duration and Wingman score
        run_message += language_config.selected_language["TIME"].format(run_duration=run_duration)
        run_message += language_config.selected_language["WINGMAN"].format(note_wingman=note_wingman, emote_wingman=EMOTE_WINGMAN)

        return run_message
