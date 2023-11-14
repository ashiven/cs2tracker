import urllib3
from application import Application
from rich.console import Console


def main():
    ## disable warnings for proxy requests
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    console = Console()

    console.print(
        "[bold yellow]"
        + "                                                                              "
    )
    console.print(
        "[bold yellow]"
        + "    __   _____  ____   ___   ______  ____    ____     __  __  _    ___  ____  "
    )
    console.print(
        "[bold yellow]"
        + "   /  ] / ___/ /    T /   \ |      T|    \  /    T   /  ]|  l/ ]  /  _]|    \ "
    )
    console.print(
        "[bold yellow]"
        + "  /  / (   \_ Y   __jY     Y|      ||  D  )Y  o  |  /  / |  ' /  /  [_ |  D  )"
    )
    console.print(
        "[bold yellow]"
        + " /  /   \__  T|  T  ||  O  |l_j  l_j|    / |     | /  /  |    \ Y    _]|    / "
    )
    console.print(
        "[bold yellow]"
        + "/   \_  /  \ ||  l_ ||     |  |  |  |    \ |  _  |/   \_ |     Y|   [_ |    \ "
    )
    console.print(
        "[bold yellow]"
        + "\     | \    ||     |l     !  |  |  |  .  Y|  |  |\     ||  .  ||     T|  .  Y"
    )
    console.print(
        "[bold yellow]"
        + " \____j  \___jl___,_j \___/   l__j  l__j\_jl__j__j \____jl__j\_jl_____jl__j\_j"
    )
    console.print(
        "[bold yellow]"
        + "                                                                              "
    )
    console.print(
        "[bold yellow]" + "Version: v2.0.1 - 11/14/2023 - Jannik Novak @ashiven_"
    )
    console.print(
        "[bold yellow]"
        + "                                                                              "
    )

    application = Application()
    application.run()


if __name__ == "__main__":
    main()
