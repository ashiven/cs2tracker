import ctypes
import tkinter as tk
from shutil import copy
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilename, asksaveasfile

import sv_ttk

from cs2tracker.app.editor_frame import ConfigEditorFrame
from cs2tracker.app.history_frame import PriceHistoryFrame
from cs2tracker.app.scraper_frame import ScraperFrame
from cs2tracker.config import get_config
from cs2tracker.constants import ICON_FILE, OS, OUTPUT_FILE, OSType
from cs2tracker.logs import PriceLogs
from cs2tracker.scraper.background_task import BackgroundTask
from cs2tracker.scraper.scraper import Scraper
from cs2tracker.util.currency_conversion import CURRENCY_SYMBOLS
from cs2tracker.util.padded_console import get_console
from cs2tracker.util.tkinter import centered, fix_sv_ttk, size_info

APPLICATION_NAME = "CS2Tracker"
WINDOW_SIZE = "630x335"
DARK_THEME = True

SCRAPER_WINDOW_TITLE = "Price Overview"
SCRAPER_WINDOW_SIZE = "900x750"

CONFIG_EDITOR_TITLE = "Config Editor"
CONFIG_EDITOR_SIZE = "850x750"

PRICE_HISTORY_TITLE = "Price History"
PRICE_HISTORY_SIZE = "900x700"

config = get_config()
console = get_console()


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

        fix_sv_ttk(ttk.Style())

        window.focus_force()
        window.mainloop()

    def _configure_window(self):
        """Configure the main application window."""
        window = tk.Tk()
        window.title(APPLICATION_NAME)
        window.geometry(centered(window, WINDOW_SIZE))
        window.minsize(*size_info(WINDOW_SIZE))

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

        self.scraper_window = None
        self.config_editor_window = None
        self.price_history_window = None
        self._add_widgets()

    def _add_widgets(self):
        """Add widgets to the main frame."""
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._configure_button_frame()
        self.button_frame.grid(row=0, column=0, padx=10, pady=(0, 20), sticky="nsew")
        self._configure_settings_frame()
        self.settings_frame.grid(row=0, column=1, padx=10, pady=(0, 20), sticky="nsew")

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
        self._add_button("Show History", self._show_history, 2)
        self._add_button("Export History", self._export_log_file, 3)
        self._add_button("Import History", self._import_log_file, 4)

    def _add_checkbox(
        self, text, variable, command, row
    ):  # pylint: disable=too-many-arguments,too-many-positional-arguments,attribute-defined-outside-init
        """Create and style a checkbox for the checkbox frame."""
        grid_pos = {"row": row, "column": 0, "sticky": "w", "padx": (10, 0), "pady": 5}
        checkbox = ttk.Checkbutton(
            self.settings_frame,
            text=text,
            variable=variable,
            command=command,
            style="Switch.TCheckbutton",
        )
        checkbox.grid(**grid_pos)

    def _configure_settings_frame(self):
        """Configure the settings frame for background tasks and other settings."""
        self.settings_frame = ttk.LabelFrame(self, text="Settings", padding=15)
        self.settings_frame.columnconfigure(0, weight=1)

        self.background_checkbox_value = tk.BooleanVar(value=BackgroundTask.identify())
        self._add_checkbox(
            "Background Task",
            self.background_checkbox_value,
            lambda: self._toggle_background_task(self.background_checkbox_value.get()),
            0,
        )

        self.discord_webhook_checkbox_value = tk.BooleanVar(value=config.discord_notifications)
        self._add_checkbox(
            "Discord Notifications",
            self.discord_webhook_checkbox_value,
            lambda: self.discord_webhook_checkbox_value.set(
                self._toggle_discord_webhook(self.discord_webhook_checkbox_value.get())
            ),
            1,
        )

        self.use_proxy_checkbox_value = tk.BooleanVar(value=config.use_proxy)
        self._add_checkbox(
            "Proxy Requests",
            self.use_proxy_checkbox_value,
            lambda: self.use_proxy_checkbox_value.set(
                self._toggle_use_proxy(self.use_proxy_checkbox_value.get())
            ),
            2,
        )

        self.dark_theme_checkbox_value = tk.BooleanVar(value=DARK_THEME)
        self._add_checkbox("Dark Theme", self.dark_theme_checkbox_value, self._toggle_theme, 3)

        self.currency_selection_label = ttk.Label(self.settings_frame, text="Currency:")
        self.currency_selection_label.grid(row=4, column=0, sticky="w", padx=(20, 0), pady=5)
        self.currency_selection = ttk.Combobox(
            self.settings_frame,
            state="readonly",
            values=list(CURRENCY_SYMBOLS),
            postcommand=self.parent.focus_set,
        )
        self.currency_selection.set(config.conversion_currency)
        self.currency_selection.grid(row=5, column=0, sticky="w", padx=(20, 0), pady=5)

        def on_currency_change(_):
            config.set_app_option("conversion_currency", self.currency_selection.get())
            self.currency_selection.selection_clear()
            self.parent.focus_set()

        self.currency_selection.bind(
            "<<ComboboxSelected>>",
            on_currency_change,
        )

    def scrape_prices(self):
        """Scrape prices from the configured sources, print the total, and save the
        results to a file.
        """
        if self.scraper_window is None or not self.scraper_window.winfo_exists():
            self._open_scraper_window()
        else:
            self.scraper_window.lift()
            self.scraper_window.focus_set()

    def _open_scraper_window(self):
        """Open a new window with the scraper GUI."""
        self.scraper_window = tk.Toplevel(self.parent)
        self.scraper_window.geometry(centered(self.scraper_window, SCRAPER_WINDOW_SIZE))
        self.scraper_window.minsize(*size_info(SCRAPER_WINDOW_SIZE))
        self.scraper_window.title(SCRAPER_WINDOW_TITLE)

        run_frame = ScraperFrame(
            self.scraper_window,
            self.scraper,
            sheet_size=SCRAPER_WINDOW_SIZE,
            dark_theme=self.dark_theme_checkbox_value.get(),
        )
        run_frame.pack(expand=True, fill="both")
        run_frame.start()

    def _edit_config(self):
        """Open a new window with a config editor GUI or lift the existing one."""
        if self.config_editor_window is None or not self.config_editor_window.winfo_exists():
            self._open_config_editor()
        else:
            self.config_editor_window.lift()
            self.config_editor_window.focus_set()

    def _open_config_editor(self):
        """Open a new window with a config editor GUI."""
        self.config_editor_window = tk.Toplevel(self.parent)
        self.config_editor_window.geometry(centered(self.config_editor_window, CONFIG_EDITOR_SIZE))
        self.config_editor_window.minsize(*size_info(CONFIG_EDITOR_SIZE))
        self.config_editor_window.title(CONFIG_EDITOR_TITLE)

        editor_frame = ConfigEditorFrame(self.config_editor_window)
        editor_frame.pack(expand=True, fill="both")

    def _show_history(self):
        """Show a chart consisting of past calculations."""
        if self.price_history_window is None or not self.price_history_window.winfo_exists():
            self._open_history_window()
        else:
            self.price_history_window.lift()
            self.price_history_window.focus_set()

    def _open_history_window(self):
        """Open a new window with a price history GUI."""
        if PriceLogs.empty():
            return

        self.price_history_window = tk.Toplevel(self.parent)
        self.price_history_window.geometry(centered(self.price_history_window, PRICE_HISTORY_SIZE))
        self.price_history_window.minsize(*size_info(PRICE_HISTORY_SIZE))
        self.price_history_window.title(PRICE_HISTORY_TITLE)

        history_frame = PriceHistoryFrame(self.price_history_window)
        history_frame.pack(expand=True, fill="both")

    def _export_log_file(self):
        """Lets the user export the log file to a different location."""
        if PriceLogs.empty():
            return

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
            console.error("Invalid log file format.")
            return
        copy(import_path, OUTPUT_FILE)
        console.info("Log file imported successfully.")

    def _toggle_background_task(self, enabled: bool):
        """Toggle whether a daily price calculation should run in the background."""
        BackgroundTask.toggle(enabled)

    def _toggle_use_proxy(self, enabled: bool):
        """Toggle whether the scraper should use proxy servers for requests."""
        proxy_api_key = config.proxy_api_key
        if not proxy_api_key and enabled:
            messagebox.showerror(
                "Config Error",
                "You need to enter a valid crawlbase API key into the configuration to use this feature.",
                parent=self.parent,
            )
            return False

        config.toggle_app_option("use_proxy", enabled)
        return True

    def _toggle_discord_webhook(self, enabled: bool):
        """Toggle whether the scraper should send notifications to a Discord webhook."""
        discord_webhook_url = config.discord_webhook_url
        if not discord_webhook_url and enabled:
            messagebox.showerror(
                "Config Error",
                "You need to enter a valid Discord webhook URL into the configuration to use this feature.",
                parent=self.parent,
            )
            return False

        config.toggle_app_option("discord_webhook", enabled)
        return True

    def _toggle_theme(self):
        """Toggle the theme of the application."""
        if self.dark_theme_checkbox_value.get():
            sv_ttk.use_dark_theme()
        else:
            sv_ttk.use_light_theme()
        fix_sv_ttk(ttk.Style())
