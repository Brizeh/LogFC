"""
Module contenant la classe LARGOS pour l'analyse des logs du boss Twin Largos.
"""

from core.models.boss import Boss
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class LARGOS(Boss):
    """
    Classe représentant le boss Twin Largos de la sixième aile de raid.

    Cette classe implémente des méthodes spécifiques pour analyser les performances
    des joueurs contre les Twin Largos, notamment concernant les ruées d'attaque.

    Attributes:
        last (LARGOS): Référence à la dernière instance créée
        name (str): Nom du boss "LARGOS"
        wing (int): Numéro de l'aile (6)
        boss_id (int): Identifiant du boss (21105)
    """

    last = None
    name = "LARGOS"
    wing = 6
    boss_id = 21105

    def __init__(self, log):
        """
        Initialise une instance de LARGOS avec un log spécifique.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        LARGOS.last = self

    def get_mvp(self):
        """
        Détermine le MVP (Most Valuable Player) pour le combat contre Twin Largos.

        Vérifie d'abord les joueurs ayant subi le plus de ruées d'attaque.

        Returns:
            str: Message formaté indiquant le MVP et la raison, ou None si aucun MVP
        """
        msg_dash = self.mvp_dash()
        if msg_dash:
            return msg_dash

        return None

    def get_lvp(self):
        """
        Détermine le LVP (Least Valuable Player) pour le combat contre Twin Largos.

        Returns:
            str: Message formaté indiquant le LVP et la raison, ou None si aucun LVP
        """
        return self.get_lvp_cc_total()

    ################################ MVP ################################

    def mvp_dash(self):
        """
        Identifie les MVP basés sur le nombre élevé de ruées d'attaque subies.

        Returns:
            str: Message MVP formaté, message de DPS faible, ou None
        """
        i_players, max_dash, _ = Analyzer.get_max_value(self.player_list, self.get_dash,
                                                        exclude=[self.is_heal, self.is_tank])
        mvp_names = self.players_to_string(i_players)

        if max_dash < 7:
            return self.get_bad_dps()
        else:
            self.add_mvps(i_players)
            if len(i_players) == 1:
                return language_config.selected_language["LARGOS MVP DASH S"].format(mvp_names=mvp_names, max_dash=max_dash)
            if len(i_players) > 1:
                return language_config.selected_language["LARGOS MVP DASH P"].format(mvp_names=mvp_names, max_dash=max_dash)

        return None

    def get_bad_dps(self, extra_exclude=None):
        """
        Identifie les DPS dont le dégât est inférieur à celui d'un support.

        Cette méthode est une surcharge spécifique à LARGOS.

        Args:
            extra_exclude (list, optional): Liste supplémentaire de fonctions de filtrage.

        Returns:
            str: Message formaté ou None si aucun joueur n'a un DPS faible
        """
        if extra_exclude is None:
            extra_exclude = []

        i_sup, sup_max_dmg, _ = Analyzer.get_max_value(self.player_list, self.get_dmg_boss, exclude=[self.is_dps])
        sup_name = self.players_to_string(i_sup)
        bad_dps = []

        for i in self.player_list:
            if any(filter_func(i) for filter_func in extra_exclude) or self.is_dead(i) or self.is_support(i):
                continue
            dps = self.get_dmg_boss(i)
            if dps < sup_max_dmg:
                if not (self.name == "QUOIDIMM" and self.get_player_spe(i) == "Spellbreaker"):
                    bad_dps.append(i)

        if bad_dps:
            self.add_mvps(bad_dps)
            bad_dps_name = self.players_to_string(bad_dps)
            if len(bad_dps) == 1:
                return language_config.selected_language["MVP BAD DPS S"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)
            else:
                return language_config.selected_language["MVP BAD DPS P"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)

        return None

    ################################ LVP ################################

    ################################ CONDITIONS ################################

    ################################ DATA MECHAS ################################

    def get_dash(self, i_player: int):
        """
        Récupère le nombre de ruées d'attaque subies par un joueur.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Nombre de ruées d'attaque subies
        """
        return self.get_mech_value(i_player, "Vapor Rush Charge")

    def get_dmg_boss(self, i_player: int):
        """
        Calcule les dégâts totaux infligés par un joueur contre les deux Largos.

        Args:
            i_player (int): Indice du joueur

        Returns:
            int: Dégâts totaux infligés
        """
        dmg = self.log.pjcontent['players'][i_player]['dpsTargets'][0][self.real_phase_id]['damage']
        dmg += self.log.pjcontent['players'][i_player]['dpsTargets'][1][self.real_phase_id]['damage']
        return dmg