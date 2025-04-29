# LogFC-Testing
## How to ? :
###  - Put all links in "src/input_logs.txt"
###  - Run.bat
## You can add custom names :
### - associate anet_accounts with some nicknames in src/custom_names.json

## Library architecture
````text
projet/
├── README.md
├── config/
│   ├── __init__.py
│   └── settings.py             # Constantes, configurations, paramètres par défaut
├── core/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── log.py              # Représente un fichier log
│   │   ├── player.py           # Classe Player et comportements associés
│   │   └── boss.py             # Classe Boss (déplacée de boss_class.py)
│   │   └── sub_models/
│   │       ├── __init__.py
│   │       ├── raid_bosses.py   # Classes spécifiques aux boss de raid
│   │       ├── ibs_bosses.py    # Classes spécifiques aux boss d'IBS
│   │       ├── eod_bosses.py    # Classes spécifiques aux boss d'EOD
│   │       ├── soto_bosses.py   # Classes spécifiques aux boss de SOTO
│   │       └── frac_bosses.py   # Classes spécifiques aux boss de fractales
│   ├── factories/
│   │   ├── __init__.py
│   │   └── boss_factory.py     # Crée les instances de boss spécifiques
│   └── stats/
│       ├── __init__.py
│       └── analyzer.py         # Logique d'analyse des stats (déplacée de la classe Stats)
├── services/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── wingman.py          # Interactions avec l'API Wingman
│   │   └── dps_report.py       # Interactions avec l'API DPS Report
│   └── parsers/
│       ├── __init__.py
│       └── input_parser.py     # Parsing des entrées utilisateur
├── utils/
│   ├── __init__.py
│   ├── formatters.py           # Fonctions de formatage (disp_time etc.)
│   ├── maths.py                # Fonctions utilitaires pour les calculs
│   └── analyzer.py             # Outils d'analyse statistique
├── i18n/
│   ├── __init__.py
│   └── languages.py            # Gestion des langues et traductions
├── views/
│   ├── __init__.py
│   └── report_generator.py     # Génération de rapports (remplace func.get_message_reward)
└── main.py                     # Point d'entrée principal

````