import subprocess
import tkinter as tk
from typing import cast

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.dates import DateFormatter

from cs2tracker.constants import CONFIG_FILE, OUTPUT_FILE, TEXT_EDITOR
from cs2tracker.scraper import Scraper


class Application:
    def __init__(self):
        self.scraper = Scraper()

    def run(self):
        """Run the main application window with buttons for scraping prices, editing the
        configuration, showing history in a chart, and editing the log file.
        """
        application_window = self._configure_window()
        application_window.mainloop()

    def _configure_window(self):
        window = tk.Tk()
        window.title("CS2Tracker")
        window.geometry("450x360")
        window.configure(bg="#1e1e1e")

        frame = tk.Frame(window, bg="#1e1e1e", padx=30, pady=30)
        frame.pack(expand=True, fill="both")

        label = tk.Label(
            frame,
            text="Welcome to CS2Tracker!",
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#1e1e1e",
        )
        label.pack(pady=(0, 30))

        def styled_button(text, command):
            button_style = {
                "font": ("Segoe UI", 12),
                "fg": "white",
                "bg": "#3c3f41",
                "activebackground": "#5c5f61",
                "bd": 0,
            }
            button = tk.Button(frame, text=text, command=command, **button_style)
            button.pack(pady=5, fill="x")
            button.bind("<Enter>", lambda _: button.config(bg="#505354"))
            button.bind("<Leave>", lambda _: button.config(bg="#3c3f41"))
            return button

        styled_button("Run!", self._scrape_prices)
        styled_button("Edit Config", self._edit_config)
        styled_button("Show History (Chart)", self._draw_plot)
        styled_button("Show History (File)", self._edit_log_file)

        background_checkbox_value = tk.BooleanVar(value=self.scraper.identify_background_task())
        background_checkbox = tk.Checkbutton(
            frame,
            text="Daily Background Calculation",
            variable=background_checkbox_value,
            command=lambda: self._toggle_background_task(background_checkbox_value.get()),
            bg="#1e1e1e",
            fg="white",
            selectcolor="#3c3f41",
            activebackground="#1e1e1e",
            font=("Segoe UI", 10),
        )
        background_checkbox.pack(pady=20)

        return window

    def _scrape_prices(self):
        """Scrape prices from the configured sources, print the total, and save the
        results to a file.
        """
        self.scraper.scrape_prices()
        # TODO:
        # - Scrape in external window on Windows (after tkinter configured to hide console)
        # - Also add the cs2tracker banner to each external scraper window
        # subprocess.Popen(f"start cmd /k {PYTHON_EXECUTABLE} -m cs2tracker.scraper", shell=True)

    def _edit_config(self):
        """Edit the configuration file using the specified text editor."""
        subprocess.call([TEXT_EDITOR, CONFIG_FILE])
        self.scraper.parse_config()

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
        subprocess.call([TEXT_EDITOR, OUTPUT_FILE])

    def _toggle_background_task(self, enabled: bool):
        """Toggle whether a daily price calculation should run in the background."""
        self.scraper.toggle_background_task(enabled)
