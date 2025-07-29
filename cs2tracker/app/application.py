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

APPLICATION_NAME = "CS2Tracker"
WINDOW_SIZE = "630x335"
DARK_THEME = True

SCRAPER_WINDOW_TITLE = "CS2Tracker Scraper"
SCRAPER_WINDOW_SIZE = "800x750"

CONFIG_EDITOR_TITLE = "Config Editor"
CONFIG_EDITOR_SIZE = "800x750"


class Application:
    def __init__(self):
        self.scraper = Scraper()
        self.application_window = None

    def run(self):
        """Run the main application window with buttons for scraping prices, editing the
        configuration, showing history in a chart, and editing the log file.
        """
        self.application_window = self._configure_window()

        if DARK_THEME:
            sv_ttk.use_dark_theme()
        else:
            sv_ttk.use_light_theme()

        self.application_window.mainloop()

    def _add_button(self, frame, text, command, row):
        """Create and style a button for the button frame."""
        grid_pos = {"row": row, "column": 0, "sticky": "ew", "padx": 10, "pady": 10}
        button = ttk.Button(frame, text=text, command=command)
        button.grid(**grid_pos)

    def _configure_button_frame(self, main_frame):
        """Configure the button frame of the application main frame."""
        button_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=15)
        button_frame.columnconfigure(0, weight=1)
        button_frame.grid(row=0, column=0, padx=10, pady=(7, 20), sticky="nsew")

        self._add_button(button_frame, "Run!", self.scrape_prices, 0)
        self._add_button(button_frame, "Edit Config", self._edit_config, 1)
        self._add_button(button_frame, "Show History", self._draw_plot, 2)
        self._add_button(button_frame, "Export History", self._export_log_file, 3)
        self._add_button(button_frame, "Import History", self._import_log_file, 4)

    def _add_checkbox(
        self, frame, text, variable, command, row
    ):  # pylint: disable=too-many-arguments,too-many-positional-arguments
        """Create and style a checkbox for the checkbox frame."""
        grid_pos = {"row": row, "column": 0, "sticky": "w", "padx": (10, 0), "pady": 5}
        checkbox = ttk.Checkbutton(
            frame,
            text=text,
            variable=variable,
            command=command,
            style="Switch.TCheckbutton",
        )
        checkbox.grid(**grid_pos)

    def _configure_checkbox_frame(self, main_frame):
        """Configure the checkbox frame for background tasks and settings."""
        checkbox_frame = ttk.LabelFrame(main_frame, text="Settings", padding=15)
        checkbox_frame.grid(row=0, column=1, padx=10, pady=(0, 20), sticky="nsew")

        background_checkbox_value = tk.BooleanVar(value=BackgroundTask.identify())
        self._add_checkbox(
            checkbox_frame,
            "Background Task",
            background_checkbox_value,
            lambda: self._toggle_background_task(background_checkbox_value.get()),
            0,
        )

        discord_webhook_checkbox_value = tk.BooleanVar(
            value=self.scraper.config.getboolean(
                "App Settings", "discord_notifications", fallback=False
            )
        )
        self._add_checkbox(
            checkbox_frame,
            "Discord Notifications",
            discord_webhook_checkbox_value,
            lambda: discord_webhook_checkbox_value.set(
                self._toggle_discord_webhook(discord_webhook_checkbox_value.get())
            ),
            1,
        )

        use_proxy_checkbox_value = tk.BooleanVar(
            value=self.scraper.config.getboolean("App Settings", "use_proxy", fallback=False)
        )
        self._add_checkbox(
            checkbox_frame,
            "Proxy Requests",
            use_proxy_checkbox_value,
            lambda: use_proxy_checkbox_value.set(
                self._toggle_use_proxy(use_proxy_checkbox_value.get())
            ),
            2,
        )

        self.dark_theme = tk.BooleanVar(value=DARK_THEME)
        self._add_checkbox(checkbox_frame, "Dark Theme", self.dark_theme, sv_ttk.toggle_theme, 3)

    def _configure_main_frame(self, window):
        """Configure the main frame of the application window with buttons and
        checkboxes.
        """
        main_frame = ttk.Frame(window, padding=15)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self._configure_button_frame(main_frame)
        self._configure_checkbox_frame(main_frame)

        main_frame.pack(expand=True, fill="both")

    def _configure_window(self):
        """Configure the main application window UI and add buttons for the main
        functionalities.
        """
        window = tk.Tk()
        window.title(APPLICATION_NAME)
        window.geometry(WINDOW_SIZE)

        if OS == OSType.WINDOWS:
            app_id = "cs2tracker.unique.id"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

        icon = tk.PhotoImage(file=ICON_FILE)
        window.wm_iconphoto(True, icon)

        self._configure_main_frame(window)

        return window

    def scrape_prices(self):
        """Scrape prices from the configured sources, print the total, and save the
        results to a file.
        """
        scraper_window = tk.Toplevel(self.application_window)
        scraper_window.geometry(SCRAPER_WINDOW_SIZE)
        scraper_window.title(SCRAPER_WINDOW_TITLE)

        run_frame = ScraperFrame(
            scraper_window,
            self.scraper,
            sheet_size=SCRAPER_WINDOW_SIZE,
            dark_theme=self.dark_theme.get(),
        )
        run_frame.pack(expand=True, fill="both")
        run_frame.start()

    def _edit_config(self):
        """Open a new window with a config editor GUI."""
        config_editor_window = tk.Toplevel(self.application_window)
        config_editor_window.geometry(CONFIG_EDITOR_SIZE)
        config_editor_window.title(CONFIG_EDITOR_TITLE)

        editor_frame = ConfigEditorFrame(config_editor_window, self.scraper)
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
            filetypes=[("CSV files", "*.csv")],
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
        proxy_api_key = self.scraper.config.get("User Settings", "proxy_api_key", fallback=None)
        if not proxy_api_key and enabled:
            messagebox.showerror(
                "Config Error",
                "You need to enter a valid crawlbase API key into the configuration to use this feature.",
            )
            return False

        self.scraper.toggle_use_proxy(enabled)
        return True

    def _toggle_discord_webhook(self, enabled: bool):
        """Toggle whether the scraper should send notifications to a Discord webhook."""
        discord_webhook_url = self.scraper.config.get(
            "User Settings", "discord_webhook_url", fallback=None
        )
        if not discord_webhook_url and enabled:
            messagebox.showerror(
                "Config Error",
                "You need to enter a valid Discord webhook URL into the configuration to use this feature.",
            )
            return False

        self.scraper.toggle_discord_webhook(enabled)
        return True
