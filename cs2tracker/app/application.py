import ctypes
import tkinter as tk
from shutil import copy
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilename, asksaveasfile
from typing import cast

import matplotlib.pyplot as plt
import sv_ttk
from matplotlib.axes import Axes
from matplotlib.dates import DateFormatter

from cs2tracker.app.editor_frame import ConfigEditorFrame
from cs2tracker.app.scraper_frame import ScraperFrame
from cs2tracker.constants import ICON_FILE, OS, OUTPUT_FILE, OSType
from cs2tracker.scraper import BackgroundTask, Scraper
from cs2tracker.util import PriceLogs
from cs2tracker.util.validated_config import get_config

APPLICATION_NAME = "CS2Tracker"
WINDOW_SIZE = "630x335"
DARK_THEME = True

SCRAPER_WINDOW_TITLE = "CS2Tracker Scraper"
SCRAPER_WINDOW_SIZE = "900x750"

CONFIG_EDITOR_TITLE = "Config Editor"
CONFIG_EDITOR_SIZE = "900x750"


config = get_config()


class Application:
    def __init__(self):
        self.scraper = Scraper()

    def run(self):
        """Run the main application window."""
        window = self._configure_window()

        if DARK_THEME:
            sv_ttk.use_dark_theme()
        else:
            sv_ttk.use_light_theme()

        window.mainloop()

    def _configure_window(self):
        """Configure the main application window."""
        window = tk.Tk()
        window.title(APPLICATION_NAME)
        window.geometry(WINDOW_SIZE)

        if OS == OSType.WINDOWS:
            app_id = "cs2tracker.unique.id"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

        icon = tk.PhotoImage(file=ICON_FILE)
        window.wm_iconphoto(True, icon)

        main_frame = MainFrame(window, self.scraper)
        main_frame.pack(expand=True, fill="both")

        return window


class MainFrame(ttk.Frame):
    # pylint: disable=too-many-instance-attributes,attribute-defined-outside-init
    def __init__(self, parent, scraper):
        super().__init__(parent, padding=15)
        self.parent = parent
        self.scraper = scraper
        self._add_widgets()

    def _add_widgets(self):
        """Add widgets to the main frame."""
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._configure_button_frame()
        self.button_frame.grid(row=0, column=0, padx=10, pady=(7, 20), sticky="nsew")
        self._configure_checkbox_frame()
        self.checkbox_frame.grid(row=0, column=1, padx=10, pady=(0, 20), sticky="nsew")

    def _add_button(self, text, command, row):
        """Create and style a button for the button frame."""
        grid_pos = {"row": row, "column": 0, "sticky": "ew", "padx": 10, "pady": 10}
        button = ttk.Button(self.button_frame, text=text, command=command)
        button.grid(**grid_pos)

    def _configure_button_frame(self):
        """Configure the button frame of the application main frame."""
        self.button_frame = ttk.Frame(self, style="Card.TFrame", padding=15)
        self.button_frame.columnconfigure(0, weight=1)

        self._add_button("Run!", self.scrape_prices, 0)
        self._add_button("Edit Config", self._edit_config, 1)
        self._add_button("Show History", self._draw_plot, 2)
        self._add_button("Export History", self._export_log_file, 3)
        self._add_button("Import History", self._import_log_file, 4)

    def _add_checkbox(
        self, text, variable, command, row
    ):  # pylint: disable=too-many-arguments,too-many-positional-arguments,attribute-defined-outside-init
        """Create and style a checkbox for the checkbox frame."""
        grid_pos = {"row": row, "column": 0, "sticky": "w", "padx": (10, 0), "pady": 5}
        checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            text=text,
            variable=variable,
            command=command,
            style="Switch.TCheckbutton",
        )
        checkbox.grid(**grid_pos)

    def _configure_checkbox_frame(self):
        """Configure the checkbox frame for background tasks and settings."""
        self.checkbox_frame = ttk.LabelFrame(self, text="Settings", padding=15)

        self.background_checkbox_value = tk.BooleanVar(value=BackgroundTask.identify())
        self._add_checkbox(
            "Background Task",
            self.background_checkbox_value,
            lambda: self._toggle_background_task(self.background_checkbox_value.get()),
            0,
        )

        self.discord_webhook_checkbox_value = tk.BooleanVar(
            value=config.getboolean("App Settings", "discord_notifications", fallback=False)
        )
        self._add_checkbox(
            "Discord Notifications",
            self.discord_webhook_checkbox_value,
            lambda: self.discord_webhook_checkbox_value.set(
                self._toggle_discord_webhook(self.discord_webhook_checkbox_value.get())
            ),
            1,
        )

        self.use_proxy_checkbox_value = tk.BooleanVar(
            value=config.getboolean("App Settings", "use_proxy", fallback=False)
        )
        self._add_checkbox(
            "Proxy Requests",
            self.use_proxy_checkbox_value,
            lambda: self.use_proxy_checkbox_value.set(
                self._toggle_use_proxy(self.use_proxy_checkbox_value.get())
            ),
            2,
        )

        self.dark_theme_checkbox_value = tk.BooleanVar(value=DARK_THEME)
        self._add_checkbox("Dark Theme", self.dark_theme_checkbox_value, sv_ttk.toggle_theme, 3)

    def scrape_prices(self):
        """Scrape prices from the configured sources, print the total, and save the
        results to a file.
        """
        scraper_window = tk.Toplevel(self.parent)
        scraper_window.geometry(SCRAPER_WINDOW_SIZE)
        scraper_window.title(SCRAPER_WINDOW_TITLE)

        run_frame = ScraperFrame(
            scraper_window,
            self.scraper,
            sheet_size=SCRAPER_WINDOW_SIZE,
            dark_theme=self.dark_theme_checkbox_value.get(),
        )
        run_frame.pack(expand=True, fill="both")
        run_frame.start()

    def _edit_config(self):
        """Open a new window with a config editor GUI."""
        config_editor_window = tk.Toplevel(self.parent)
        config_editor_window.geometry(CONFIG_EDITOR_SIZE)
        config_editor_window.title(CONFIG_EDITOR_TITLE)

        editor_frame = ConfigEditorFrame(config_editor_window)
        editor_frame.pack(expand=True, fill="both")

    def _draw_plot(self):
        """Draw a plot of the scraped prices over time."""
        dates, usd_prices, eur_prices = PriceLogs.read()

        fig, ax_raw = plt.subplots(figsize=(10, 8), num="CS2Tracker Price History")
        fig.suptitle("CS2Tracker Price History", fontsize=16)
        fig.autofmt_xdate()

        ax = cast(Axes, ax_raw)
        ax.plot(dates, usd_prices, label="Dollars")
        ax.plot(dates, eur_prices, label="Euros")
        ax.legend()
        date_formatter = DateFormatter("%Y-%m-%d")
        ax.xaxis.set_major_formatter(date_formatter)

        plt.show()

    def _export_log_file(self):
        """Lets the user export the log file to a different location."""
        export_path = asksaveasfile(
            title="Export Log File",
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv")],
        )
        if export_path:
            copy(OUTPUT_FILE, export_path.name)

    def _import_log_file(self):
        """Lets the user import a log file from a different location."""
        import_path = askopenfilename(
            title="Import Log File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not PriceLogs.validate_file(import_path):
            return
        copy(import_path, OUTPUT_FILE)

    def _toggle_background_task(self, enabled: bool):
        """Toggle whether a daily price calculation should run in the background."""
        BackgroundTask.toggle(enabled)

    def _toggle_use_proxy(self, enabled: bool):
        """Toggle whether the scraper should use proxy servers for requests."""
        proxy_api_key = config.get("User Settings", "proxy_api_key", fallback=None)
        if not proxy_api_key and enabled:
            messagebox.showerror(
                "Config Error",
                "You need to enter a valid crawlbase API key into the configuration to use this feature.",
                parent=self.parent,
            )
            return False

        config.toggle_use_proxy(enabled)
        return True

    def _toggle_discord_webhook(self, enabled: bool):
        """Toggle whether the scraper should send notifications to a Discord webhook."""
        discord_webhook_url = config.get("User Settings", "discord_webhook_url", fallback=None)
        if not discord_webhook_url and enabled:
            messagebox.showerror(
                "Config Error",
                "You need to enter a valid Discord webhook URL into the configuration to use this feature.",
                parent=self.parent,
            )
            return False

        config.toggle_discord_webhook(enabled)
        return True
