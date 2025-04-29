from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable, Tuple, ClassVar, TypeVar

import pytz

from config.settings import BOSS_DICT, CUSTOM_NAMES, ALL_PLAYERS, DATE_FORMAT, PARIS_TIMEZONE
from core.models.log import Log
from core.stats.analyzer import Analyzer
from i18n.languages import language_config
from utils.formatters import time_to_index

# Type pour les fonctions de filtrage des joueurs
PlayerFilter = Callable[[int], bool]
# Type pour les valeurs de retour des fonctions get_value
T = TypeVar('T', int, float)

class Boss:
    """
    Classe de base représentant une rencontre de boss dans Guild Wars 2.
    
    Cette classe encapsule la logique commune pour toutes les rencontres de boss,
    y compris l'analyse des logs, le suivi des joueurs et l'évaluation des performances.
    
    Attributes:
        name (str) : Nom du boss (doit être défini par les sous-classes)
        wing (int) : Numéro de l'aile où se trouve le boss (pour les raids)
        boss_id (int) : Identifiant unique du boss dans le jeu
        real_phase (str) : Phase principale à analyser pour les statistiques
    """
    
    # Attributs de classe par défaut, à surcharger dans les sous-classes
    name: ClassVar[Optional[str]] = None
    wing: ClassVar[int] = 0
    boss_id: ClassVar[int] = -1
    real_phase: ClassVar[str] = "Full Fight"

    # Constantes pour les IDs des buffs et mécaniques
    QUICK_ID: ClassVar[int] = 1187
    ALAC_ID: ClassVar[int] = 30328
    BANNER_IDS: ClassVar[List[int]] = [14449, 14417]
    FOOD_SWAP_ICON: ClassVar[str] = "https://wiki.guildwars2.com/images/d/d6/Champion_of_the_Crown.png"

    # Valeurs de seuil
    MIN_QUICK_CONTRIB: ClassVar[float] = 30
    MIN_ALAC_CONTRIB: ClassVar[float] = 30
    BUYER_DEATH_THRESHOLD: ClassVar[int] = 20000  # ms
    INSTANT_DEATH_TIME_DIFF: ClassVar[int] = 8000  # ms

    def __init__(self, log: Log) -> None:
        """
        Initialise une rencontre de boss à partir d'un objet Log.

        Args:
            log: L'objet Log contenant les données de la rencontre
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

        # Listes pour suivre les joueurs MVP et LVP
        self.mvp_accounts: List[str] = []
        self.lvp_accounts: List[str] = []

        # Initialiser les joueurs dans le dictionnaire global
        self._initialize_players()

    def _initialize_players(self) -> None:
        """
        Initialise les joueurs participant à cette rencontre dans le dictionnaire global.
        
        Pour chaque joueur, s'il existe déjà dans le dictionnaire ALL_PLAYERS,
        ajoute ce boss à son historique. Sinon, crée un nouveau joueur.
        """
        for i in self.player_list:
            account = self.get_player_account(i)
            player = ALL_PLAYERS.get(account)
            
            if not player:
                # Créer un nouveau joueur s'il n'existe pas encore
                from core.models.player import Player
                new_player = Player(self, account)
                ALL_PLAYERS[account] = new_player
            else:
                # Ajouter ce boss à l'historique du joueur
                player.add_boss(self)

    def __repr__(self) -> str:
        """
        Représentation textuelle du boss pour le débogage.

        Returns:
            URL du log
        """
        return self.log.url

    # -------------------------------------------------------------------------
    # Méthodes pour récupérer les attributs du boss
    # -------------------------------------------------------------------------

    def is_cm(self) -> bool:
        """
        Détermine si cette rencontre est en mode challenge (CM).

        Returns:
            True si le combat est en mode CM, False sinon
        """
        return self.log.pjcontent.get('isCM', False)

    def get_log_name(self) -> str:
        """
        Récupère le nom officiel de la rencontre depuis le log.

        Returns:
            Nom de la rencontre
        """
        return self.log.pjcontent.get('fightName', 'Unknown')

    def get_mechanics(self) -> List[Dict[str, Any]]:
        """
        Récupère les mécaniques du combat liées aux joueurs.

        Returns:
            Liste des mécaniques affectant les joueurs pendant le combat
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
        Récupère la durée totale du combat en millisecondes.

        Returns:
            Durée du combat en ms
        """
        return self.log.pjcontent.get('durationMS', 0)

    def get_start_date(self) -> datetime:
        """
        Récupère la date et l'heure de début du combat.

        Convertit l'horodatage de début en objet datetime,
        puis le convertit dans le fuseau horaire de Paris.

        Returns:
            Datetime au format fuseau horaire Paris
        """
        start_date_text = self.log.pjcontent.get('timeStartStd', '')
        if not start_date_text:
            return datetime.now(PARIS_TIMEZONE)

        try:
            start_date = datetime.strptime(start_date_text, DATE_FORMAT)
            return start_date.astimezone(PARIS_TIMEZONE)
        except ValueError:
            # En cas d'erreur de parsing
            return datetime.now(PARIS_TIMEZONE)
    
    def get_end_date(self) -> datetime:
        """
        Récupère la date et l'heure de fin du combat.
        
        Convertit l'horodatage de fin en objet datetime,
        puis le convertit dans le fuseau horaire de Paris.
        
        Returns:
            Datetime au format fuseau horaire Paris
        """
        end_date_text = self.log.pjcontent.get('timeEndStd', '')
        if not end_date_text:
            return datetime.now(PARIS_TIMEZONE)
            
        date_format = "%Y-%m-%d %H:%M:%S %z"
        try:
            end_date = datetime.strptime(end_date_text, date_format)
            return end_date.astimezone(PARIS_TIMEZONE)
        except ValueError:
            # En cas d'erreur de parsing
            start_date = self.get_start_date()
            return start_date + timedelta(milliseconds=self.duration_ms)

    def get_wingman_time(self) -> Optional[List[int]]:
        """
        Récupère les temps de référence Wingman pour ce boss.

        Interroge l'API Wingman pour obtenir les durées médianes et de référence
        pour ce boss, en fonction de son ID et du mode (CM ou normal).

        Returns:
            Liste contenant [temps_médian, temps_top] ou None en cas d'erreur
        """
        from services.api.wingman import WingmanAPI
        return WingmanAPI.get_boss_benchmark(self.boss_id, self.cm)

    def get_player_list(self) -> List[int]:
        """
        Récupère la liste des indices des joueurs participant au combat.

        Filtre les joueurs pour exclure ceux qui sont dans des groupes spéciaux (50+)
        et ceux qui sont détectés comme des acheteurs (pour les ventes de raids).

        Returns:
            Liste des indices des joueurs participants réels
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
        Récupère le percentile Wingman pour ce combat.

        Interroge l'API Wingman pour obtenir le percentile du combat actuel
        par rapport aux statistiques globales pour ce boss.

        Returns:
            Le percentile du combat ou None si non disponible
        """
        from services.api.wingman import WingmanAPI
        time_stamp = int(self.get_start_date().timestamp())
        return WingmanAPI.get_percentile(self.boss_id, self.cm, self.duration_ms, time_stamp)

    # -------------------------------------------------------------------------
    # Méthodes pour identifier les rôles des joueurs
    # -------------------------------------------------------------------------

    def is_quick(self, i_player: int) -> bool:
        """
        Vérifie si le joueur fournit un bon uptime de célérité.

        Un joueur est considéré comme fournisseur de célérité s'il
        génère au moins MIN_QUICK_CONTRIB % d'uptime sur la phase principale.

        Args:
            i_player: Indice du joueur à vérifier

        Returns:
            True si le joueur est fournisseur de célérité, False sinon
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
        Vérifie si le joueur fournit un bon uptime d'alacrity.

        Un joueur est considéré comme fournisseur d'alacrity s'il
        génère au moins MIN_ALAC_CONTRIB % d'uptime sur la phase principale.

        Args:
            i_player: Indice du joueur à vérifier

        Returns:
            True si le joueur est fournisseur d'alacrity, False sinon
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
        Vérifie si le joueur joue un rôle de support.

        Un joueur est considéré comme support s'il:
        - Fournit de la célérité
        - Fournit de l'alacrity
        - Est un Druid (avant le patch du 17/07/2022)
        - Est un Bannerslave (avant le patch du 17/07/2022)

        Args:
            i_player: Indice du joueur à vérifier

        Returns:
            True si le joueur est un support, False sinon
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return False

        prof = players[i_player].get('profession', '')

        # Support Druid avant le patch du 17 juillet 2022
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
        Vérifie si le joueur joue un rôle de DPS (dégâts).

        Un joueur est considéré comme DPS s'il n'est pas un support.

        Args:
            i_player: Indice du joueur à vérifier

        Returns:
            True si le joueur est un DPS, False sinon
        """
        return not self.is_support(i_player)

    def is_tank(self, i_player: int) -> bool:
        """
        Vérifie si le joueur joue un rôle de tank.

        Un joueur est considéré comme tank s'il a de la ténacité (toughness).

        Args:
            i_player: Indice du joueur à vérifier

        Returns:
            True si le joueur est un tank, False sinon
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return False

        return players[i_player].get('toughness', 0) > 0

    def is_heal(self, i_player: int) -> bool:
        """
        Vérifie si le joueur joue un rôle de healer.

        Un joueur est considéré comme healer s'il a du healing power.

        Args:
            i_player: Indice du joueur à vérifier

        Returns:
            True si le joueur est un healer, False sinon
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return False

        return players[i_player].get('healing', 0) > 0

    def is_dead(self, i_player: int) -> bool:
        """
        Vérifie si le joueur est mort pendant le combat.

        Args:
            i_player: Indice du joueur à vérifier

        Returns:
            True si le joueur est mort, False sinon
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
        Vérifie si le joueur est un acheteur (vente de raid).

        Un joueur est considéré comme acheteur s'il:
        - Meurt dans les premières 20 secondes du combat
        - N'a pas de données de rotation

        Args:
            i_player: Indice du joueur à vérifier

        Returns:
            True si le joueur est un acheteur, False sinon
        """
        player_name = self.get_player_name(i_player)
        mechanics = self.log.pjcontent.get('mechanics', [])

        # Vérifier si le joueur est mort tôt dans le combat
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

        # Vérifier si le joueur a des données de rotation
        try:
            rotation = self.get_player_rotation(i_player)
            if not rotation:
                return True
        except (KeyError, IndexError):
            return True

        return False

    def is_buff_up(self, i_player: int, target_time: int, buff_name: str) -> bool:
        """
        Vérifie si un buff spécifique était actif sur un joueur à un moment donné.

        Args:
            i_player: Indice du joueur à vérifier
            target_time: Temps (en ms) auquel vérifier le buff
            buff_name: Nom du buff à vérifier

        Returns:
            True si le buff était actif, False sinon
        """
        buffmap = self.log.pjcontent.get('buffMap', {})
        buff_id = None

        # Trouver l'ID du buff à partir de son nom
        for id_str, buff in buffmap.items():
            if buff.get('name') == buff_name:
                # Les IDs dans buffMap commencent par 'b', donc on enlève le 'b'
                try:
                    buff_id = int(id_str[1:])
                    break
                except ValueError:
                    continue

        if buff_id is None:
            return False

        # Trouver les données du buff pour ce joueur
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

        # Extraire les coordonnées temporelles et les états du buff
        xbuffplot = [pos[0] for pos in buff_data]
        ybuffplot = [pos[1] for pos in buff_data]

        # Trouver l'état du buff au moment cible
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
        Vérifie si le joueur est mort instantanément (sans être d'abord mis à terre).

        Un joueur est considéré comme mort instantanément si:
        - Il est mort sans être mis à terre auparavant
        - Il a été mis à terre mais est mort plus de 8 secondes après

        Args:
            i_player: Indice du joueur à vérifier

        Returns:
            True si le joueur est mort instantanément, False sinon
        """
        downs_deaths = self.get_player_mech_history(i_player, ["Downed", "Dead"])

        if not downs_deaths:
            return False

        # Vérifier si le dernier événement est une mort
        if downs_deaths[-1].get('name') == "Dead":
            # Mort sans être mis à terre
            if len(downs_deaths) == 1:
                return True

            # Mort longtemps après avoir été mis à terre
            if len(downs_deaths) > 1:
                time_diff = downs_deaths[-1].get('time', 0) - downs_deaths[-2].get('time', 0)
                if time_diff > self.INSTANT_DEATH_TIME_DIFF:
                    return True

        return False

    def is_condi(self, i_player: int) -> bool:
        """
        Vérifie si le joueur joue un build de dégâts sur la durée (condition damage).

        Un joueur est considéré comme condi si ses dégâts de condition sont supérieurs
        à ses dégâts directs.

        Args:
            i_player: Indice du joueur à vérifier

        Returns:
            True si le joueur est condi, False sinon
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
        Vérifie si le joueur joue un build de dégâts directs (power damage).

        Args:
            i_player: Indice du joueur à vérifier

        Returns:
            True si le joueur est power, False sinon
        """
        return not self.is_condi(i_player)

    def is_bannerslave(self, i_player: int) -> bool:
        """
        Vérifie si le joueur joue un Warrior/Berserker bannerslave.

        Applicable uniquement avant le patch du 17/07/2022.

        Args:
            i_player: Indice du joueur à vérifier

        Returns:
            True si le joueur est bannerslave, False sinon
        """
        pre_patch_date = datetime(2022, 7, 17, 23, 0, 0, tzinfo=pytz.FixedOffset(60))

        # Vérifier si le combat a eu lieu avant le patch
        if self.start_date >= pre_patch_date:
            return False

        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return False

        prof = players[i_player].get('profession', '')

        # Vérifier si le joueur est un Warrior/Berserker
        if prof not in ["Warrior", "Berserker"]:
            return False

        # Vérifier s'il a fourni des buffs de bannière
        group_buffs = players[i_player].get('groupBuffs', [])
        for buff in group_buffs:
            if buff.get('id') in self.BANNER_IDS:
                return True

        return False

    # -------------------------------------------------------------------------
    # Méthodes pour accéder aux données des joueurs
    # -------------------------------------------------------------------------

    def get_player_name(self, i_player: int) -> str:
        """
        Récupère le nom du joueur.

        Args:
            i_player: Indice du joueur

        Returns:
            Nom du joueur
        """
        return self.log.jcontent.get('players', [])[i_player].get('name', 'Unknown')

    def get_player_account(self, i_player: int) -> str:
        """
        Récupère le nom de compte du joueur.

        Args:
            i_player: Indice du joueur

        Returns:
            Nom de compte du joueur (format: name.1234)
        """
        return self.log.pjcontent.get('players', [])[i_player].get('account', 'Unknown')

    def get_player_pos(self, i_player: int, start: int = 0, end: Optional[int] = None) -> List[List[float]]:
        """
        Récupère les positions du joueur au cours du combat.

        Args:
            i_player: Indice du joueur
            start: Indice de début pour les positions
            end: Indice de fin pour les positions (None = jusqu'à la fin)

        Returns:
            Liste des positions [x, y, z] du joueur
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return []

        combat_data = players[i_player].get('combatReplayData', {})
        positions = combat_data.get('positions', [])

        return positions[start:end]

    def get_cc_boss(self, i_player: int) -> float:
        """
        Récupère les dégâts de barre de défiance infligés au boss par le joueur.

        Args:
            i_player: Indice du joueur

        Returns:
            Dégâts de barre de défiance infligés au boss
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
        Récupère les dégâts infligés au boss par le joueur.

        Args:
            i_player: Indice du joueur

        Returns:
            Dégâts infligés au boss
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
        Récupère les dégâts de barre de défiance infligés au total par le joueur.

        Args:
            i_player: Indice du joueur

        Returns:
            Dégâts de barre de défiance infligés au total
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
        Récupère l'indice d'un joueur à partir de son nom.

        Args:
            name: Nom du joueur à rechercher

        Returns:
            Indice du joueur ou None s'il n'est pas trouvé
        """
        players = self.log.pjcontent.get('players', [])

        for i_player, player in enumerate(players):
            if player.get('name') == name:
                return i_player

        return None

    def get_player_spe(self, i_player: int) -> str:
        """
        Récupère la spécialisation du joueur.

        Args:
            i_player: Indice du joueur

        Returns:
            Nom de la spécialisation
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return "Unknown"

        return players[i_player].get('profession', 'Unknown')

    def get_player_mech_history(self, i_player: int, mechs: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Récupère l'historique des mécaniques pour un joueur.

        Collecte tous les événements de mécanique qui ont affecté le joueur pendant le combat,
        avec possibilité de filtrer par types de mécaniques spécifiques.

        Args:
            i_player: Indice du joueur
            mechs: Liste des noms de mécaniques à filtrer (None = toutes)

        Returns:
            Liste des événements de mécanique pour le joueur, triée par temps
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
                    # Ajouter l'événement si mechs est vide ou si le nom de la mécanique est dans mechs
                    if not mechs or mech_name in mechs:
                        history.append({
                            "name": mech_name,
                            "time": data.get('time', 0)
                        })

        # Trier les événements par temps croissant
        history.sort(key=lambda event: event.get("time", 0))
        return history

    def players_to_string(self, i_players: List[int]) -> str:
        """
        Convertit une liste d'indices de joueurs en une chaîne formatée avec leurs noms.

        Utilise les noms personnalisés si disponibles, sinon utilise les noms des joueurs dans le log.
        Le résultat est formaté en Markdown pour l'affichage.

        Args:
            i_players: Liste des indices des joueurs

        Returns:
            Chaîne formatée avec les noms des joueurs
        """
        name_list = []

        for i in i_players:
            account = self.get_player_account(i)
            custom_name = CUSTOM_NAMES.get(account)

            if custom_name:
                name_list.append(custom_name)
            else:
                name_list.append(self.get_player_name(i))

        # Formater la chaîne de résultat en style Markdown
        return "__" + '__ / __'.join(name_list) + "__"

    def get_player_death_timer(self, i_player: int) -> Optional[int]:
        """
        Récupère le moment où le joueur est mort pendant le combat.

        Args:
            i_player: Indice du joueur

        Returns:
            Temps de mort en ms depuis le début du combat, ou None si le joueur n'est pas mort
        """
        if not self.is_dead(i_player):
            return None

        mech_history = self.get_player_mech_history(i_player, ["Dead"])

        if mech_history:
            # Renvoyer le temps de la dernière mort
            return mech_history[-1].get('time')

        return None

    def get_player_rotation(self, i_player: int) -> List[Dict[str, Any]]:
        """
        Récupère la rotation des compétences du joueur pendant le combat.

        Args:
            i_player: Indice du joueur

        Returns:
            Liste des compétences utilisées par le joueur
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return []

        return players[i_player].get('rotation', [])

    def time_entered_area(self, i_player: int, center: List[float], radius: float) -> Optional[int]:
        """
        Détermine le moment où le joueur est entré dans une zone circulaire.

        Args:
            i_player: Indice du joueur
            center: Coordonnées [x, y, z] du centre de la zone
            radius: Rayon de la zone

        Returns:
            Temps en ms depuis le début du combat, ou None si le joueur n'est jamais entré dans la zone
        """
        from utils.maths import get_dist

        poses = self.get_player_pos(i_player)
        if not poses:
            return None

        # Délai entre chaque position (ms)
        position_interval = 150

        for i, pos in enumerate(poses):
            if get_dist(pos, center) < radius:
                return i * position_interval

        return None

    def time_exited_area(self, i_player: int, center: List[float], radius: float) -> Optional[int]:
        """
        Détermine le moment où le joueur est sorti d'une zone circulaire après y être entré.

        Args:
            i_player: Indice du joueur
            center: Coordonnées [x, y, z] du centre de la zone
            radius: Rayon de la zone

        Returns:
            Temps en ms depuis le début du combat, ou None si le joueur n'est jamais sorti de la zone
        """
        from utils.maths import get_dist

        time_enter = self.time_entered_area(i_player, center, radius)
        if time_enter is None:
            return None

        # Délai entre chaque position (ms)
        position_interval = 150

        # Indice de la position d'entrée
        i_enter = int(time_enter / position_interval)

        # Récupérer les positions après l'entrée dans la zone
        poses = self.get_player_pos(i_player, start=i_enter)
        if not poses:
            return None

        for i, pos in enumerate(poses):
            if get_dist(pos, center) > radius:
                return (i + i_enter) * position_interval

        return None

    def add_mvps(self, players: List[int]) -> None:
        """
        Ajoute des joueurs à la liste des MVP (Most Valuable Players) pour ce combat.

        Incrémente également le compteur de MVP pour chaque joueur dans le dictionnaire global.

        Args:
            players: Liste des indices des joueurs à ajouter comme MVP
        """
        # Récupérer les comptes des joueurs MVP
        self.mvp_accounts = [self.get_player_account(i) for i in players]

        # Incrémenter le compteur de MVP pour chaque joueur
        for i in players:
            account = self.get_player_account(i)
            player = ALL_PLAYERS.get(account)
            if player:
                player.mvps += 1

    def add_lvps(self, players: List[int]) -> None:
        """
        Ajoute des joueurs à la liste des LVP (Least Valuable Players) pour ce combat.

        Incrémente également le compteur de LVP pour chaque joueur dans le dictionnaire global.

        Args:
            players: Liste des indices des joueurs à ajouter comme LVP
        """
        # Récupérer les comptes des joueurs LVP
        self.lvp_accounts = [self.get_player_account(i) for i in players]

        # Incrémenter le compteur de LVP pour chaque joueur
        for i in players:
            account = self.get_player_account(i)
            player = ALL_PLAYERS.get(account)
            if player:
                player.lvps += 1

    def _get_dps_contrib(self, exclude: List[PlayerFilter] = None) -> Dict[str, float]:
        """
        Calcule la contribution en dégâts de chaque joueur, normalisée sur une échelle de 0 à 20.

        Cette méthode permet d'obtenir une représentation relative des performances en dégâts,
        où le joueur ayant fait le plus de dégâts obtient 20 points, et les autres sont
        évalués proportionnellement.

        Args:
            exclude: Liste des fonctions de filtrage pour exclure certains joueurs

        Returns:
            Dictionnaire associant les comptes des joueurs à leur contribution normalisée
        """
        if exclude is None:
            exclude = []

        dps_ranking = {}
        max_dps = 0

        # Calculer les dégâts pour chaque joueur et trouver le maximum
        for i in self.player_list:
            # Ignorer les joueurs exclus par les filtres
            if any(filter_func(i) for filter_func in exclude):
                continue

            try:
                # Récupérer les dégâts pour la phase principale
                player_dps = self.get_dmg_boss(i)

                # Mettre à jour le maximum
                if player_dps > max_dps:
                    max_dps = player_dps

                # Stocker les dégâts du joueur
                dps_ranking[self.get_player_account(i)] = player_dps
            except (KeyError, IndexError):
                continue

        # Normaliser les valeurs sur une échelle de 0 à 20
        if max_dps > 0:
            for player in dps_ranking:
                dps_ranking[player] = 20.0 * dps_ranking[player] / max_dps

        return dps_ranking

    def get_dps_ranking(self) -> Dict[str, float]:
        """
        Récupère le classement des joueurs DPS selon leur contribution en dégâts.

        Les joueurs de support sont exclus de ce classement.

        Returns:
            Dictionnaire associant les comptes des joueurs à leur contribution normalisée
        """
        return self._get_dps_contrib([self.is_support])

    def get_player_group(self, i_player: int) -> int:
        """
        Récupère le numéro du groupe auquel appartient le joueur.

        Args:
            i_player: Indice du joueur

        Returns:
            Numéro du groupe
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return 0

        return players[i_player].get('group', 0)

    def get_foodswap_count(self, i_player: int) -> int:
        """
        Compte le nombre de fois où le joueur a changé de nourriture pendant le combat.

        Détecte les changements de buff de nourriture en cherchant l'icône spécifique.

        Args:
            i_player: Indice du joueur

        Returns:
            Nombre de changements de nourriture
        """
        players = self.log.pjcontent.get('players', [])
        if i_player >= len(players):
            return 0

        buff_map = self.log.pjcontent.get('buffMap', {})
        buff_uptimes = players[i_player].get('buffUptimes', [])

        # IDs des buffs de nourriture
        food_swap_ids = []

        # Identifier les buffs de nourriture par leur icône
        for buff_name, data in buff_map.items():
            if data.get('icon') == self.FOOD_SWAP_ICON:
                try:
                    # Les IDs dans buffMap commencent par 'b', donc on enlève le 'b'
                    food_swap_ids.append(int(buff_name[1:]))
                except ValueError:
                    continue

        food_swap_count = 0

        # Compter les changements d'état de chaque buff de nourriture
        for buff in buff_uptimes:
            if buff.get('id') in food_swap_ids:
                states = buff.get('states', [])
                for state in states:
                    # L'état 1 indique que le buff est actif
                    if len(state) > 1 and state[1] == 1:
                        food_swap_count += 1

        return food_swap_count

    # -------------------------------------------------------------------------
    # "MVP"
    # -------------------------------------------------------------------------

    def get_mvp_cc_boss(self, extra_exclude: List[Callable[[int], bool]] = None) -> Optional[str]:
        """
        Identifie et récompense les joueurs avec la meilleure contribution au contrôle du boss (CC).

        Trouve les joueurs qui ont fourni la valeur minimum de CC sur le boss principal,
        les ajoute à la liste des MVP et génère un message formaté pour le rapport.

        Args:
            extra_exclude: Liste de fonctions de filtrage supplémentaires pour exclure certains joueurs

        Returns:
            Message formaté pour le rapport, ou None si aucun CC n'a été fait
        """
        if extra_exclude is None:
            extra_exclude = []

        # Obtenir les joueurs avec la contribution CC minimale
        i_players, min_cc, total_cc = Analyzer.get_min_value(self.player_list, self.get_cc_boss, exclude=extra_exclude)

        # Si aucun joueur n'a fait de CC, ne pas générer de message
        if total_cc == 0:
            return None

        # Ajouter ces joueurs à la liste des MVP
        self.add_mvps(i_players)

        # Préparer les variables pour le message
        mvp_names = self.players_to_string(i_players)
        cc_ratio = min_cc / total_cc * 100
        number_mvp = len(i_players)

        # Sélectionner le message approprié en fonction du nombre de MVP et de la valeur de CC
        lang_dict = language_config.selected_language

        if min_cc == 0:
            if number_mvp == 1:
                return lang_dict["MVP BOSS 0 CC S"].format(mvp_names=mvp_names)
            else:
                return lang_dict["MVP BOSS 0 CC P"].format(mvp_names=mvp_names)
        else:
            if number_mvp == 1:
                return lang_dict["MVP BOSS CC S"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            else:
                return lang_dict["MVP BOSS CC P"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)

    def get_mvp_cc_total(self, extra_exclude: List[Callable[[int], bool]] = None) -> Optional[str]:
        """
        Identifie et récompense les joueurs avec la meilleure contribution au contrôle total (CC).

        Trouve les joueurs qui ont fourni la valeur minimum de CC au total (boss + adds),
        les ajoute à la liste des MVP et génère un message formaté pour le rapport.

        Args:
            extra_exclude: Liste de fonctions de filtrage supplémentaires pour exclure certains joueurs

        Returns:
            Message formaté pour le rapport, ou None si aucun CC n'a été fait
        """
        if extra_exclude is None:
            extra_exclude = []

        # Obtenir les joueurs avec la contribution CC minimale
        i_players, min_cc, total_cc = Analyzer.get_min_value(self.player_list, self.get_cc_total, exclude=extra_exclude)

        # Si aucun joueur n'a fait de CC, ne pas générer de message
        if total_cc == 0:
            return None

        # Ajouter ces joueurs à la liste des MVP
        self.add_mvps(i_players)

        # Préparer les variables pour le message
        mvp_names = self.players_to_string(i_players)
        cc_ratio = min_cc / total_cc * 100
        number_mvp = len(i_players)

        # Sélectionner le message approprié en fonction du nombre de MVP et de la valeur de CC
        lang_dict = language_config.selected_language

        if min_cc == 0:
            if number_mvp == 1:
                return lang_dict["MVP TOTAL 0 CC S"].format(mvp_names=mvp_names)
            else:
                return lang_dict["MVP TOTAL 0 CC P"].format(mvp_names=mvp_names)
        else:
            if number_mvp == 1:
                return lang_dict["MVP TOTAL CC S"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            else:
                return lang_dict["MVP TOTAL CC P"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)

    def get_bad_dps(self, extra_exclude: List[Callable[[int], bool]] = None) -> Optional[str]:
        """
        Identifie les joueurs DPS qui font moins de dégâts qu'un support.

        Cette méthode recherche les joueurs de support ayant fait le plus de dégâts,
        puis identifie les joueurs DPS dont les dégâts sont inférieurs à ce support.
        Ces joueurs DPS sont considérés comme sous-performants et sont ajoutés à la liste des MVP
        (ironiquement) pour souligner leur besoin d'amélioration.

        Args:
            extra_exclude: Liste de fonctions de filtrage supplémentaires pour exclure certains joueurs

        Returns:
            Message formaté pour le rapport, ou None si aucun DPS n'est sous-performant
        """
        if extra_exclude is None:
            extra_exclude = []

        # Trouver le support avec les dégâts les plus élevés
        i_sup, sup_max_dmg, _ = Analyzer.get_max_value(
            self.player_list,
            self.get_dmg_boss,
            exclude=[self.is_dps, self.is_bannerslave]
        )

        sup_name = self.players_to_string(i_sup)
        bad_dps = []

        # Identifier les joueurs DPS qui font moins de dégâts que le meilleur support
        for i in self.player_list:
            # Exclure les joueurs qui ne sont pas pertinents pour cette analyse
            should_exclude = (
                    (extra_exclude and any(filter_func(i) for filter_func in extra_exclude)) or
                    self.is_dead(i) or
                    self.is_support(i) or
                    self.is_bannerslave(i)
            )

            if should_exclude:
                continue

            dps = self.get_dmg_boss(i)

            # Vérifier si ce DPS fait moins de dégâts que le meilleur support
            if dps < sup_max_dmg:
                # Exception spéciale pour les Spellbreakers sur le boss QUOIDIMM
                if not (self.name == "QUOIDIMM" and self.get_player_spe(i) == "Spellbreaker"):
                    bad_dps.append(i)

        # S'il y a des DPS sous-performants, générer un message
        if bad_dps:
            self.add_mvps(bad_dps)
            bad_dps_name = self.players_to_string(bad_dps)

            lang_dict = language_config.selected_language

            if len(bad_dps) == 1:
                return lang_dict["MVP BAD DPS S"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)
            else:
                return lang_dict["MVP BAD DPS P"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)

        return None

    # -------------------------------------------------------------------------
    # "LVP"
    # -------------------------------------------------------------------------

    def get_lvp_cc_boss(self) -> Optional[str]:
        """
        Identifie et pénalise les joueurs avec la pire contribution au contrôle du boss (CC).

        Trouve les joueurs qui ont fourni la valeur maximum de CC sur le boss principal,
        les ajoute à la liste des LVP et génère un message formaté pour le rapport.

        Returns:
            Message formaté pour le rapport, ou None si aucun CC n'a été fait
        """
        # Obtenir les joueurs avec la contribution CC maximale
        i_players, max_cc, total_cc = Analyzer.get_max_value(self.player_list, self.get_cc_boss)

        # Si aucun joueur n'a fait de CC, ne pas générer de message
        if total_cc == 0:
            return None

        # Ajouter ces joueurs à la liste des LVP
        self.add_lvps(i_players)

        # Préparer les variables pour le message
        lvp_names = self.players_to_string(i_players)
        cc_ratio = max_cc / total_cc * 100

        # Générer le message
        lang_dict = language_config.selected_language
        return lang_dict["LVP BOSS CC"].format(lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)

    def get_lvp_cc_total(self) -> Optional[str]:
        """
        Identifie et pénalise les joueurs avec la pire contribution au contrôle total (CC).

        Trouve les joueurs qui ont fourni la valeur maximum de CC au total (boss + adds),
        les ajoute à la liste des LVP et génère un message formaté pour le rapport.

        Returns:
            Message formaté pour le rapport, ou None si aucun CC n'a été fait
        """
        # Obtenir les joueurs avec la contribution CC maximale
        i_players, max_cc, total_cc = Analyzer.get_max_value(self.player_list, self.get_cc_total)

        # Si aucun joueur n'a fait de CC, ne pas générer de message
        if total_cc == 0:
            return None

        # Ajouter ces joueurs à la liste des LVP
        self.add_lvps(i_players)

        # Préparer les variables pour le message
        lvp_names = self.players_to_string(i_players)
        cc_ratio = max_cc / total_cc * 100

        # Générer le message
        lang_dict = language_config.selected_language
        return lang_dict["LVP TOTAL CC"].format(lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)

    def get_lvp_dps(self) -> str:
        """
        Identifie et pénalise les joueurs avec la pire contribution aux dégâts.

        Trouve les joueurs qui ont fait le plus de dégâts au boss,
        les ajoute à la liste des LVP et génère un message formaté pour le rapport.
        Cette méthode vérifie également si le joueur a changé de nourriture fréquemment,
        ce qui peut expliquer sa mauvaise performance.

        Returns:
            Message formaté pour le rapport
        """
        # Obtenir les joueurs avec les dégâts maximaux
        i_players, max_dmg, total_dmg = Analyzer.get_max_value(self.player_list, self.get_dmg_boss)

        # Calculer les statistiques supplémentaires
        dmg_ratio = max_dmg / total_dmg * 100 if total_dmg > 0 else 0
        lvp_dps_name = self.players_to_string(i_players)
        dps = max_dmg * 1000 / self.duration_ms if self.duration_ms > 0 else 0

        # Vérifier les changements de nourriture
        food_swap_count = self.get_foodswap_count(i_players[0]) if i_players else 0

        # Ajouter ces joueurs à la liste des LVP
        self.add_lvps(i_players)

        # Générer le message approprié en fonction des changements de nourriture
        lang_dict = language_config.selected_language

        if food_swap_count:
            return lang_dict["LVP DPS FOODSWAP"].format(
                lvp_dps_name=lvp_dps_name,
                max_dmg=max_dmg,
                dmg_ratio=dmg_ratio,
                dps=dps,
                foodSwapCount=food_swap_count
            )
        else:
            return lang_dict["LVP DPS"].format(
                lvp_dps_name=lvp_dps_name,
                max_dmg=max_dmg,
                dmg_ratio=dmg_ratio,
                dps=dps
            )

    # -------------------------------------------------------------------------
    # Données liées au boss
    # -------------------------------------------------------------------------

    def get_pos_boss(self, start: int = 0, end: Optional[int] = None) -> List[List[float]]:
        """
        Récupère les positions du boss principal au cours du combat.

        Parcourt les cibles (targets) pour trouver celle qui correspond à un boss connu
        et renvoie ses positions.

        Args:
            start: Indice de début pour les positions (défaut = 0)
            end: Indice de fin pour les positions (None = jusqu'à la fin)

        Returns:
            Liste des positions [x, y, z] du boss

        Raises:
            ValueError: Si aucun boss n'est trouvé dans les cibles
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
        Récupère les temps de début et de fin d'une phase spécifique du combat.

        Args:
            target_phase: Nom de la phase à rechercher
            in_milliseconds: Si True, renvoie les temps en millisecondes,
                            sinon en indices de position

        Returns:
            Tuple (début, fin) représentant les temps ou indices de la phase

        Raises:
            ValueError: Si la phase n'est pas trouvée
        """
        phases = self.log.pjcontent.get('phases', [])

        for phase in phases:
            if phase.get('name') == target_phase:
                start = phase.get('start', 0)
                end = phase.get('end', 0)

                if in_milliseconds:
                    return start, end

                # Convertir en indices de position
                return time_to_index(start, self.time_base), time_to_index(end, self.time_base)

        raise ValueError(f'Phase "{target_phase}" not found')

    def get_mech_value(self, i_player: int, mech_name: str, phase: str = "Full Fight") -> int:
        """
        Récupère le nombre d'occurrences d'une mécanique pour un joueur dans une phase donnée.

        Args:
            i_player: Indice du joueur
            mech_name: Nom de la mécanique à rechercher
            phase: Nom de la phase (défaut = "Full Fight")

        Returns:
            Nombre d'occurrences de la mécanique pour ce joueur
        """
        phase_id = self.get_phase_id(phase)

        # Créer la liste des noms de mécaniques
        mechs_list = []
        for mech in self.mechanics:
            mechs_list.append(mech.get('name', ''))

        # Vérifier si la mécanique existe
        if mech_name in mechs_list:
            i_mech = mechs_list.index(mech_name)

            try:
                # Accéder aux statistiques de mécanique avec vérification des indices
                phases = self.log.jcontent.get('phases', [])
                if phase_id < len(phases):
                    mech_stats = phases[phase_id].get('mechanicStats', [])

                    if i_player < len(mech_stats) and i_mech < len(mech_stats[i_player]):
                        return mech_stats[i_player][i_mech][0]
            except (IndexError, KeyError, TypeError):
                # En cas d'erreur, retourner 0
                pass

        return 0

    def boss_hp_to_time(self, hp: float) -> Optional[int]:
        """
        Convertit un pourcentage de santé du boss en temps écoulé depuis le début du combat.

        Cette méthode trouve le premier moment où le boss a atteint un pourcentage de santé
        inférieur à la valeur spécifiée.

        Args:
            hp: Pourcentage de santé du boss (0-100)

        Returns:
            Temps en ms où le boss avait ce pourcentage de santé, ou None si non trouvé
        """
        targets = self.log.pjcontent.get('targets', [])
        if not targets:
            return None

        hp_percents = targets[0].get('healthPercents', [])

        for timer in hp_percents:
            # Vérifier que timer est une liste avec au moins 2 éléments
            if isinstance(timer, list) and len(timer) > 1:
                if timer[1] < hp:
                    return timer[0]

        return None

    def get_mechanic_history(self, name: str) -> List[Dict[str, Any]]:
        """
        Récupère l'historique complet d'une mécanique spécifique pendant le combat.

        Args:
            name: Nom complet de la mécanique

        Returns:
            Liste des occurrences de la mécanique, ou liste vide si non trouvée
        """
        mechanics = self.log.pjcontent.get('mechanics', [])

        for mech in mechanics:
            if mech.get('fullName') == name:
                return mech.get('mechanicsData', [])

        return []

    def get_phase_id(self, name: str) -> int:
        """
        Récupère l'identifiant d'une phase du combat à partir de son nom.

        Args:
            name: Nom de la phase

        Returns:
            ID de la phase, ou 0 si non trouvée
        """
        phases = self.log.pjcontent.get('phases', [])

        for i, phase in enumerate(phases):
            if phase.get('name') == name:
                return i

        return 0

    def get_time_base(self) -> int:
        """
        Calcule l'intervalle de temps entre chaque position enregistrée.

        Cette valeur est utilisée pour convertir les indices de position en timestamps.
        Elle représente le rapport entre la durée totale du combat et le nombre de positions
        enregistrées.

        Returns:
            Intervalle de temps en millisecondes
        """
        players = self.log.pjcontent.get('players', [])
        if not players:
            return 150  # Valeur par défaut

        # Accéder au premier joueur pour obtenir les données de replay
        combat_data = players[0].get('combatReplayData', {})
        start = combat_data.get('start', 0)
        end = combat_data.get('end', 0)
        positions = combat_data.get('positions', [])

        if not positions or end <= start:
            return 150  # Valeur par défaut

        # Calculer l'intervalle en divisant la durée totale par le nombre de positions
        delta = end - start
        return int(delta / len(positions))
