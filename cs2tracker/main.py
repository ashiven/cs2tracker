import sys

import urllib3

from cs2tracker.application import Application
from cs2tracker.constants import AUTHOR_STRING, BANNER
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

    if "--only-scrape" in sys.argv:
        scraper = Scraper()
        scraper.console.print(f"[bold yellow]{BANNER}\n{AUTHOR_STRING}\n")
        scraper.scrape_prices()
    else:
        console = PaddedConsole()
        console.print(f"[bold yellow]{BANNER}\n{AUTHOR_STRING}\n")
        application = Application()
        application.run()


if __name__ == "__main__":
    main()
