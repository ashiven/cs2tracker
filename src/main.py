import urllib3
from colorama import Fore, Style

from application import Application


def main():
    ## disable warnings for proxy requests
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    print(
        Fore.YELLOW
        + "                                                                              "
        + Style.RESET_ALL
    )
    print(
        Fore.YELLOW
        + "    __   _____  ____   ___   ______  ____    ____     __  __  _    ___  ____  "
        + Style.RESET_ALL
    )
    print(
        Fore.YELLOW
        + "   /  ] / ___/ /    T /   \ |      T|    \  /    T   /  ]|  l/ ]  /  _]|    \ "
        + Style.RESET_ALL
    )
    print(
        Fore.YELLOW
        + "  /  / (   \_ Y   __jY     Y|      ||  D  )Y  o  |  /  / |  ' /  /  [_ |  D  )"
        + Style.RESET_ALL
    )
    print(
        Fore.YELLOW
        + " /  /   \__  T|  T  ||  O  |l_j  l_j|    / |     | /  /  |    \ Y    _]|    / "
        + Style.RESET_ALL
    )
    print(
        Fore.YELLOW
        + "/   \_  /  \ ||  l_ ||     |  |  |  |    \ |  _  |/   \_ |     Y|   [_ |    \ "
        + Style.RESET_ALL
    )
    print(
        Fore.YELLOW
        + "\     | \    ||     |l     !  |  |  |  .  Y|  |  |\     ||  .  ||     T|  .  Y"
        + Style.RESET_ALL
    )
    print(
        Fore.YELLOW
        + " \____j  \___jl___,_j \___/   l__j  l__j\_jl__j__j \____jl__j\_jl_____jl__j\_j"
        + Style.RESET_ALL
    )
    print(
        Fore.YELLOW
        + "                                                                              "
        + Style.RESET_ALL
    )
    print(
        Fore.YELLOW
        + "Version: v1.0.2 - 03/12/2023 - Jannik Novak @ashiven_"
        + Style.RESET_ALL
    )
    print(
        Fore.YELLOW
        + "                                                                              "
        + Style.RESET_ALL
    )

    application = Application()
    application.run()


if __name__ == "__main__":
    main()
