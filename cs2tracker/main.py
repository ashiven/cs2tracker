import urllib3
from rich.console import Console

from ._version import version
from .application import Application


def main():
    ## disable warnings for proxy requests
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    console = Console()
    console.print(
        "[bold yellow]"
        + """
    __   _____ _____  ______  ____    ____     __  __  _    ___  ____
   /  ] / ___/|     T|      T|    \  /    T   /  ]|  l/ ]  /  _]|    \\
  /  / (   \_ l__/  ||      ||  D  )Y  o  |  /  / |  ' /  /  [_ |  D  )
 /  /   \__  T|   __jl_j  l_j|    / |     | /  /  |    \ Y    _]|    /
/   \_  /  \ ||  /  |  |  |  |    \ |  _  |/   \_ |     Y|   [_ |    \\
\     | \    ||     |  |  |  |  .  Y|  |  |\     ||  .  ||     T|  .  Y
 \____j  \___jl_____j  l__j  l__j\_jl__j__j \____jl__j\_jl_____jl__j\_j


"""
        + f"Version: v{version} - 11/14/2023 - Jannik Novak @ashiven_\n"
    )

    application = Application()
    application.run()


if __name__ == "__main__":
    main()
