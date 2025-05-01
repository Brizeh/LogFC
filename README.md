# LogFC-Testing
## How to ? :
###  - Put all links in "src/input_logs.txt"
###  - Run.bat
## You can add custom names :
### - associate anet_accounts with some nicknames in src/custom_names.json

## Library architecture
````text
LogFC/
├── README.md
├── config/
│   ├── __init__.py
│   └── settings.py             # Constants, configurations, default parameters
├── core/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── log.py              # Represents a log file
│   │   ├── player.py           # Player class and associated behaviors
│   │   ├── boss.py             # Base Boss class with common functionality
│   │   └── boss_models/        # Organized boss models by content type
│   │       ├── __init__.py
│   │       ├── golem.py        # Golem-specific implementation
│   │       ├── raid/           # Raid bosses organized by wings
│   │       │   ├── __init__.py
│   │       │   ├── wing1_vg.py
│   │       │   ├── wing1_gors.py
│   │       │   └── ... 
│   │       ├── fractals/       # Fractal bosses
│   │       │   └── ...
│   │       ├── eod/            # End of Dragons bosses
│   │       │   └── ...
│   │       ├── ibs/            # Icebrood Saga bosses
│   │       │   └── ...
│   │       └── soto/           # Secrets of the Obscure bosses
│   │           └── ...
│   ├── factories/
│   │   ├── __init__.py
│   │   └── boss_factory.py     # Creates specific boss instances
│   └── stats/
│       ├── __init__.py
│       └── analyzer.py         # Stats analysis logic (moved from Stats class)
├── services/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── wingman.py          # Interactions with Wingman API
│   │   └── dps_report.py       # Interactions with DPS Report API
│   └── parsers/
│       ├── __init__.py
│       └── input_parser.py     # Parsing user inputs
├── utils/
│   ├── __init__.py
│   ├── formatters.py           # Formatting functions (disp_time etc.)
│   ├── maths.py                # Utility functions for calculations
│   └── analyzer.py             # Statistical analysis tools
├── i18n/
│   ├── __init__.py
│   ├── languages.py            # Language management and translations
│   └── languages_dict/         # Language dictionaries
│       ├── french.py           # French translations
│       └── english.py          # English translations
├── views/
│   ├── __init__.py
│   └── report_generator.py     # Report generation (replaces func.get_message_reward)
└── main.py                     # Main entry point
````