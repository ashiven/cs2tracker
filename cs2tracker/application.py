import csv
import datetime
import os
import subprocess
import tkinter as tk

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

from .constants import CONFIG_FILE, OUTPUT_FILE, TEXT_EDITOR
from .scraper import Scraper


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
        window.geometry("400x400")

        label = tk.Label(window, text="Welcome to CS2Tracker!")
        label.grid(column=0, row=0, pady=50, sticky="NSEW")

        run_button = tk.Button(window, text="Run!", command=self._scrape_prices)
        edit_button = tk.Button(window, text="Edit Config", command=self._edit_config)
        plot_button = tk.Button(
            window, text="Show History (Chart)", command=self._draw_plot
        )
        plotfile_button = tk.Button(
            window, text="Show History (File)", command=self._edit_log_file
        )

        run_button.grid(row=1, column=0, pady=10, sticky="NSEW")
        edit_button.grid(row=2, column=0, pady=10, sticky="NSEW")
        plot_button.grid(row=3, column=0, pady=10, sticky="NSEW")
        plotfile_button.grid(row=4, column=0, pady=10, sticky="NSEW")

        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(1, weight=1)
        window.grid_rowconfigure(2, weight=1)
        window.grid_rowconfigure(3, weight=1)
        window.grid_rowconfigure(4, weight=1)
        label.grid_configure(sticky="NSEW")
        run_button.grid_configure(sticky="NSEW")
        edit_button.grid_configure(sticky="NSEW")
        plot_button.grid_configure(sticky="NSEW")
        plotfile_button.grid_configure(sticky="NSEW")

        return window

    def _scrape_prices(self):
        """Scrape prices from the configured sources, print the total, and save the
        results to a file.
        """
        self.scraper.scrape_prices()
        self.scraper.print_total()
        self.scraper.save_to_file()

    def _edit_config(self):
        """Edit the configuration file using the specified text editor."""
        subprocess.call([TEXT_EDITOR, CONFIG_FILE])
        config = self.scraper.parse_config()
        self.scraper.set_config(config)

    def _parse_logs(self):
        """
        Parse the output file to extract dates, dollar prices, and euro prices.

        This data is used for drawing the plot of past prices.
        """
        if not os.path.isfile(OUTPUT_FILE):
            open(OUTPUT_FILE, "w", encoding="utf-8").close()

        dates, dollars, euros = [], [], []
        with open(OUTPUT_FILE, "r", newline="", encoding="utf-8") as price_logs:
            price_logs_reader = csv.reader(price_logs)
            for row in price_logs_reader:
                date, price_with_currency = row
                date = datetime.datetime.strptime(date[:-9], "%Y-%m-%d %H:%M:%S")
                price = float(price_with_currency.rstrip("$€"))
                dates.append(date)
                if price_with_currency.endswith("€"):
                    euros.append(price)
                else:
                    dollars.append(price)

        return dates, dollars, euros

    def _draw_plot(self):
        """Draw a plot of the scraped prices over time."""
        dates, dollars, euros = self._parse_logs()

        fig, ax = plt.subplots()
        ax.plot(dates, dollars, label="Dollars")
        ax.plot(dates, euros, label="Euros")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()

        date_form = DateFormatter("%d-%m-%Y")
        ax.xaxis.set_major_formatter(date_form)
        fig.autofmt_xdate()

        plt.show()

    def _edit_log_file(self):
        """Opens the file containing past price calculations."""
        if not os.path.isfile(OUTPUT_FILE):
            open(OUTPUT_FILE, "w", encoding="utf-8").close()
        subprocess.call([TEXT_EDITOR, OUTPUT_FILE])
