from datetime import timedelta
from config.settings import EMOTE_WINGMAN, ALL_PLAYERS, CUSTOM_NAMES
from i18n.languages import language_config
from utils.formatters import disp_time


class ReportGenerator:
    @staticmethod
    def generate_report(logs, players, titre="Run"):
        if not logs:
            print("No boss found")
            return []

        cutting_text_limit = 1700
        split_message = []

        # Recherche des MVP et LVP
        mvp, lvp, max_mvp_score, max_lvp_score = ReportGenerator._calculate_mvp_lvp(players)

        # Trier les logs par date
        logs.sort(key=lambda log: log.start_date, reverse=False)

        # Organiser les logs par aile
        wings = ReportGenerator._organize_by_wings(logs)

        # Date de début et durée totale
        run_date = logs[0].start_date.strftime("%d/%m/%Y")
        run_duration = disp_time(logs[-1].end_date - logs[0].start_date)
        number_boss = len(logs)

        # Construction du message
        run_message = f"# {titre}\n" if number_boss > 2 else ""
        run_message += f"# {run_date}\n"

        # Informations Wingman
        total_wingman_score = 0
        notes_nb = 0

        # Génération du rapport par aile
        for wingname, wing in wings.items():
            run_message = ReportGenerator._add_wing_info(run_message, wingname, wing, notes_nb, total_wingman_score,
                                                         split_message, cutting_text_limit)

        # Ajout du résumé pour les runs avec plusieurs boss
        if number_boss > 2:
            run_message = ReportGenerator._add_summary(run_message, mvp, lvp, max_mvp_score, max_lvp_score,
                                                       run_duration, notes_nb, total_wingman_score)

        split_message.append(run_message)

        # Nettoyage des données globales
        logs.clear()
        players.clear()

        return split_message

    # Méthodes privées d'aide à la génération
    @staticmethod
    def _calculate_mvp_lvp(players):
        # ... code pour calculer MVP et LVP ...
        pass

    @staticmethod
    def _organize_by_wings(logs):
        # ... code pour organiser les logs par aile ...
        pass

    @staticmethod
    def _add_wing_info(run_message, wingname, wing, notes_nb, total_wingman_score, split_message, cutting_text_limit):
        # ... code pour ajouter les informations de l'aile ...
        pass

    @staticmethod
    def _add_summary(run_message, mvp, lvp, max_mvp_score, max_lvp_score, run_duration, notes_nb, total_wingman_score):
        # ... code pour ajouter le résumé ...
        pass

    @staticmethod
    def _cut_text(text, limit, split_message):
        # ... code pour découper le texte si trop long ...
        pass
