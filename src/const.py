# VARIABLES
import json
from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent

DEFAULT_LANGUAGE = "FR"
DEFAULT_TITLE = "Run"
DEFAULT_INPUT_FILE = str(_PACKAGE_DIR / "input_logs.txt")

BIG = float('inf')

DPS_REPORT_JSON_URL = "https://dps.report/getJson?permalink="

ALL_BOSSES = []

ARXIV = {}

dmgStats = {
    "DmgTarget"     : "Total damage to the boss",
    "DmgPowerTarget": "Total power damage to the boss",
    "DmgCondiTarget": "Total condi damage to the boss",
    "CcTarget"      : "Total breakbar damage to the boss",
    "DmgAll"        : "Total damage to all targets",
    "DmgPowerAll"   : "Total power damage to all targets",
    "DmgCondiAll"   : "Total condi damage to all targets",
    "CcAll"         : "Total breakbar damage to all targets"
}

gameplayStats = {
    "TimeWasted"         : "Time wasted interrupting skill casts",
    "BadCancels"         : "Number of bad skill cast cancels",
    "TimeSaved"          : "Time saved interrupting skill casts",
    "GoodCancels"        : "Number of good skill cast cancels",
    "WeaponSwaps"        : "Number of weapon swaps",
    "avgCombatUptime"    : "%Time spent casting skills & autos during combat",
    "avgCombatNoAAUptime": "%Time spent casting skills during combat (not counting auto attacks)",
    "avgDistSqd"         : "Average distance to center of squad",
    "avgDistCom"         : "Average distance to commander"
}

offensiveStats = {
    "avgCritRate"  : "Percent time hits critical",
    "avgFlankRate" : "Percent time hits while flanking",
    "avgWritPower" : "Percent time power hits while self above 90% HP",
    "avgWritCondi" : "Percent time condition hits while self above 90% HP",
    "avgGlanceRate": "Percent time hits while glancing"
}

defensiveStats = {
    "DmgTaken"        : "Total damage taken",
    "PowerDmgTaken"   : "Total power damage taken",
    "CondiDmgTaken"   : "Total condi damage taken",
    "BreakbarDmgTaken": "Total breakbar damage taken",
    "DmgBarrier"      : "Total damage absorbed by barrier",
    "Interrupted"     : "Number of times player got interrupted",
    "Cced"            : "Number of times player got CC",
    "CcTime"          : "Time player was CC",
    "Evaded"          : "Number of times player evaded attacks",
    "Blocked"         : "Number of times player blocked attacks",
    "Dodged"          : "Number of times player used dodge",
    "Downed"          : "Number of times player got downed",
    "DownedTime"      : "Time player was downed",
    "Dead"            : "Number of times player died",
    "DeadTime"        : "Time player was dead"
}

supportStats = {
    "CondiCleans"    : "Number of condi cleanses on allies",
    "CondiCleansTime": "Time condi cleansed on allies",
    "SelfCleans"     : "Number of condi cleanses on self",
    "SelfCleansTime" : "Time condi cleansed on self",
    "BoonStrips"     : "Number of boons strip on boss",
    "BoonStripsTime" : "Time of boons stripped on boss",
    "StunBreak"      : "Number of stun breaks",
    "StunBreakTime"  : "Time of removed stuns",
    "Resurrects"     : "Number of resurrects on allies",
    "ResurrectTime"  : "Time spent resurrecting allies",
    "avgBoons"       : "Average number of boons"
}

ALL_MECHS = {
    "Damage Stats": dmgStats.copy(),
    "Gameplay Stats": gameplayStats.copy(),
    "Offensive Stats": offensiveStats.copy(),
    "Defensive Stats": defensiveStats.copy(),
    "Support Stats": supportStats.copy()
}

EXTRA_MECHS = {}

ALL_PLAYERS = {}
DUPS_CHECKER = {}

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
    26867: "deci",
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
    27124: "kela",
    
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
    with open(_PACKAGE_DIR / "custom_names.json", encoding="utf-8") as file:
        CUSTOM_NAMES = json.load(file)
except:
    CUSTOM_NAMES = {}
        
    
EMOTE_WINGMAN = "<:wingman:1195372315903533127>"