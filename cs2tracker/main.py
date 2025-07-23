import sys

import urllib3

from cs2tracker.application import Application
from cs2tracker.constants import AUTHOR_STRING, BANNER, OS, OSType
from cs2tracker.padded_console import PaddedConsole
from cs2tracker.scraper import Scraper


def main():
    """
    The main entry point for the CS2Tracker application.

    Provides a console output with the application version and date, and initializes the
    application.
    """

    # Disable warnings for proxy requests
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Set output encoding to UTF-8 with BOM for Windows compatibility
    if OS == OSType.WINDOWS:
        sys.stdout.reconfigure(encoding="utf-8-sig")  # type: ignore

    console = PaddedConsole()
    console.print(f"[bold yellow]{BANNER}\n{AUTHOR_STRING}\n")

    if "--only-scrape" in sys.argv:
        scraper = Scraper()
        scraper.scrape_prices()
    else:
        application = Application()
        application.run()


if __name__ == "__main__":
    main()
