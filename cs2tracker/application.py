import tkinter as tk
from subprocess import Popen
from threading import Thread
from typing import cast

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.dates import DateFormatter

from cs2tracker.constants import (
    CONFIG_FILE,
    OS,
    OUTPUT_FILE,
    PYTHON_EXECUTABLE,
    TEXT_EDITOR,
    OSType,
)
from cs2tracker.scraper import Scraper

WINDOW_TITLE = "CS2Tracker"
WINDOW_SIZE = "450x380"
BACKGROUND_COLOR = "#1e1e1e"
BUTTON_COLOR = "#3c3f41"
BUTTON_HOVER_COLOR = "#505354"
BUTTON_ACTIVE_COLOR = "#5c5f61"
FONT_STYLE = "Segoe UI"
FONT_COLOR = "white"

SCRAPER_WINDOW_TITLE = "CS2Tracker"
SCRAPER_WINDOW_HEIGHT = 40
SCRAPER_WINDOW_WIDTH = 75
SCRAPER_WINDOW_BACKGROUND_COLOR = "Black"


class Application:
    def __init__(self):
        self.scraper = Scraper()

    def run(self):
        """Run the main application window with buttons for scraping prices, editing the
        configuration, showing history in a chart, and editing the log file.
        """
        application_window = self._configure_window()
        application_window.mainloop()

    def _add_button(self, frame, text, command):
        """Create and style a button for the main application window."""
        button_style = {
            "font": (FONT_STYLE, 12),
            "fg": FONT_COLOR,
            "bg": BUTTON_COLOR,
            "activebackground": BUTTON_ACTIVE_COLOR,
        }
        button = tk.Button(frame, text=text, command=command, **button_style)
        button.pack(pady=5, fill="x")
        button.bind("<Enter>", lambda _: button.config(bg=BUTTON_HOVER_COLOR))
        button.bind("<Leave>", lambda _: button.config(bg=BUTTON_COLOR))
        return button

    def _configure_window(self):
        """Configure the main application window UI and add buttons for the main
        functionalities.
        """
        window = tk.Tk()
        window.title(WINDOW_TITLE)
        window.geometry(WINDOW_SIZE)
        window.configure(bg=BACKGROUND_COLOR)

        frame = tk.Frame(window, bg=BACKGROUND_COLOR, padx=30, pady=30)
        frame.pack(expand=True, fill="both")

        label = tk.Label(
            frame,
            text=f"Welcome to {WINDOW_TITLE}!",
            font=(FONT_STYLE, 16, "bold"),
            fg=FONT_COLOR,
            bg=BACKGROUND_COLOR,
        )
        label.pack(pady=(0, 30))

        self._add_button(frame, "Run!", self._scrape_prices)
        self._add_button(frame, "Edit Config", self._edit_config)
        self._add_button(frame, "Show History (Chart)", self._draw_plot)
        self._add_button(frame, "Show History (File)", self._edit_log_file)

        background_checkbox_value = tk.BooleanVar(value=self.scraper.identify_background_task())
        background_checkbox = tk.Checkbutton(
            frame,
            text="Daily Background Calculation",
            variable=background_checkbox_value,
            command=lambda: self._toggle_background_task(background_checkbox_value.get()),
            bg=BACKGROUND_COLOR,
            fg=FONT_COLOR,
            selectcolor=BUTTON_COLOR,
            activebackground=BACKGROUND_COLOR,
            font=(FONT_STYLE, 10),
        )
        background_checkbox.pack(pady=20)

        return window

    def _scrape_prices(self):
        """Scrape prices from the configured sources, print the total, and save the
        results to a file.
        """
        if OS == OSType.WINDOWS:
            scraper_cmd = (
                'start powershell -NoExit -Command "& {'
                f"$Host.UI.RawUI.WindowTitle = '{SCRAPER_WINDOW_TITLE}'; "
                "$size = $Host.UI.RawUI.WindowSize; "
                f"$size.Width = {SCRAPER_WINDOW_WIDTH}; "
                f"$size.Height = {SCRAPER_WINDOW_HEIGHT}; "
                "$Host.UI.RawUI.WindowSize = $size; "
                f"$Host.UI.RawUI.BackgroundColor = '{SCRAPER_WINDOW_BACKGROUND_COLOR}'; "
                "Clear-Host; "
                f"{PYTHON_EXECUTABLE} -m cs2tracker.scraper"
                '}"'
            )
            Popen(scraper_cmd, shell=True)
        else:
            self.scraper.scrape_prices()
            # TODO: implement external window for Linux

    def _edit_config(self):
        """Edit the configuration file using the specified text editor."""
        _popen_and_call(
            popen_args={"args": [TEXT_EDITOR, CONFIG_FILE], "shell": True},
            callback=self.scraper.parse_config,
        )

    def _draw_plot(self):
        """Draw a plot of the scraped prices over time."""
        dates, dollars, euros = self.scraper.read_price_log()

        fig, ax_raw = plt.subplots(figsize=(10, 8), num="CS2Tracker Price History")
        fig.suptitle("CS2Tracker Price History", fontsize=16)
        fig.autofmt_xdate()

        ax = cast(Axes, ax_raw)
        ax.plot(dates, dollars, label="Dollars")
        ax.plot(dates, euros, label="Euros")
        ax.legend()
        date_formatter = DateFormatter("%d-%m-%Y")
        ax.xaxis.set_major_formatter(date_formatter)

        plt.show()

    def _edit_log_file(self):
        """Opens the file containing past price calculations."""
        Popen([TEXT_EDITOR, OUTPUT_FILE], shell=True)

    def _toggle_background_task(self, enabled: bool):
        """Toggle whether a daily price calculation should run in the background."""
        self.scraper.toggle_background_task(enabled)


def _popen_and_call(popen_args, callback):
    """
    Runs the given args in a subprocess.Popen, and then calls the function callback when
    the subprocess completes.

    Source: https://stackoverflow.com/questions/2581817/python-subprocess-callback-when-cmd-exits
    """

    def process_and_callback(popen_args, callback):
        process = Popen(**popen_args)
        process.wait()
        callback()

    thread = Thread(target=process_and_callback, args=(popen_args, callback), daemon=True)
    thread.start()
