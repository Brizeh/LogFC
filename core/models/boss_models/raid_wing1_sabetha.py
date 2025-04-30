# core/models/sub_models/raid_bosses/wing1.py
from typing import Optional, List, Dict, ClassVar

from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config, lang_dict
from utils.formatters import time_to_index
from utils.maths import get_dist


class SABETHA(Boss):
    """
    Sabetha (Wing 1, Boss 3)

    Ce boss est caractérisé par des phases de splits avec des adds importants
    et des mécaniques de bombes et de canons qui doivent être gérées correctement.
    """

    # Attributs de classe
    last: Optional['SABETHA'] = None  # Référence à la dernière instance créée
    name: ClassVar[str] = "SABETHA"
    wing: ClassVar[int] = 1
    boss_id: ClassVar[int] = 15375
    real_phase: ClassVar[str] = "Full Fight"

    # Positions et constantes pour les mécaniques
    pos_sab: List[float] = [376.7, 364.4]
    pos_canon1: List[float] = [346.9, 706.7]
    pos_canon2: List[float] = [35.9, 336.8]
    pos_canon3: List[float] = [403.3, 36.0]
    pos_canon4: List[float] = [713.9, 403.1]
    canon_detect_radius: float = 45.0
    scaler: float = 9.34179

    def __init__(self, log: Log) -> None:
        """
        Initialise un objet Sabetha.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SABETHA.last = self  # Met à jour la référence à la dernière instance

    def get_mvp(self) -> Optional[str]:
        """
        Détermine le joueur MVP pour Sabetha.
        Priorité: bon usage des bombes > bons dégâts sur les adds > bad DPS (excluant les canons)

        Returns:
            Message de récompense MVP ou None si aucun joueur ne se démarque
        """
        # Vérifier d'abord si des joueurs ont bien utilisé les bombes
        msg_terrorists = self.mvp_terrorists()
        if msg_terrorists:
            return msg_terrorists

        # Ensuite, vérifier les dégâts dans les phases de split
        msg_dmg_split = self.mvp_dmg_split()
        if msg_dmg_split:
            return msg_dmg_split

        # Enfin, vérifier les DPS sous-performants (en excluant les joueurs aux canons)
        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_cannon])
        if msg_bad_dps:
            return msg_bad_dps

        return None

    def get_lvp(self) -> str:
        """
        Détermine le joueur LVP pour Sabetha, basé sur les dégâts dans les phases de split.

        Returns:
            Message de pénalité LVP
        """
        return self.lvp_dmg_split()

    def get_dps_ranking(self) -> Dict[str, float]:
        """
        Calcule le classement DPS adapté pour Sabetha.
        Exclut les supports et les joueurs aux canons car ils ont un rôle spécifique.

        Returns:
            Dictionnaire des contributions DPS normalisées
        """
        return self._get_dps_contrib([self.is_support, self.is_cannon])

    ################################ MVP ################################

    def mvp_dmg_split(self) -> Optional[str]:
        """
        Identifie les joueurs qui ont fait le moins de dégâts pendant les phases d'adds.
        Ces joueurs sont considérés comme MVP car ils se sont concentrés sur les mécaniques.

        Returns:
            Message MVP pour les bons dégâts sur les adds ou None si personne ne se démarque
        """
        # Obtenir les joueurs qui ont fait le moins de dégâts dans les phases d'adds
        i_players, min_dmg, total_dmg = Analyzer.get_min_value(
            self.player_list,
            self.get_dmg_split,
            exclude=[self.is_support, self.is_cannon]
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
            return lang_dict["SABETHA MVP SPLIT"].format(
                mvp_names=mvp_names,
                dmg_ratio=dmg_ratio
            )

        return None

    def mvp_terrorists(self) -> Optional[str]:
        """
        Identifie les joueurs qui ont bien géré les bombes pendant le combat.
        Les "terroristes" sont les joueurs qui ont éloigné les bombes des autres joueurs.

        Returns:
            Message MVP pour les bons utilisateurs de bombes ou None si personne ne se démarque
        """
        # Obtenir la liste des joueurs qui ont bien géré les bombes
        i_players = self.get_terrorists()

        # Ajouter ces joueurs à la liste des MVP
        self.add_mvps(i_players)

        if i_players:
            # Préparer le message
            mvp_names = self.players_to_string(i_players)

            # Générer le message
            return lang_dict["SABETHA MVP BOMB"].format(mvp_names=mvp_names)

        return None

    ################################ LVP ################################

    def lvp_dmg_split(self) -> str:
        """
        Identifie les joueurs qui ont fait le plus de dégâts pendant les phases d'adds.
        Ces joueurs sont considérés comme LVP car ils se sont concentrés sur les dégâts
        au détriment des mécaniques.

        Returns:
            Message LVP pour les joueurs avec les dégâts les plus élevés sur les adds
        """
        # Obtenir les joueurs qui ont fait le plus de dégâts dans les phases d'adds
        i_players, max_dmg, total_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_split)

        # Préparer les variables pour le message
        lvp_names = self.players_to_string(i_players)
        dmg_ratio = max_dmg / total_dmg * 100

        # Ajouter ces joueurs à la liste des LVP
        self.add_lvps(i_players)

        # Générer le message
        return lang_dict["SABETHA LVP SPLIT"].format(
            lvp_names=lvp_names,
            dmg_ratio=dmg_ratio
        )

    ################################ CONDITIONS ###############################

    def is_cannon(self, i_player: int, n: int = 0) -> bool:
        """
        Vérifie si un joueur a géré un canon pendant le combat.

        Args:
            i_player: Indice du joueur
            n: Numéro du canon à vérifier (0 = tous, 1-4 = canon spécifique)

        Returns:
            True si le joueur a géré le(s) canon(s) spécifié(s), False sinon
        """
        # Récupérer les positions du joueur pendant le combat
        pos_player = self.get_player_pos(i_player)

        # Déterminer quels canons vérifier
        if n == 0:
            canon_pos = [
                SABETHA.pos_canon1,
                SABETHA.pos_canon2,
                SABETHA.pos_canon3,
                SABETHA.pos_canon4
            ]
        elif n == 1:
            canon_pos = [SABETHA.pos_canon1]
        elif n == 2:
            canon_pos = [SABETHA.pos_canon2]
        elif n == 3:
            canon_pos = [SABETHA.pos_canon3]
        elif n == 4:
            canon_pos = [SABETHA.pos_canon4]
        else:
            canon_pos = []

        # Vérifier si le joueur a été à proximité d'un canon
        for pos in pos_player:
            for canon in canon_pos:
                # Utiliser la fonction get_dist pour calculer la distance entre deux points
                if get_dist(pos, canon) <= SABETHA.canon_detect_radius:
                    return True

        return False

    def is_terrorist(self, i_player: int) -> bool:
        """
        Vérifie si un joueur a bien géré les bombes (en s'éloignant des autres joueurs).

        Args:
            i_player: Indice du joueur

        Returns:
            True si le joueur a bien géré les bombes, False sinon
        """
        # Récupérer l'historique des bombes pour ce joueur
        bomb_history = self.get_player_mech_history(i_player, ["Timed Bomb"])

        if bomb_history:
            # Récupérer les positions du joueur et la liste des autres joueurs
            poses = self.get_player_pos(i_player)
            players = self.player_list

            # Examiner chaque bombe
            for bomb in bomb_history:
                # Le joueur a 3 secondes après l'apparition de la bombe pour s'éloigner
                bomb_time = bomb['time'] + 3000
                time_index = time_to_index(bomb_time, self.time_base)

                try:
                    # Position du joueur au moment de l'explosion
                    bomb_pos = poses[time_index]
                except IndexError:
                    # Si l'indice est hors limites, passer à la bombe suivante
                    continue

                # Compter combien de joueurs sont à proximité de l'explosion
                bombed_players = 0
                for i in players:
                    # Ne pas compter le joueur lui-même ou les joueurs morts
                    if i == i_player or self.is_dead(i):
                        continue

                    # Position de ce joueur au moment de l'explosion
                    i_pos = self.get_player_pos(i)[time_index]

                    # Vérifier si ce joueur est dans le rayon de l'explosion (270 unités après scaling)
                    if get_dist(bomb_pos, i_pos) * SABETHA.scaler <= 270:
                        bombed_players += 1

                # Si le joueur a touché plus d'un autre joueur, ce n'est pas un bon terroriste
                if bombed_players > 1:
                    return True

        return False

    ################################ DATA MECHAS ################################

    def get_dmg_split(self, i_player: int) -> int:
        """
        Calcule les dégâts totaux faits par un joueur pendant les phases d'adds.

        Args:
            i_player: Indice du joueur

        Returns:
            Total des dégâts faits pendant les phases d'adds
        """
        try:
            # Récupérer les dégâts pour chacun des trois adds importants
            dmg_kernan = self.log.jcontent['phases'][2]['dpsStatsTargets'][i_player][0][0]
            dmg_mornifle = self.log.jcontent['phases'][5]['dpsStatsTargets'][i_player][0][0]
            dmg_karde = self.log.jcontent['phases'][7]['dpsStatsTargets'][i_player][0][0]

            # Additionner les dégâts des trois adds
            return dmg_kernan + dmg_mornifle + dmg_karde

        except (IndexError, KeyError, TypeError):
            # En cas d'erreur d'accès aux données
            return 0

    def get_terrorists(self) -> List[int]:
        """
        Identifie tous les joueurs qui ont bien géré les bombes pendant le combat.

        Returns:
            Liste des indices des joueurs qui ont bien géré les bombes
        """
        terrorists = []

        for i in self.player_list:
            if self.is_terrorist(i):
                terrorists.append(i)

        return terrorists