from datetime import timedelta

from config.settings import CUSTOM_NAMES, EMOTE_WINGMAN, ALL_PLAYERS
from i18n.languages import language_config
from utils.formatters import disp_time


class ReportGenerator:
    """
    Classe qui génère des rapports de raid formatés à partir des logs et des données des joueurs.

    Cette classe transforme les données brutes des logs de combat et des statistiques des joueurs
    en un rapport formaté en Markdown qui peut être partagé dans un chat Discord ou autre.

    Attributes:
        logs (list) : Liste des logs de boss à inclure dans le rapport
        players (dict) : Dictionnaire des joueurs participant au raid
        titre (str) : Titre du rapport (défaut : "Run")
        cutting_text_limit (int) : Limite de caractères pour la découpe des messages (défaut : 1700)
    """

    def __init__(self, logs: list, players: dict, titre: str = "Run"):
        """
        Initialise un générateur de rapport avec les logs, les joueurs et un titre optionnel.

        Args:
            logs (list) : Liste des logs de boss à inclure dans le rapport
            players (dict) : Dictionnaire des joueurs participant au raid
            titre (str, optional) : Titre du rapport. Par défaut "Run"
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
        Génère le rapport complet et le renvoie sous forme de liste de messages.

        Le rapport inclut des détails sur chaque aile et chaque boss, ainsi que les
        MVPs, LVPs et autres statistiques si disponibles.

        Returns:
            list: Liste de chaînes de caractères formatées en Markdown,
                 chacune respectant la limite de caractères définie
        """
        if not self.logs:
            print("No boss found")
            return []

        # Déterminer les MVPs et LVPs
        self._calculate_mvp_lvp()

        # Trier les logs par date de début
        self.logs.sort(key=lambda log: log.start_date, reverse=False)

        # Organiser les logs par aile
        wings = self._group_logs_by_wing()

        # Informations générales du raid
        run_date = self.logs[0].start_date.strftime("%d/%m/%Y")
        run_duration = disp_time(self.logs[-1].end_date - self.logs[0].start_date)
        number_boss = len(self.logs)

        # Initialiser le message avec titre et date
        run_message = f"# {self.titre}\n" if number_boss > 2 else ""
        run_message += f"# {run_date}\n"

        # Générer les détails pour chaque aile
        run_message, wingman_stats = self._generate_wing_details(wings, run_message)

        # Ajouter le récapitulatif si nécessaire
        if number_boss > 2:
            run_message = self._add_summary(run_message, run_duration, wingman_stats)

        # Ajouter le dernier message s'il n'est pas vide
        if run_message:
            self.split_message.append(run_message)

        # Nettoyer les données pour libérer la mémoire
        logs_copy = self.split_message.copy()
        self.logs.clear()
        self.players.clear()
        self.split_message.clear()

        return logs_copy

    def _cut_text(self, text: str) -> str:
        """
        Découpe le texte si sa longueur dépasse la limite définie.

        Lorsque le texte dépasse la limite, la portion actuelle est ajoutée à
        split_message et une nouvelle chaîne vide est retournée.

        Args:
            text (str) : Le texte à vérifier et potentiellement découper

        Returns:
            str: Le texte original ou une chaîne vide si le texte a été découpé
        """
        if len(text) >= self.cutting_text_limit:
            self.split_message.append(text)
            return ""
        return text

    def _group_logs_by_wing(self) -> dict:
        """
        Regroupe les logs par aile.

        Returns:
            dict: Dictionnaire où les clés sont les noms/numéros d'aile et les valeurs
                 sont les listes de logs correspondants
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
        Calcule les MVPs (Most Valuable Players) et LVPs (Least Valuable Players) du raid.

        Cette méthode détermine les joueurs avec le plus grand nombre de MVPs et LVPs,
        et stocke leurs noms (personnalisés si disponibles) dans mvp_names et lvp_names.
        """
        # Trouver les joueurs avec le plus grand nombre de MVPs
        for player in self.players.values():
            if player.mvps > self.max_mvp_score:
                self.max_mvp_score = player.mvps
                self.mvp = [player]
            elif player.mvps == self.max_mvp_score:
                self.mvp.append(player)

            # Trouver les joueurs avec le plus grand nombre de LVPs
            if player.lvps > self.max_lvp_score:
                self.max_lvp_score = player.lvps
                self.lvp = [player]
            elif player.lvps == self.max_lvp_score:
                self.lvp.append(player)

        # Extraire les noms des MVPs (avec noms personnalisés si disponibles)
        for player in self.mvp:
            account = player.account
            custom_name = CUSTOM_NAMES.get(account)
            self.mvp_names.append(custom_name if custom_name else player.name)

        # Extraire les noms des LVPs (avec noms personnalisés si disponibles)
        for player in self.lvp:
            account = player.account
            custom_name = CUSTOM_NAMES.get(account)
            self.lvp_names.append(custom_name if custom_name else player.name)

    def _generate_wing_details(self, wings: dict, run_message: str) -> tuple:
        """
        Génère les détails pour chaque aile et bosses correspondants.

        Args:
            wings (dict): Dictionnaire des ailes et leurs logs associés
            run_message (str): Message en cours de construction

        Returns:
            tuple: (message mis à jour, (total_wingman_score, notes_nb))
        """
        total_wingman_score = 0
        notes_nb = 0

        for wingname, wing in wings.items():
            # Calculer la durée de l'aile
            wing_first_log = wing[0]
            wing_last_log = wing[-1]
            wing_duration = disp_time(wing_last_log.end_date - wing_first_log.start_date)

            # Ajouter l'en-tête de l'aile au message
            run_message = self._format_wing_header(wingname, wing_duration, wing, run_message)

            # Traiter chaque boss de l'aile
            for boss in wing:
                # Formater les informations du boss
                boss_name = boss.name + (" CM" if boss.cm else "")
                boss_duration = disp_time(timedelta(seconds=boss.duration_ms / 1000))
                boss_url = boss.log.url
                boss_percentil = boss.wingman_percentile

                # Ajouter les détails du boss au message
                if boss_percentil is not None:
                    notes_nb += 1
                    total_wingman_score += boss_percentil
                    run_message += f"* **[{boss_name}]({boss_url})** **{boss_duration} ({boss_percentil}%{EMOTE_WINGMAN})**\n"
                else:
                    run_message += f"* **[{boss_name}]({boss_url})** **{boss_duration}**\n"
                run_message = self._cut_text(run_message)

                # Ajouter MVP/LVP du boss s'ils existent
                if boss.mvp:
                    run_message += boss.mvp + "\n"
                    run_message = self._cut_text(run_message)
                if boss.lvp:
                    run_message += boss.lvp + "\n"
                    run_message = self._cut_text(run_message)

                # Mettre à jour les statistiques DPS pour les joueurs (sauf pour ESCORT)
                if boss.name != "ESCORT":
                    for player_account, dps_mark in boss.get_dps_ranking().items():
                        ALL_PLAYERS[player_account].add_mark(dps_mark)

            # Ajouter une ligne vide après chaque aile
            run_message += "\n"

        return run_message, (total_wingman_score, notes_nb)

    def _format_wing_header(self, wingname, wing_duration: str, wing: list, run_message: str) -> str:
        """
        Formate l'en-tête d'une aile en fonction de son type.

        Args:
            wingname: Nom ou numéro de l'aile
            wing_duration (str): Durée formatée de l'aile
            wing (list): Liste des logs de l'aile
            run_message (str): Message en cours de construction

        Returns:
            str: Message avec l'en-tête de l'aile ajouté
        """
        # Formater différemment selon que le nom d'aile est un nombre ou une chaîne
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
            # Pour les ailes avec des noms spéciaux, utiliser le dictionnaire de traduction
            run_message += language_config.selected_language[wingname].format(wing_duration=wing_duration)

        return run_message

    def _add_summary(self, run_message: str, run_duration: str, wingman_stats: tuple) -> str:
        """
        Ajoute un récapitulatif au rapport avec les MVPs, LVPs et statistiques globales.

        Args:
            run_message (str): Message en cours de construction
            run_duration (str): Durée totale du raid formatée
            wingman_stats (tuple): Tuple contenant (total_wingman_score, notes_nb)

        Returns:
            str: Message avec le récapitulatif ajouté
        """
        total_wingman_score, notes_nb = wingman_stats

        # Préparer les chaînes pour les MVPs et LVPs
        mvps = ', '.join(self.mvp_names)
        lvps = ', '.join(self.lvp_names)

        # Calculer la note moyenne Wingman
        note_wingman = total_wingman_score / notes_nb if notes_nb > 0 else 0

        # Ajouter les MVPs s'il y en a plus d'un
        if self.max_mvp_score > 1:
            run_message += language_config.selected_language["MVP"].format(mvps=mvps, max_mvp_score=self.max_mvp_score)

        # Ajouter les LVPs s'il y en a plus d'un
        if self.max_lvp_score > 1:
            run_message += language_config.selected_language["LVP"].format(lvps=lvps, max_lvp_score=self.max_lvp_score)

        # Ajouter la durée totale et la note Wingman
        run_message += language_config.selected_language["TIME"].format(run_duration=run_duration)
        run_message += language_config.selected_language["WINGMAN"].format(note_wingman=note_wingman, emote_wingman=EMOTE_WINGMAN)

        return run_message