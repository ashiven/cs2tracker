from rich.console import Console
from rich.padding import Padding

PADDING_BOTTOM = 0
PADDING_TOP = 0
PADDING_LEFT = 4
PADDING_RIGHT = 0


class PaddedConsole:
    def __init__(self, padding=(PADDING_TOP, PADDING_RIGHT, PADDING_BOTTOM, PADDING_LEFT)):
        """Initialize a PaddedConsole with specified padding."""
        self.console = Console()
        self.padding = padding

    def print(self, text):
        """Print text with padding to the console."""
        self.console.print(Padding(text, self.padding))

    def __getattr__(self, attr):
        """Ensure console methods can be called directly on PaddedConsole."""
        return getattr(self.console, attr)


console = PaddedConsole()


def get_console():
    """Get the PaddedConsole instance."""
    return console
