import os
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
        """Configure the main application window layout with buttons for the various
        actions.
        """
        window = tk.Tk()
        window.title("CS2Tracker")
        window.geometry("450x450")

        label = tk.Label(window, text="Welcome to CS2Tracker!")
        run_button = tk.Button(window, text="Run!", command=self._scrape_prices)
        edit_button = tk.Button(window, text="Edit Config", command=self._edit_config)
        plot_button = tk.Button(window, text="Show History (Chart)", command=self._draw_plot)
        plot_file_button = tk.Button(
            window, text="Show History (File)", command=self._edit_log_file
        )
        background_checkbox_value = tk.BooleanVar(value=self.scraper.identify_background_task())
        background_checkbox = tk.Checkbutton(
            window,
            text="Daily Background Calculation",
            command=lambda: self._toggle_background_task(background_checkbox_value.get()),
            variable=background_checkbox_value,
        )

        label.grid(row=0, column=0, pady=50, sticky="NSEW")
        run_button.grid(row=1, column=0, pady=10, sticky="NSEW")
        edit_button.grid(row=2, column=0, pady=10, sticky="NSEW")
        plot_button.grid(row=3, column=0, pady=10, sticky="NSEW")
        plot_file_button.grid(row=4, column=0, pady=10, sticky="NSEW")
        background_checkbox.grid(row=5, column=0, pady=10, sticky="NS")

        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(1, weight=1)
        window.grid_rowconfigure(2, weight=1)
        window.grid_rowconfigure(3, weight=1)
        window.grid_rowconfigure(4, weight=1)
        window.grid_rowconfigure(5, weight=1)

        label.grid_configure(sticky="NSEW")
        run_button.grid_configure(sticky="NSEW")
        edit_button.grid_configure(sticky="NSEW")
        plot_button.grid_configure(sticky="NSEW")
        plot_file_button.grid_configure(sticky="NSEW")
        background_checkbox.grid_configure(sticky="NSEW")

        return window

    def _scrape_prices(self):
        """Scrape prices from the configured sources, print the total, and save the
        results to a file.
        """
        self.scraper.scrape_prices()

    def _edit_config(self):
        """Edit the configuration file using the specified text editor."""
        subprocess.call([TEXT_EDITOR, CONFIG_FILE])
        self.scraper.parse_config()

    def _draw_plot(self):
        """Draw a plot of the scraped prices over time."""
        dates, dollars, euros = self.scraper.read_price_log()

        fig, ax_raw = plt.subplots()
        ax = cast(Axes, ax_raw)

        ax.plot(dates, dollars, label="Dollars")
        ax.plot(dates, euros, label="Euros")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()

        date_formatter = DateFormatter("%d-%m-%Y")
        ax.xaxis.set_major_formatter(date_formatter)
        fig.autofmt_xdate()

        plt.show()

    def _edit_log_file(self):
        """Opens the file containing past price calculations."""
        if not os.path.isfile(OUTPUT_FILE):
            open(OUTPUT_FILE, "w", encoding="utf-8").close()
        subprocess.call([TEXT_EDITOR, OUTPUT_FILE])

    def _toggle_background_task(self, enabled: bool):
        """Toggle whether a daily price calculation should run in the background."""
        success = self.scraper.toggle_background_task(enabled)
        if success and enabled:
            self.scraper.console.print("[bold green][+] Background task enabled.")
        elif success and not enabled:
            self.scraper.console.print("[bold green][-] Background task disabled.")
        else:
            self.scraper.console.print("[bold red][!] Failed to toggle background task.")
