import urllib3
from rich.console import Console

from cs2tracker.application import Application
from cs2tracker.constants import AUTHOR_STRING, BANNER


def main():
    """
    The main entry point for the CS2Tracker application.

    Provides a console output with the application version and date, and initializes the
    application.
    """

    # Disable warnings for proxy requests
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    console = Console()
    console.print(f"[bold yellow]{BANNER}\n{AUTHOR_STRING}\n")

    application = Application()
    application.run()


if __name__ == "__main__":
    main()
