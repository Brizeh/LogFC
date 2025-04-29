# core/stats/analyzer.py
from typing import List, Callable, Tuple, Optional

from config.settings import BIG


class Analyzer:
    """
    Classe d'analyse statistique pour les rencontres de boss.
    Fournit des méthodes d'analyse des performances des joueurs.
    """

    @staticmethod
    def get_max_value(
            player_list: List[int],
            value_func: Callable[[int], float],
            exclude: Optional[List[Callable[[int], bool]]] = None
    ) -> Tuple[List[int], float, float]:
        """
        Trouve les joueurs ayant la valeur maximale pour une métrique donnée.

        Args:
            player_list: Liste des joueurs
            value_func: Fonction qui calcule la métrique pour un joueur
            exclude: Liste de fonctions de filtrage pour exclure certains joueurs

        Returns:
            Tuple de (indices des joueurs avec max, valeur maximale, valeur totale)
        """
        if exclude is None:
            exclude = []

        value_max = -1
        value_tot = 0
        i_maxs = []

        for i in player_list:
            value = value_func(i)
            value_tot += value

            if any(filter_func(i) for filter_func in exclude):
                continue

            if value > value_max:
                value_max = value
                i_maxs = [i]
            elif abs(value - value_max) < 1:
                i_maxs.append(i)

        if value_max == 0:
            return [], value_max, value_tot

        return i_maxs, value_max, value_tot

    @staticmethod
    def get_min_value(
            player_list: List[int],
            value_func: Callable[[int], float],
            exclude: Optional[List[Callable[[int], bool]]] = None
    ) -> Tuple[List[int], float, float]:
        """
        Trouve les joueurs ayant la valeur minimale pour une métrique donnée.

        Args:
            player_list: Liste des joueurs
            value_func: Fonction qui calcule la métrique pour un joueur
            exclude: Liste de fonctions de filtrage pour exclure certains joueurs

        Returns:
            Tuple de (indices des joueurs avec min, valeur minimale, valeur totale)
        """
        if exclude is None:
            exclude = []

        value_min = BIG
        value_tot = 0
        i_mins = []

        for i in player_list:
            value = value_func(i)
            value_tot += value

            if any(filter_func(i) for filter_func in exclude):
                continue

            if value < value_min:
                value_min = value
                i_mins = [i]
            elif abs(value - value_min) < 1:
                i_mins.append(i)

        return i_mins, value_min, value_tot

    @staticmethod
    def get_tot_value(
            player_list: List[int],
            value_func: Callable[[int], float],
            exclude: Optional[List[Callable[[int], bool]]] = None
    ) -> float:
        """
        Calcule la valeur totale d'une métrique pour tous les joueurs.

        Args:
            player_list: Liste des joueurs
            value_func: Fonction qui calcule la métrique pour un joueur
            exclude: Liste de fonctions de filtrage pour exclure certains joueurs

        Returns:
            La valeur totale de la métrique
        """
        if exclude is None:
            exclude = []

        value_tot = 0
        for i in player_list:
            if any(filter_func(i) for filter_func in exclude):
                continue

            value_tot += value_func(i)

        return value_tot