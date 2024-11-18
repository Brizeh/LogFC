import json

DEFAULT_LANGUAGE = "FR"
DEFAULT_TITLE = "Run"
DEFAULT_INPUT_FILE = "src/input_logs.txt"

BIG = float('inf')

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

CUSTOM_NAMES = {
    "James Heal.5467"    : "Ravi",
    "hidrozig.5201"      : "Hidrozig",
    "histoRy.6401"       : "HistoRy",
    "Twiyaka.9738"       : "Brizeh",
    "Ava.7895"           : "Ava",
    "Rhonk.4283"         : "Rhonk",
    "Swiizz.5304"        : "Swiizz",
    "Le Scribe.1952"     : "Nico",
    "Lyco.3528"          : "Lyco",
    "endymion.3162"      : "Endymion",
    "Arkadia.9432"       : "Babar",
    "Fibonacci.8610"     : "Fibo",
    "Jiho.1035"          : "Jiho",
    "Blaxono Junior.4732": "Boti",
    "Moonaris.9587"      : "King",
    "Jason.4372"         : "Jason",
    "Arka.3754"          : "Arka",
    "Gabranth.2580"      : "Gab",
    "xxxime.9401"        : "Sweay",
    "JackyGnu.2486"      : "Jacky",
    "oscaro.3079"        : "Zheuja",
    "Yurih.9586"         : "Yurih",
    "Guitou.5682"        : "Guitou",
    "Yvaz.7593"          : "Ibu",
    "spirits x zeke.9054": "Zeke",
    "BobbyFrasier.8450"  : "BobbyFrasier",
    "ich.7086"           : "Ich",
    "Yoomi.8251"         : "Yoomi",
    "Jaydens.9812"       : "Jadam",
    "PonGX.7832"         : "Pongi",
    "Rayden.3145"        : "Rayden",
    "Teh Aajian.9714"    : "Teh Asian",
    "Koeur.1235"         : "Koeur",
    "Huny.6124"          : "Huny",
    "anko.5043"          : "Aiko",
    "Tonnio.3256"        : "Tonnio",
    "Henroo.9314"        : "Henroo",
    "Ambroid.7156"       : "Ambroid"
}

with open('wingman_updater/WINGMAN_DATA.json') as f:
    wingman_data = json.load(f)
    
EMOTE_WINGMAN = ":wing:"