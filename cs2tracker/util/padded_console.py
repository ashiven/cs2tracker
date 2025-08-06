from rich.console import Console
from rich.padding import Padding

PADDING_BOTTOM = 0
PADDING_TOP = 0
PADDING_LEFT = 4
PADDING_RIGHT = 0


MAX_LINE_LEN = 72
SEPARATOR = "-"


class PaddedConsole:
    def __init__(self, padding=(PADDING_TOP, PADDING_RIGHT, PADDING_BOTTOM, PADDING_LEFT)):
        """Initialize a PaddedConsole with specified padding."""
        self.console = Console()
        self.padding = padding

    def print(self, text):
        """Print text with padding to the console."""
        self.console.print(Padding(text, self.padding))

    def info(self, text):
        """Print info text with padding to the console."""
        text = "[bold green][+] " + text
        self.print(text)

    def error(self, text):
        """Print error text with padding to the console."""
        text = "[bold red][!] " + text
        self.print(text)

    def title(self, text, color):
        """Print the given text as a title."""
        title = text.center(MAX_LINE_LEN, SEPARATOR)
        console.print(f"\n[bold {color}]{title}\n")

    def separator(self, color):
        """Print a separator line."""
        separator = SEPARATOR * MAX_LINE_LEN
        console.print(f"[bold {color}]{separator}")

    def price(self, price_str, price_source, owned, steam_market_price, total_owned):
        # pylint: disable=too-many-arguments,too-many-positional-arguments
        """Print price information."""
        console.print(price_str.format(price_source, owned, steam_market_price, total_owned))

    def __getattr__(self, attr):
        """Ensure console methods can be called directly on PaddedConsole."""
        return getattr(self.console, attr)


console = PaddedConsole()


def get_console():
    """Get the PaddedConsole instance."""
    return console
