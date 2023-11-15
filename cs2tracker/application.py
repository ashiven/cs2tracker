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
            window, text="Show History (File)", command=self._plot_file
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

        window.mainloop()

    def _scrape_prices(self):
        self.scraper.scrape_prices()
        self.scraper.print_total()
        self.scraper.save_to_file()

    def _edit_config(self):
        subprocess.call([TEXT_EDITOR, CONFIG_FILE])
        config = self.scraper._parse_config()
        self.scraper._set_config(config)

    def _draw_plot(self):
        datesp, dollars, euros = self._parse_output()

        fig, ax = plt.subplots()
        ax.plot(datesp, dollars, label="Dollars")
        ax.plot(datesp, euros, label="Euros")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()

        date_form = DateFormatter("%d-%m-%Y")
        ax.xaxis.set_major_formatter(date_form)
        fig.autofmt_xdate()

        plt.show()

    def _parse_output(self):
        def parse_row(row):
            date_str, price_str = row
            price = float(price_str[:-1])
            return date_str, price

        dates = []
        dollars = []
        euros = []
        row_num = 0

        if not os.path.isfile(OUTPUT_FILE):
            open(OUTPUT_FILE, "w").close()

        with open(OUTPUT_FILE, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                row_num += 1
                date, price = parse_row(row)
                if row_num % 2 == 0:
                    euros.append(price)
                else:
                    dollars.append(price)
                    dates.append(date)

        datesp = []
        for date_str in dates:
            date = datetime.datetime.strptime(date_str[:-9], "%Y-%m-%d")
            datesp.append(date)

        return datesp, dollars, euros

    def _plot_file(self):
        if not os.path.isfile(OUTPUT_FILE):
            open(OUTPUT_FILE, "w").close()
        subprocess.call([TEXT_EDITOR, OUTPUT_FILE])
