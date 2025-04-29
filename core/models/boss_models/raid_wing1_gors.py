from typing import Optional, List, ClassVar

from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class GORS(Boss):
    """
    Gorseval (Wing 1, Boss 2)

    Ce boss est caractérisé par ses phases de split où les joueurs doivent gérer
    des orbes et des spectres, ainsi que par la mécanique "egged" qui peut causer
    des problèmes significatifs.
    """

    # Attributs de classe
    last: Optional['GORS'] = None  # Référence à la dernière instance créée
    name: ClassVar[str] = "GORSEVAL"
    wing: ClassVar[int] = 1
    boss_id: ClassVar[int] = 15429
    real_phase: ClassVar[str] = "Full Fight"

    def __init__(self, log: Log) -> None:
        """
        Initialise un objet Gorseval.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        GORS.last = self  # Met à jour la référence à la dernière instance

    def get_mvp(self) -> Optional[str]:
        """
        Détermine le joueur MVP pour Gorseval.
        Priorité: joueurs egged > dégâts dans les phases de split > bad DPS

        Returns:
            Message de récompense MVP ou None si aucun joueur ne se démarque
        """
        # Vérifier d'abord si des joueurs ont été "egged"
        msg_egg = self.mvp_egg()
        if msg_egg:
            return msg_egg

        # Ensuite, vérifier les dégâts dans les phases de split
        msg_dmg_split = self.mvp_dmg_split()
        if msg_dmg_split:
            return msg_dmg_split

        # Enfin, vérifier les DPS sous-performants
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self) -> str:
        """
        Détermine le joueur LVP pour Gorseval, basé sur les dégâts dans les phases de split.

        Returns:
            Message de pénalité LVP
        """
        return self.lvp_dmg_split()

    ################################ MVP ################################

    def mvp_dmg_split(self) -> Optional[str]:
        """
        Identifie les joueurs qui ont fait le moins de dégâts pendant les phases de split.
        Ces joueurs sont considérés comme MVP car ils se sont concentrés sur les mécaniques.

        Returns:
            Message MVP pour les bons dégâts en phase de split ou None si personne ne se démarque
        """
        # Obtenir les joueurs qui ont fait le moins de dégâts dans les phases de split
        i_players, min_dmg, total_dmg = Analyzer.get_min_value(
            self.player_list,
            self.get_dmg_split,
            exclude=[self.is_support]
        )

        # Calculer le total des dégâts des joueurs DPS
        dps_total_dmg = Analyzer.get_tot_value(
            self.player_list,
            self.get_dmg_split,
            exclude=[self.is_support]
        )

        # Si les dégâts sont significativement bas (moins de 75% de la part attendue)
        if min_dmg / dps_total_dmg < 1 / 6 * 0.75:
            # Ajouter ces joueurs à la liste des MVP
            self.add_mvps(i_players)

            # Préparer les variables pour le message
            mvp_names = self.players_to_string(i_players)
            dmg_ratio = min_dmg / total_dmg * 100

            # Générer le message
            lang_dict = language_config.selected_language
            return lang_dict["GORS MVP SPLIT"].format(
                mvp_names=mvp_names,
                min_dmg=min_dmg,
                dmg_ratio=dmg_ratio
            )

        return None

    def mvp_egg(self) -> Optional[str]:
        """
        Identifie les joueurs qui ont été "egged" pendant le combat.
        Cette mécanique est importante et mérite d'être soulignée.

        Returns:
            Message MVP pour les joueurs egged ou None si personne n'a été egged
        """
        # Obtenir la liste des joueurs qui ont été "egged"
        i_players = self.get_egged()

        if i_players:
            # Ajouter ces joueurs à la liste des MVP
            self.add_mvps(i_players)

            # Préparer le message
            mvp_names = self.players_to_string(i_players)
            lang_dict = language_config.selected_language

            # Sélectionner le message approprié en fonction du nombre de joueurs
            if len(i_players) == 1:
                return lang_dict["GORS MVP EGG S"].format(mvp_names=mvp_names)
            else:
                return lang_dict["GORS MVP EGG P"].format(mvp_names=mvp_names)

        return None

    ################################ LVP ################################

    def lvp_dmg_split(self) -> str:
        """
        Identifie les joueurs qui ont fait le plus de dégâts pendant les phases de split.
        Ces joueurs sont considérés comme LVP car ils se sont concentrés sur les dégâts
        au détriment des mécaniques.

        Returns:
            Message LVP pour les joueurs avec les dégâts les plus élevés en phase de split
        """
        # Obtenir les joueurs qui ont fait le plus de dégâts dans les phases de split
        i_players, max_dmg, total_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_split)

        # Préparer les variables pour le message
        lvp_names = self.players_to_string(i_players)
        dmg_ratio = max_dmg / total_dmg * 100

        # Ajouter ces joueurs à la liste des LVP
        self.add_lvps(i_players)

        # Générer le message
        lang_dict = language_config.selected_language
        return lang_dict["GORS LVP SPLIT"].format(
            lvp_names=lvp_names,
            max_dmg=max_dmg,
            dmg_ratio=dmg_ratio
        )

    ################################ CONDITIONS ###############################

    def got_egged(self, i_player: int) -> bool:
        """
        Vérifie si un joueur a été touché par la mécanique "Egged".

        Args:
            i_player: Indice du joueur

        Returns:
            True si le joueur a été touché par la mécanique, False sinon
        """
        return self.get_mech_value(i_player, "Egged") > 0

    ################################ DATA MECHAS ################################

    def get_dmg_split(self, i_player: int) -> int:
        """
        Calcule les dégâts totaux faits par un joueur pendant les phases de split.

        Args:
            i_player: Indice du joueur

        Returns:
            Total des dégâts faits durant les phases de split
        """
        dmg_split = 0

        try:
            # Récupérer les statistiques de dégâts pour les deux phases de split
            dmg_split_1 = self.log.jcontent['phases'][3]['dpsStatsTargets'][i_player]
            dmg_split_2 = self.log.jcontent['phases'][6]['dpsStatsTargets'][i_player]

            # Additionner les dégâts de toutes les cibles dans les deux phases
            for add_split1, add_split2 in zip(dmg_split_1, dmg_split_2):
                dmg_split += add_split1[0] + add_split2[0]

        except (IndexError, KeyError, TypeError):
            # En cas d'erreur d'accès aux données
            return 0

        return dmg_split

    def get_egged(self) -> List[int]:
        """
        Identifie tous les joueurs qui ont été touchés par la mécanique "Egged".

        Returns:
            Liste des indices des joueurs qui ont été egged
        """
        egged = []

        for i in self.player_list:
            if self.got_egged(i):
                egged.append(i)

        return egged