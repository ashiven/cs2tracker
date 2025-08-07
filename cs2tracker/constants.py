import ctypes
import enum
import os
import sys
import tkinter as tk
from datetime import datetime
from shutil import copy, copytree
from subprocess import DEVNULL
from tkinter import ttk

import sv_ttk
from nodejs import npm

from cs2tracker.util.tkinter import centered

try:
    from cs2tracker._version import version  # pylint: disable=E0611

    VERSION = f"v{version}"
except ImportError:
    VERSION = "latest"


class OSType(enum.Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    MACOS = "MacOS"


if sys.platform.startswith("win"):
    OS = OSType.WINDOWS
elif sys.platform.startswith("linux"):
    OS = OSType.LINUX
elif sys.platform.startswith("darwin"):
    OS = OSType.MACOS
else:
    raise NotImplementedError(f"Unsupported OS: {sys.platform}")


PYTHON_EXECUTABLE = sys.executable
RUNNING_IN_EXE = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

if RUNNING_IN_EXE:
    MEIPASS_DIR = sys._MEIPASS  # type: ignore  pylint: disable=protected-access
    MODULE_DIR = MEIPASS_DIR
    PROJECT_DIR = MEIPASS_DIR

    if OS == OSType.WINDOWS:
        APP_DATA_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Local")
    elif OS == OSType.LINUX:
        APP_DATA_DIR = os.environ.get(
            "XDG_DATA_HOME", os.path.join(os.path.expanduser("~"), ".local", "share")
        )
    else:
        raise NotImplementedError(f"Unsupported OS: {OS}")

    CONFIG_FILE_SOURCE = os.path.join(MODULE_DIR, "data", "config.ini")
    OUTPUT_FILE_SOURCE = os.path.join(MODULE_DIR, "data", "output.csv")
    INVENTORY_CONVERT_SCRIPT_SOURCE = os.path.join(MODULE_DIR, "data", "convert_inventory.js")
    INVENTORY_IMPORT_SCRIPT_SOURCE = os.path.join(MODULE_DIR, "data", "get_inventory.js")
    NODE_MODULES_SOURCE = os.path.join(MODULE_DIR, "data", "node_modules")

    DATA_DIR = os.path.join(APP_DATA_DIR, "cs2tracker", "data")
    CONFIG_FILE = os.path.join(DATA_DIR, "config.ini")
    CONFIG_FILE_BACKUP = os.path.join(DATA_DIR, "config.ini.bak")
    OUTPUT_FILE = os.path.join(DATA_DIR, "output.csv")
    INVENTORY_CONVERT_SCRIPT = os.path.join(DATA_DIR, "convert_inventory.js")
    INVENTORY_IMPORT_SCRIPT = os.path.join(DATA_DIR, "get_inventory.js")
    NODE_MODULES = os.path.join(DATA_DIR, "node_modules")

    ICON_FILE = os.path.join(PROJECT_DIR, "assets", "icon.png")
    BATCH_FILE = os.path.join(DATA_DIR, "cs2tracker_scraper.bat")
    INVENTORY_IMPORT_FILE = os.path.join(DATA_DIR, "inventory.json")
    INVENTORY_IMPORT_SCRIPT_DEPENDENCIES = [
        "steam-user",
        "globaloffensive",
        "@node-steam/vdf",
        "axios",
    ]

    def show_temp_popup():
        """Show a temporary popup window while copying initial files."""
        popup = tk.Tk()
        popup.title("Please wait")
        popup.geometry(centered(popup, "300x80"))
        popup.resizable(False, False)
        if OS == OSType.WINDOWS:
            app_id = "cs2tracker.unique.id"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        icon = tk.PhotoImage(file=ICON_FILE)
        popup.wm_iconphoto(True, icon)

        label = ttk.Label(popup, text="Setting up the application. Please wait...")
        label.pack(pady=20)

        sv_ttk.use_dark_theme()

        popup.update()
        return popup

    def copy_initial_files_with_popup():
        """Copy initial files to the user data directory with a temporary popup."""
        popup = show_temp_popup()

        try:
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR)
            if not os.path.exists(OUTPUT_FILE):
                copy(OUTPUT_FILE_SOURCE, OUTPUT_FILE)
            if not os.path.exists(CONFIG_FILE):
                copy(CONFIG_FILE_SOURCE, CONFIG_FILE)
            if not os.path.exists(INVENTORY_CONVERT_SCRIPT):
                copy(INVENTORY_CONVERT_SCRIPT_SOURCE, INVENTORY_CONVERT_SCRIPT)
            if not os.path.exists(INVENTORY_IMPORT_SCRIPT):
                copy(INVENTORY_IMPORT_SCRIPT_SOURCE, INVENTORY_IMPORT_SCRIPT)
            if not os.path.exists(NODE_MODULES):
                copytree(NODE_MODULES_SOURCE, NODE_MODULES)
        finally:
            popup.destroy()

    # pylint: disable=too-many-boolean-expressions
    if (
        not os.path.exists(DATA_DIR)
        or not os.path.exists(OUTPUT_FILE)
        or not os.path.exists(CONFIG_FILE)
        or not os.path.exists(INVENTORY_CONVERT_SCRIPT)
        or not os.path.exists(INVENTORY_IMPORT_SCRIPT)
        or not os.path.exists(NODE_MODULES)
    ):
        copy_initial_files_with_popup()

    # Always copy the source config into the user data directory as a backup
    # and overwrite the existing backup if it exists
    # (This is to ensure that no outdated config backup remains in the user data directory)
    copy(CONFIG_FILE_SOURCE, CONFIG_FILE_BACKUP)


else:
    MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_DIR = os.path.dirname(MODULE_DIR)
    DATA_DIR = os.path.join(MODULE_DIR, "data")

    CONFIG_FILE = os.path.join(DATA_DIR, "config.ini")
    CONFIG_FILE_BACKUP = os.path.join(DATA_DIR, "config.ini.bak")
    OUTPUT_FILE = os.path.join(DATA_DIR, "output.csv")
    INVENTORY_CONVERT_SCRIPT = os.path.join(DATA_DIR, "convert_inventory.js")
    INVENTORY_IMPORT_SCRIPT = os.path.join(DATA_DIR, "get_inventory.js")
    NODE_MODULES = os.path.join(DATA_DIR, "node_modules")

    ICON_FILE = os.path.join(PROJECT_DIR, "assets", "icon.png")
    BATCH_FILE = os.path.join(DATA_DIR, "cs2tracker_scraper.bat")
    INVENTORY_IMPORT_FILE = os.path.join(DATA_DIR, "inventory.json")
    INVENTORY_IMPORT_SCRIPT_DEPENDENCIES = [
        "steam-user",
        "globaloffensive",
        "@node-steam/vdf",
        "axios",
    ]

    if not os.path.exists(CONFIG_FILE_BACKUP):
        copy(CONFIG_FILE, CONFIG_FILE_BACKUP)


# Ensures that the necessary node modules are installed if a user wants
# to import their steam inventory via the cs2tracker/data/get_inventory.js Node.js script.
if not os.path.exists(NODE_MODULES):
    npm.Popen(
        ["install", "-g", "--prefix", DATA_DIR] + INVENTORY_IMPORT_SCRIPT_DEPENDENCIES,
        stdout=DEVNULL,
        stderr=DEVNULL,
        shell=True,
        cwd=DATA_DIR,
    )


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


CAPSULE_PAGES = {
    "Katowice 2014 Sticker Capsule": "https://steamcommunity.com/market/search?q=katowice+2014+legends+challengers",
    "Cologne 2014 Sticker Capsule": "https://steamcommunity.com/market/search?q=cologne+2014+legends+challengers",
    "DreamHack 2014 Sticker Capsule": "https://steamcommunity.com/market/search?q=dreamhack+2014+legends",
    "Katowice 2015 Sticker Capsule": "https://steamcommunity.com/market/search?q=katowice+2015+legends+challengers",
    "Cologne 2015 Sticker Capsule": "https://steamcommunity.com/market/search?q=cologne+2015+legends+challengers",
    "Cluj-Napoca 2015 Sticker Capsule": "https://steamcommunity.com/market/search?q=cluj+napoca+2015+legends+challengers",
    "Columbus 2016 Sticker Capsule": "https://steamcommunity.com/market/search?q=columbus+2016+legends+challengers",
    "Cologne 2016 Sticker Capsule": "https://steamcommunity.com/market/search?q=cologne+2016+legends+challengers",
    "Atlanta 2017 Sticker Capsule": "https://steamcommunity.com/market/search?q=atlanta+2017+legends+challengers",
    "Krakow 2017 Sticker Capsule": "https://steamcommunity.com/market/search?q=krakow+2017+legends+challengers",
    "Boston 2018 Sticker Capsule": "https://steamcommunity.com/market/search?q=boston+2018+legends+challengers",
    "London 2018 Sticker Capsule": "https://steamcommunity.com/market/search?q=london+2018+legends+challengers",
    "Katowice 2019 Sticker Capsule": "https://steamcommunity.com/market/search?q=katowice+2019+legends+challengers",
    "Berlin 2019 Sticker Capsule": "https://steamcommunity.com/market/search?q=berlin+2019+legends+challengers",
    "2020 RMR Sticker Capsule": "https://steamcommunity.com/market/search?q=2020+rmr",
    "Stockholm 2021 Sticker Capsule": "https://steamcommunity.com/market/search?q=stockholm+capsule",
    "Antwerp 2022 Sticker Capsule": "https://steamcommunity.com/market/search?q=antwerp+capsule",
    "Rio 2022 Sticker Capsule": "https://steamcommunity.com/market/search?q=rio+capsule",
    "Paris 2023 Sticker Capsule": "https://steamcommunity.com/market/search?q=paris+capsule",
    "Copenhagen 2024 Sticker Capsule": "https://steamcommunity.com/market/search?q=copenhagen+capsule",
    "Shanghai 2024 Sticker Capsule": "https://steamcommunity.com/market/search?q=shanghai+capsule",
    "Austin 2025 Sticker Capsule": "https://steamcommunity.com/market/search?q=austin+capsule",
}
