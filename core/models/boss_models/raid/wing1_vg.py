from typing import Optional, Dict, ClassVar

from core.models.boss import Boss
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config


class VG(Boss):
    """
    Vale Guardian (Wing 1, Boss 1)

    Ce boss est caractérisé par ses phases "bleues" où les joueurs doivent gérer
    des téléportations pour éviter des dégâts et assurer la mécanique des secteurs.
    """

    # Attributs de classe
    last: Optional['VG'] = None  # Référence à la dernière instance créée
    name: ClassVar[str] = "VG"
    wing: ClassVar[int] = 1
    boss_id: ClassVar[int] = 15438
    real_phase: ClassVar[str] = "Full Fight"

    def __init__(self, log: Log) -> None:
        """
        Initialise un objet Vale Guardian.

        Args:
            log: L'objet Log contenant les données du combat
        """
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        VG.last = self  # Met à jour la référence à la dernière instance

    def get_mvp(self) -> Optional[str]:
        """
        Détermine le joueur MVP pour Vale Guardian.
        Privilégie les joueurs qui ont fait les téléportations bleues.

        Returns:
            Message de récompense MVP ou None si aucun joueur ne se démarque
        """
        # Vérifier si quelqu'un a bien géré les téléportations bleues
        msg_bleu = self.mvp_bleu()
        if msg_bleu:
            return msg_bleu

        # Méthode par défaut des mauvais DPS si aucun MVP spécifique n'est trouvé
        return self.get_bad_dps(extra_exclude=[self.is_condi])

    def get_lvp(self) -> Optional[str]:
        """
        Détermine le joueur LVP pour Vale Guardian.
        Utilise le critère des dégâts par défaut.

        Returns:
            Message de pénalité LVP ou None si aucun joueur ne se démarque
        """
        return self.get_lvp_dps()

    def get_dps_ranking(self) -> Dict[str, float]:
        """
        Calcule le classement DPS adapté pour Vale Guardian.
        Exclut les supports et les joueurs condi car ils ont un rôle spécifique.

        Returns:
            Dictionnaire des contributions DPS normalisées
        """
        return self._get_dps_contrib([self.is_support, self.is_condi])

    ################################ MVP ################################   

    def mvp_bleu(self) -> Optional[str]:
        """
        Détermine si des joueurs méritent d'être MVP pour avoir géré les téléportations bleues.

        Returns:
            Message MVP pour les téléportations bleues ou None si personne ne se démarque
        """
        # Obtenir les joueurs qui ont fait le plus de téléportations bleues
        i_players, max_bleu, _ = Analyzer.get_max_value(self.player_list, self.get_bleu)

        # Si personne n'a fait de téléportations ou si les téléportations sont trop peu nombreuses
        if max_bleu < 3:
            # Vérifier plutôt si certains DPS ont sous-performé
            return self.get_bad_dps(extra_exclude=[self.is_condi])

        if max_bleu > 1:
            # Ajouter ces joueurs à la liste des MVP
            self.add_mvps(i_players)

            # Préparer les variables pour le message
            mvp_names = self.players_to_string(i_players)
            nb_players = len(i_players)

            if nb_players == 1:
                return language_config.selected_language["VG MVP BLEU S"].format(mvp_names=mvp_names, max_bleu=max_bleu)
            else:
                return language_config.selected_language["VG MVP BLEU P"].format(mvp_names=mvp_names, nb_players=nb_players, max_bleu=max_bleu)

        return None

    ################################ DATA MECHAS ################################

    def get_bleu(self, i_player: int) -> int:
        """
        Calcule le nombre total de téléportations bleues gérées par un joueur.

        La mécanique bleue comprend les téléportations dans les secteurs (Green Guard TP)
        et les téléportations sur le boss.

        Args:
            i_player: Indice du joueur

        Returns:
            Nombre total de téléportations bleues
        """
        # Les téléportations bleues sont comptabilisées sous deux mécaniques différentes
        bleu_split = self.get_mech_value(i_player, "Green Guard TP")
        bleu_boss = self.get_mech_value(i_player, "Boss TP")

        # La somme des deux donne le nombre total de téléportations bleues
        return bleu_boss + bleu_split