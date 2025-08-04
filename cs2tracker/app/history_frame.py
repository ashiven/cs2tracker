from tkinter import ttk
from typing import cast

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.dates import DateFormatter

from cs2tracker.util import PriceLogs


class PriceHistoryFrame(ttk.Frame):
    def __init__(self, parent):
        """Initialize the price history frame."""
        super().__init__(parent)

        self._add_widgets()

    def _add_widgets(self):
        """Add widgets to the frame."""
        self._configure_canvas()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.toolbar.pack()

    def _configure_canvas(self):
        """Configure the canvas on which the price history chart is drawn."""
        self._draw_plot()
        plt.close(self.fig)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()

    def _draw_plot(self):
        """Draw a chart of the price history."""
        dates, usd_prices, eur_prices = PriceLogs.read()

        self.fig, ax_raw = plt.subplots(dpi=100)
        self.fig.autofmt_xdate()

        ax = cast(Axes, ax_raw)
        ax.plot(dates, usd_prices, label="USD")
        ax.plot(dates, eur_prices, label="EUR")
        ax.legend()
        date_formatter = DateFormatter("%Y-%m-%d")
        ax.xaxis.set_major_formatter(date_formatter)
