from datetime import datetime

import urllib3
from rich.console import Console

from cs2tracker._version import version  # pylint: disable=E0611
from cs2tracker.application import Application


def main():
    """
    The main entry point for the CS2Tracker application.

    Provides a console output with the application version and date, and initializes the
    application.
    """

    ## disable warnings for proxy requests
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    console = Console()
    console.print(
        "[bold yellow]"
        + """
    __   _____ _____  ______  ____    ____     __  __  _    ___  ____
   /  ] / ___/|     T|      T|    \\  /    T   /  ]|  l/ ]  /  _]|    \\
  /  / (   \\_ l__/  ||      ||  D  )Y  o  |  /  / |  ' /  /  [_ |  D  )
 /  /   \\__  T|   __jl_j  l_j|    / |     | /  /  |    \\ Y    _]|    /
/   \\_  /  \\ ||  /  |  |  |  |    \\ |  _  |/   \\_ |     Y|   [_ |    \\
\\     | \\    ||     |  |  |  |  .  Y|  |  |\\     ||  .  ||     T|  .  Y
 \\____j  \\___jl_____j  l__j  l__j\\_jl__j__j \\____jl__j\\_jl_____jl__j\\_j


"""
        + f"Version: v{version} - {datetime.today().strftime('%Y/%m/%d')} - Jannik Novak @ashiven\n"
    )

    application = Application()
    application.run()


if __name__ == "__main__":
    main()
