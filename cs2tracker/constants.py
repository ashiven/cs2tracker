import enum
import os
import sys
from datetime import datetime
from shutil import copy

try:
    from cs2tracker._version import version  # pylint: disable=E0611

    VERSION = f"v{version}"
except ImportError:
    VERSION = "latest"


class OSType(enum.Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"


OS = OSType.WINDOWS if sys.platform.startswith("win") else OSType.LINUX
PYTHON_EXECUTABLE = sys.executable


RUNNING_IN_EXE = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

if RUNNING_IN_EXE:
    MEIPASS_DIR = sys._MEIPASS  # type: ignore  pylint: disable=protected-access
    MODULE_DIR = MEIPASS_DIR
    PROJECT_DIR = MEIPASS_DIR
    APP_DATA_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Local")
    DATA_DIR = os.path.join(APP_DATA_DIR, "cs2tracker", "data")
    os.makedirs(DATA_DIR, exist_ok=True)

    ICON_FILE = os.path.join(PROJECT_DIR, "assets", "icon.png")
    CONFIG_FILE_SOURCE = os.path.join(MODULE_DIR, "data", "config.ini")
    CONFIG_FILE = os.path.join(DATA_DIR, "config.ini")
    CONFIG_FILE_BACKUP = os.path.join(DATA_DIR, "config.ini.bak")
    OUTPUT_FILE_SOURCE = os.path.join(MODULE_DIR, "data", "output.csv")
    OUTPUT_FILE = os.path.join(DATA_DIR, "output.csv")
    BATCH_FILE = os.path.join(DATA_DIR, "cs2tracker_scraper.bat")
    INVENTORY_IMPORT_FILE = os.path.join(DATA_DIR, "inventory.json")

    # Always copy the source config into the user data directory as a backup
    # and overwrite the existing backup if it exists
    # (This is to ensure that no outdated config backup remains in the user data directory)
    copy(CONFIG_FILE_SOURCE, CONFIG_FILE_BACKUP)

    if not os.path.exists(OUTPUT_FILE):
        copy(OUTPUT_FILE_SOURCE, OUTPUT_FILE)
    if not os.path.exists(CONFIG_FILE):
        copy(CONFIG_FILE_SOURCE, CONFIG_FILE)

else:
    MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_DIR = os.path.dirname(MODULE_DIR)
    DATA_DIR = os.path.join(MODULE_DIR, "data")

    ICON_FILE = os.path.join(PROJECT_DIR, "assets", "icon.png")
    CONFIG_FILE = os.path.join(DATA_DIR, "config.ini")
    CONFIG_FILE_BACKUP = os.path.join(DATA_DIR, "config.ini.bak")
    OUTPUT_FILE = os.path.join(DATA_DIR, "output.csv")
    BATCH_FILE = os.path.join(DATA_DIR, "cs2tracker_scraper.bat")
    INVENTORY_IMPORT_FILE = os.path.join(DATA_DIR, "inventory.json")

    if not os.path.exists(CONFIG_FILE_BACKUP):
        copy(CONFIG_FILE, CONFIG_FILE_BACKUP)


INVENTORY_IMPORT_SCRIPT = os.path.join(MODULE_DIR, "data", "get_inventory.js")
INVENTORY_IMPORT_SCRIPT_DEPENDENCIES = [
    "steam-user",
    "globaloffensive",
    "@node-steam/vdf",
    "axios",
]


BANNER = """
    __   _____ _____  ______  ____    ____     __  __  _    ___  ____
   /  ] / ___/|     T|      T|    \\  /    T   /  ]|  l/ ]  /  _]|    \\
  /  / (   \\_ l__/  ||      ||  D  )Y  o  |  /  / |  ' /  /  [_ |  D  )
 /  /   \\__  T|   __jl_j  l_j|    / |     | /  /  |    \\ Y    _]|    /
/   \\_  /  \\ ||  /  |  |  |  |    \\ |  _  |/   \\_ |     Y|   [_ |    \\
\\     | \\    ||     |  |  |  |  .  Y|  |  |\\     ||  .  ||     T|  .  Y
 \\____j  \\___jl_____j  l__j  l__j\\_jl__j__j \\____jl__j\\_jl_____jl__j\\_j

"""
AUTHOR_STRING = (
    f"Version: {VERSION} - {datetime.today().strftime('%Y/%m/%d')} - Jannik Novak @ashiven\n"
)

CASE_HREFS = [
    "https://steamcommunity.com/market/listings/730/Revolution%20Case",
    "https://steamcommunity.com/market/listings/730/Recoil%20Case",
    "https://steamcommunity.com/market/listings/730/Dreams%20%26%20Nightmares%20Case",
    "https://steamcommunity.com/market/listings/730/Operation%20Riptide%20Case",
    "https://steamcommunity.com/market/listings/730/Snakebite%20Case",
    "https://steamcommunity.com/market/listings/730/Operation%20Broken%20Fang%20Case",
    "https://steamcommunity.com/market/listings/730/Fracture%20Case",
    "https://steamcommunity.com/market/listings/730/Chroma%20Case",
    "https://steamcommunity.com/market/listings/730/Chroma%202%20Case",
    "https://steamcommunity.com/market/listings/730/Chroma%203%20Case",
    "https://steamcommunity.com/market/listings/730/Clutch%20Case",
    "https://steamcommunity.com/market/listings/730/CS%3AGO%20Weapon%20Case",
    "https://steamcommunity.com/market/listings/730/CS%3AGO%20Weapon%20Case%202",
    "https://steamcommunity.com/market/listings/730/CS%3AGO%20Weapon%20Case%203",
    "https://steamcommunity.com/market/listings/730/CS20%20Case",
    "https://steamcommunity.com/market/listings/730/Danger%20Zone%20Case",
    "https://steamcommunity.com/market/listings/730/eSports%202013%20Case",
    "https://steamcommunity.com/market/listings/730/eSports%202013%20Winter%20Case",
    "https://steamcommunity.com/market/listings/730/eSports%202014%20Summer%20Case",
    "https://steamcommunity.com/market/listings/730/Falchion%20Case",
    "https://steamcommunity.com/market/listings/730/Gamma%20Case",
    "https://steamcommunity.com/market/listings/730/Gamma%202%20Case",
    "https://steamcommunity.com/market/listings/730/Glove%20Case",
    "https://steamcommunity.com/market/listings/730/Horizon%20Case",
    "https://steamcommunity.com/market/listings/730/Huntsman%20Weapon%20Case",
    "https://steamcommunity.com/market/listings/730/Operation%20Bravo%20Case",
    "https://steamcommunity.com/market/listings/730/Operation%20Breakout%20Weapon%20Case",
    "https://steamcommunity.com/market/listings/730/Operation%20Hydra%20Case",
    "https://steamcommunity.com/market/listings/730/Operation%20Phoenix%20Weapon%20Case",
    "https://steamcommunity.com/market/listings/730/Operation%20Vanguard%20Weapon%20Case",
    "https://steamcommunity.com/market/listings/730/Operation%20Wildfire%20Case",
    "https://steamcommunity.com/market/listings/730/Prisma%20Case",
    "https://steamcommunity.com/market/listings/730/Prisma%202%20Case",
    "https://steamcommunity.com/market/listings/730/Revolver%20Case",
    "https://steamcommunity.com/market/listings/730/Shadow%20Case",
    "https://steamcommunity.com/market/listings/730/Shattered%20Web%20Case",
    "https://steamcommunity.com/market/listings/730/Spectrum%20Case",
    "https://steamcommunity.com/market/listings/730/Spectrum%202%20Case",
    "https://steamcommunity.com/market/listings/730/Winter%20Offensive%20Weapon%20Case",
    "https://steamcommunity.com/market/listings/730/Kilowatt%20Case",
    "https://steamcommunity.com/market/listings/730/Gallery%20Case",
    "https://steamcommunity.com/market/listings/730/Fever%20Case",
]


KATOWICE_2014_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=katowice+2014+legends+challengers",
    "items": [
        "https://steamcommunity.com/market/listings/730/EMS%20Katowice%202014%20Legends",
        "https://steamcommunity.com/market/listings/730/EMS%20Katowice%202014%20Challengers",
    ],
}

COLOGNE_2014_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=cologne+2014+legends+challengers",
    "items": [
        "https://steamcommunity.com/market/listings/730/ESL%20One%20Cologne%202014%20Legends",
        "https://steamcommunity.com/market/listings/730/ESL%20One%20Cologne%202014%20Challengers",
    ],
}

DREAMHACK_2014_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=dreamhack+2014+legends",
    "items": [
        "https://steamcommunity.com/market/listings/730/DreamHack%202014%20Legends%20%28Holo-Foil%29"
    ],
}

KATOWICE_2015_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=katowice+2015+legends+challengers",
    "items": [
        "https://steamcommunity.com/market/listings/730/ESL%20One%20Katowice%202015%20Legends%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/ESL%20One%20Katowice%202015%20Challengers%20%28Holo-Foil%29",
    ],
}

COLOGNE_2015_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=cologne+2015+legends+challengers",
    "items": [
        "https://steamcommunity.com/market/listings/730/ESL%20One%20Cologne%202015%20Legends%20%28Foil%29",
        "https://steamcommunity.com/market/listings/730/ESL%20One%20Cologne%202015%20Challengers%20%28Foil%29",
    ],
}

CLUJ_NAPOCA_2015_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=cluj+napoca+2015+legends+challengers",
    "items": [
        "https://steamcommunity.com/market/listings/730/DreamHack%20Cluj-Napoca%202015%20Legends%20%28Foil%29",
        "https://steamcommunity.com/market/listings/730/DreamHack%20Cluj-Napoca%202015%20Challengers%20%28Foil%29",
        "https://steamcommunity.com/market/listings/730/Autograph%20Capsule%20%7C%20Legends%20%28Foil%29%20%7C%20Cluj-Napoca%202015",
        "https://steamcommunity.com/market/listings/730/Autograph%20Capsule%20%7C%20Challengers%20%28Foil%29%20%7C%20Cluj-Napoca%202015",
    ],
}

COLUMBUS_2016_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=columbus+2016+legends+challengers",
    "items": [
        "https://steamcommunity.com/market/listings/730/MLG%20Columbus%202016%20Legends%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/MLG%20Columbus%202016%20Challengers%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Autograph%20Capsule%20%7C%20Legends%20%28Foil%29%20%7C%20MLG%20Columbus%202016",
        "https://steamcommunity.com/market/listings/730/Autograph%20Capsule%20%7C%20Challengers%20%28Foil%29%20%7C%20MLG%20Columbus%202016",
    ],
}

COLOGNE_2016_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=cologne+2016+legends+challengers",
    "items": [
        "https://steamcommunity.com/market/listings/730/Cologne%202016%20Legends%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Cologne%202016%20Challengers%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Autograph%20Capsule%20%7C%20Legends%20%28Foil%29%20%7C%20Cologne%202016",
        "https://steamcommunity.com/market/listings/730/Autograph%20Capsule%20%7C%20Challengers%20%28Foil%29%20%7C%20Cologne%202016",
    ],
}

ATLANTA_2017_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=atlanta+2017+legends+challengers",
    "items": [
        "https://steamcommunity.com/market/listings/730/Atlanta%202017%20Legends%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Atlanta%202017%20Challengers%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Autograph%20Capsule%20%7C%20Legends%20%28Foil%29%20%7C%20Atlanta%202017",
        "https://steamcommunity.com/market/listings/730/Autograph%20Capsule%20%7C%20Challengers%20%28Foil%29%20%7C%20Atlanta%202017",
    ],
}

KRAKOW_2017_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=krakow+2017+legends+challengers",
    "items": [
        "https://steamcommunity.com/market/listings/730/Krakow%202017%20Legends%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Krakow%202017%20Challengers%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Krakow%202017%20Legends%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Krakow%202017%20Challengers%20Autograph%20Capsule",
    ],
}

BOSTON_2018_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=boston+2018+legends+challengers",
    "items": [
        "https://steamcommunity.com/market/listings/730/Boston%202018%20Legends%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Boston%202018%20Minor%20Challengers%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Boston%202018%20Returning%20Challengers%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Boston%202018%20Attending%20Legends%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Boston%202018%20Minor%20Challengers%20with%20Flash%20Gaming%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Boston%202018%20Legends%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Boston%202018%20Minor%20Challengers%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Boston%202018%20Returning%20Challengers%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Boston%202018%20Attending%20Legends%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Boston%202018%20Minor%20Challengers%20with%20Flash%20Gaming%20Autograph%20Capsule",
    ],
}

LONDON_2018_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=london+2018+legends+challengers",
    "items": [
        "https://steamcommunity.com/market/listings/730/London%202018%20Legends%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/London%202018%20Minor%20Challengers%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/London%202018%20Returning%20Challengers%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/London%202018%20Legends%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/London%202018%20Minor%20Challengers%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/London%202018%20Returning%20Challengers%20Autograph%20Capsule",
    ],
}

KATOWICE_2019_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=katowice+2019+legends+challengers",
    "items": [
        "https://steamcommunity.com/market/listings/730/Katowice%202019%20Legends%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Katowice%202019%20Minor%20Challengers%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Katowice%202019%20Returning%20Challengers%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Katowice%202019%20Legends%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Katowice%202019%20Minor%20Challengers%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Katowice%202019%20Returning%20Challengers%20Autograph%20Capsule",
    ],
}

BERLIN_2019_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=berlin+2019+legends+challengers",
    "items": [
        "https://steamcommunity.com/market/listings/730/Berlin%202019%20Legends%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Berlin%202019%20Minor%20Challengers%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Berlin%202019%20Returning%20Challengers%20%28Holo-Foil%29",
        "https://steamcommunity.com/market/listings/730/Berlin%202019%20Legends%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Berlin%202019%20Minor%20Challengers%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Berlin%202019%20Returning%20Challengers%20Autograph%20Capsule",
    ],
}

RMR_2020_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=2020+rmr",
    "items": [
        "https://steamcommunity.com/market/listings/730/2020%20RMR%20Legends",
        "https://steamcommunity.com/market/listings/730/2020%20RMR%20Challengers",
        "https://steamcommunity.com/market/listings/730/2020%20RMR%20Contenders",
    ],
}

STOCKHOLM_2021_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=stockholm+capsule",
    "items": [
        "https://steamcommunity.com/market/listings/730/Stockholm%202021%20Legends%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Stockholm%202021%20Challengers%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Stockholm%202021%20Contenders%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Stockholm%202021%20Champions%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Stockholm%202021%20Finalists%20Autograph%20Capsule",
    ],
}

ANTWERP_2022_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=antwerp+capsule",
    "items": [
        "https://steamcommunity.com/market/listings/730/Antwerp%202022%20Legends%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Antwerp%202022%20Challengers%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Antwerp%202022%20Contenders%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Antwerp%202022%20Champions%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Antwerp%202022%20Challengers%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Antwerp%202022%20Legends%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Antwerp%202022%20Contenders%20Autograph%20Capsule",
    ],
}

RIO_2022_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=rio+capsule",
    "items": [
        "https://steamcommunity.com/market/listings/730/Rio%202022%20Legends%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Rio%202022%20Challengers%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Rio%202022%20Contenders%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Rio%202022%20Champions%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Rio%202022%20Challengers%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Rio%202022%20Legends%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Rio%202022%20Contenders%20Autograph%20Capsule",
    ],
}

PARIS_2023_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=paris+capsule",
    "items": [
        "https://steamcommunity.com/market/listings/730/Paris%202023%20Legends%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Paris%202023%20Challengers%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Paris%202023%20Contenders%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Paris%202023%20Champions%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Paris%202023%20Challengers%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Paris%202023%20Legends%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Paris%202023%20Contenders%20Autograph%20Capsule",
    ],
}

COPENHAGEN_2024_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=copenhagen+capsule",
    "items": [
        "https://steamcommunity.com/market/listings/730/Copenhagen%202024%20Legends%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Copenhagen%202024%20Challengers%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Copenhagen%202024%20Contenders%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Copenhagen%202024%20Champions%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Copenhagen%202024%20Challengers%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Copenhagen%202024%20Legends%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Copenhagen%202024%20Contenders%20Autograph%20Capsule",
    ],
}

SHANGHAI_2024_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=shanghai+capsule",
    "items": [
        "https://steamcommunity.com/market/listings/730/Shanghai%202024%20Legends%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Shanghai%202024%20Challengers%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Shanghai%202024%20Contenders%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Shanghai%202024%20Champions%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Shanghai%202024%20Challengers%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Shanghai%202024%20Legends%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Shanghai%202024%20Contenders%20Autograph%20Capsule",
    ],
}

AUSTIN_2025_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=austin+capsule",
    "items": [
        "https://steamcommunity.com/market/listings/730/Austin%202025%20Legends%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Austin%202025%20Challengers%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Austin%202025%20Contenders%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Austin%202025%20Champions%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Austin%202025%20Challengers%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Austin%202025%20Legends%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Austin%202025%20Contenders%20Autograph%20Capsule",
    ],
}

CAPSULE_INFO = {
    "Katowice 2014 Sticker Capsule": KATOWICE_2014_CAPSULES,
    "Cologne 2014 Sticker Capsule": COLOGNE_2014_CAPSULES,
    "DreamHack 2014 Sticker Capsule": DREAMHACK_2014_CAPSULES,
    "Katowice 2015 Sticker Capsule": KATOWICE_2015_CAPSULES,
    "Cologne 2015 Sticker Capsule": COLOGNE_2015_CAPSULES,
    "Cluj-Napoca 2015 Sticker Capsule": CLUJ_NAPOCA_2015_CAPSULES,
    "Columbus 2016 Sticker Capsule": COLUMBUS_2016_CAPSULES,
    "Cologne 2016 Sticker Capsule": COLOGNE_2016_CAPSULES,
    "Atlanta 2017 Sticker Capsule": ATLANTA_2017_CAPSULES,
    "Krakow 2017 Sticker Capsule": KRAKOW_2017_CAPSULES,
    "Boston 2018 Sticker Capsule": BOSTON_2018_CAPSULES,
    "London 2018 Sticker Capsule": LONDON_2018_CAPSULES,
    "Katowice 2019 Sticker Capsule": KATOWICE_2019_CAPSULES,
    "Berlin 2019 Sticker Capsule": BERLIN_2019_CAPSULES,
    "2020 RMR Sticker Capsule": RMR_2020_CAPSULES,
    "Stockholm 2021 Sticker Capsule": STOCKHOLM_2021_CAPSULES,
    "Antwerp 2022 Sticker Capsule": ANTWERP_2022_CAPSULES,
    "Rio 2022 Sticker Capsule": RIO_2022_CAPSULES,
    "Paris 2023 Sticker Capsule": PARIS_2023_CAPSULES,
    "Copenhagen 2024 Sticker Capsule": COPENHAGEN_2024_CAPSULES,
    "Shanghai 2024 Sticker Capsule": SHANGHAI_2024_CAPSULES,
    "Austin 2025 Sticker Capsule": AUSTIN_2025_CAPSULES,
}
