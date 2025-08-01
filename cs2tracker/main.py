import sys
from subprocess import DEVNULL

import urllib3
from nodejs import npm

from cs2tracker.app import Application
from cs2tracker.constants import (
    AUTHOR_STRING,
    BANNER,
    DATA_DIR,
    INVENTORY_IMPORT_SCRIPT_DEPENDENCIES,
    OS,
    OSType,
)
from cs2tracker.scraper import Scraper
from cs2tracker.util import get_console


def main():
    """
    The main entry point for the CS2Tracker application.

    Provides a console output with the application version and date, and initializes the
    application.
    """

    # Disable warnings for proxy requests
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Set output encoding to UTF-8 with BOM for Windows compatibility
    if OS == OSType.WINDOWS and sys.stdout is not None:
        sys.stdout.reconfigure(encoding="utf-8-sig")  # type: ignore

    console = get_console()
    console.print(f"[bold yellow]{BANNER}\n{AUTHOR_STRING}\n")

    if "--only-scrape" in sys.argv:
        scraper = Scraper()
        scraper.scrape_prices()
    else:
        # Ensures that the necessary node modules are installed if a user wants
        # to import their steam inventory via the cs2tracker/data/get_inventory.js Node.js script.
        npm.Popen(
            ["install"] + INVENTORY_IMPORT_SCRIPT_DEPENDENCIES,
            stdout=DEVNULL,
            stderr=DEVNULL,
            shell=True,
            cwd=DATA_DIR,
        )

        application = Application()
        application.run()


if __name__ == "__main__":
    main()
