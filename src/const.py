import json

DEFAULT_LANGUAGE = "FR"
DEFAULT_TITLE = "Run"
DEFAULT_INPUT_FILE = "src/input_logs.txt"

BIG = float('inf')

DPS_REPORT_JSON_URL = "https://dps.report/getJson?permalink="

ALL_BOSSES = []
ALL_PLAYERS = {}

BOSS_DICT = {
    #  RAID BOSSES
    15438: "vg",
    15429: "gors",
    15375: "sab",

    16123: "sloth",
    16115: "matt",

    16253: "esc",
    16235: "kc",
    16246: "xera",

    17194: "cairn",
    17172: "mo",
    17188: "sam",
    17154: "dei",

    19767: "sh",
    19450: "dhuum",

    43974: "ca",
    21105: "twins",
    20934: "qadim",

    22006: "adina",
    21964: "sabir",
    22000: "qpeer",

    26725: "greer",
    26774: "deci",
    26712: "ura",

    #  IBS BOSSES
    22154: "ice",
    22343: "falln",
    22492: "frae",
    22711: "whisp",
    22521: "bone",

    #  EOD BOSSES
    24033: "trin",
    23957: "ankka",
    24266: "li",
    43488: "void",
    25414: "olc",

    #  SOTO BOSSES
    25705: "dagda",
    25989: "cerus",

    # FRAC BOSSES
    17021: "mama",
    17028: "siax",
    16948: "enso",

    17632: "skor",
    17949: "arriv",
    17759: "arkk",

    23254: "ai",

    25577: "kana",

    26231: "eparc"
}

EXTRA_BOSS_DICT = {
    16199: "golem",
    19645: "golem"
}

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Alt-Used': 'dps.report',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

try:
    with open("src/custom_names.json") as file:
        CUSTOM_NAMES = json.load(file)
except:
    CUSTOM_NAMES = {}

EMOTE_WINGMAN = ":wing:"