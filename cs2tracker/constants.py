import os
import sys

TEXT_EDITOR = "notepad" if sys.platform == "win32" else "nano"
BASE_DIR = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
OUTPUT_FILE = f"{BASE_DIR}/data/output.csv"
CONFIG_FILE = f"{BASE_DIR}/data/config.ini"


RMR_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=2020+rmr",
    "items": [
        "https://steamcommunity.com/market/listings/730/2020%20RMR%20Legends",
        "https://steamcommunity.com/market/listings/730/2020%20RMR%20Challengers",
        "https://steamcommunity.com/market/listings/730/2020%20RMR%20Contenders",
    ],
    "names": ["RMR Legends", "RMR Challengers", "RMR Contenders"],
}

STOCKHOLM_CAPSULES = {
    "page": "https://steamcommunity.com/market/search?q=stockholm+capsule",
    "items": [
        "https://steamcommunity.com/market/listings/730/Stockholm%202021%20Legends%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Stockholm%202021%20Challengers%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Stockholm%202021%20Contenders%20Sticker%20Capsule",
        "https://steamcommunity.com/market/listings/730/Stockholm%202021%20Champions%20Autograph%20Capsule",
        "https://steamcommunity.com/market/listings/730/Stockholm%202021%20Finalists%20Autograph%20Capsule",
    ],
    "names": [
        "Stockholm Legends",
        "Stockholm Challengers",
        "Stockholm Contenders",
        "Stockholm Champions Autographs",
        "Stockholm Finalists Autographs",
    ],
}

ANTWERP_CAPSULES = {
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
    "names": [
        "Antwerp Legends",
        "Antwerp Challengers",
        "Antwerp Contenders",
        "Antwerp Champions Autographs",
        "Antwerp Challengers Autographs",
        "Antwerp Legends Autographs",
        "Antwerp Contenders Autographs",
    ],
}

RIO_CAPSULES = {
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
    "names": [
        "Rio Legends",
        "Rio Challengers",
        "Rio Contenders",
        "Rio Champions Autographs",
        "Rio Challengers Autographs",
        "Rio Legends Autographs",
        "Rio Contenders Autographs",
    ],
}

PARIS_CAPSULES = {
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
    "names": [
        "Paris Legends",
        "Paris Challengers",
        "Paris Contenders",
        "Paris Champions Autographs",
        "Paris Challengers Autographs",
        "Paris Legends Autographs",
        "Paris Contenders Autographs",
    ],
}

COPENHAGEN_CASULES = {
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
    "names": [
        "Copenhagen Legends",
        "Copenhagen Challengers",
        "Copenhagen Contenders",
        "Copenhagen Champions Autographs",
        "Copenhagen Challengers Autographs",
        "Copenhagen Legends Autographs",
        "Copenhagen Contenders Autographs",
    ],
}

SHANGHAI_CAPSULES = {
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
    "names": [
        "Shanghai Legends",
        "Shanghai Challengers",
        "Shanghai Contenders",
        "Shanghai Champions Autographs",
        "Shanghai Challengers Autographs",
        "Shanghai Legends Autographs",
        "Shanghai Contenders Autographs",
    ],
}


AUSTIN_CAPSULES = {
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
    "names": [
        "Austin Legends",
        "Austin Challengers",
        "Austin Contenders",
        "Austin Champions Autographs",
        "Austin Challengers Autographs",
        "Austin Legends Autographs",
        "Austin Contenders Autographs",
    ],
}

CAPSULE_INFO = {
    "2020 RMR": RMR_CAPSULES,
    "Stockholm": STOCKHOLM_CAPSULES,
    "Antwerp": ANTWERP_CAPSULES,
    "Rio": RIO_CAPSULES,
    "Paris": PARIS_CAPSULES,
    "Copenhagen": COPENHAGEN_CASULES,
    "Shanghai": SHANGHAI_CAPSULES,
    "Austin": AUSTIN_CAPSULES,
}


CASE_PAGES = [
    "https://steamcommunity.com/market/search?q=revolution+case",
    "https://steamcommunity.com/market/search?q=recoil+case",
    "https://steamcommunity.com/market/search?q=dreams+and+nightmares+case",
    "https://steamcommunity.com/market/search?q=operation+riptide+case",
    "https://steamcommunity.com/market/search?q=snakebite+case",
    "https://steamcommunity.com/market/search?q=broken+fang+case",
    "https://steamcommunity.com/market/search?q=fracture+case",
    "https://steamcommunity.com/market/search?q=chroma+case",
    "https://steamcommunity.com/market/search?q=chroma+case",
    "https://steamcommunity.com/market/search?q=chroma+case",
    "https://steamcommunity.com/market/search?q=clutch+case",
    "https://steamcommunity.com/market/search?q=csgo+weapon+case",
    "https://steamcommunity.com/market/search?q=csgo+weapon+case",
    "https://steamcommunity.com/market/search?q=csgo+weapon+case",
    "https://steamcommunity.com/market/search?q=cs20+case",
    "https://steamcommunity.com/market/search?q=danger+zone+case",
    "https://steamcommunity.com/market/search?q=esports+case",
    "https://steamcommunity.com/market/search?q=esports+case",
    "https://steamcommunity.com/market/search?q=esports+case",
    "https://steamcommunity.com/market/search?q=falchion+case",
    "https://steamcommunity.com/market/search?q=gamma+case",
    "https://steamcommunity.com/market/search?q=gamma+case",
    "https://steamcommunity.com/market/search?q=glove+case",
    "https://steamcommunity.com/market/search?q=horizon+case",
    "https://steamcommunity.com/market/search?q=huntsman+weapon+case",
    "https://steamcommunity.com/market/search?q=operation+bravo+case",
    "https://steamcommunity.com/market/search?q=operation+breakout+case",
    "https://steamcommunity.com/market/search?q=operation+hydra+case",
    "https://steamcommunity.com/market/search?q=operation+phoenix+case",
    "https://steamcommunity.com/market/search?q=operation+vanguard+case",
    "https://steamcommunity.com/market/search?q=operation+wildfire+case",
    "https://steamcommunity.com/market/search?q=prisma+case",
    "https://steamcommunity.com/market/search?q=prisma+case",
    "https://steamcommunity.com/market/search?q=revolver+case",
    "https://steamcommunity.com/market/search?q=shadow+case",
    "https://steamcommunity.com/market/search?q=shattered+web+case",
    "https://steamcommunity.com/market/search?q=spectrum+case",
    "https://steamcommunity.com/market/search?q=spectrum+case",
    "https://steamcommunity.com/market/search?q=winter+offensive+case",
    "https://steamcommunity.com/market/search?q=kilowatt+case",
    "https://steamcommunity.com/market/search?q=gallery+case",
    "https://steamcommunity.com/market/search?q=fever+case",
]

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
