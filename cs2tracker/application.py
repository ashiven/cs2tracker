import ctypes
import tkinter as tk
from shutil import copy
from subprocess import Popen
from threading import Thread
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfile
from typing import cast

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.dates import DateFormatter

from cs2tracker.background_task import BackgroundTask
from cs2tracker.constants import (
    CONFIG_FILE,
    CONFIG_FILE_BACKUP,
    ICON_FILE,
    OS,
    OUTPUT_FILE,
    POWERSHELL_COLORIZE_OUTPUT,
    PYTHON_EXECUTABLE,
    RUNNING_IN_EXE,
    TEXT_EDITOR,
    OSType,
)
from cs2tracker.price_logs import PriceLogs
from cs2tracker.scraper import Scraper

APPLICATION_NAME = "CS2Tracker"

WINDOW_SIZE = "600x550"
BACKGROUND_COLOR = "#1e1e1e"
BUTTON_COLOR = "#3c3f41"
BUTTON_HOVER_COLOR = "#505354"
BUTTON_ACTIVE_COLOR = "#5c5f61"
FONT_STYLE = "Segoe UI"
FONT_COLOR = "white"

SCRAPER_WINDOW_HEIGHT = 40
SCRAPER_WINDOW_WIDTH = 120
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

    def _add_checkbox(self, frame, text, variable, command):
        checkbox = tk.Checkbutton(
            frame,
            text=text,
            variable=variable,
            command=command,
            bg=BACKGROUND_COLOR,
            fg=FONT_COLOR,
            selectcolor=BUTTON_COLOR,
            activebackground=BACKGROUND_COLOR,
            font=(FONT_STYLE, 10),
            anchor="w",
            padx=20,
        )
        checkbox.pack(fill="x", anchor="w", pady=2)

    def _configure_main_frame(self, frame):
        """Configure the main frame of the application window."""
        label = tk.Label(
            frame,
            text=f"Welcome to {APPLICATION_NAME}!",
            font=(FONT_STYLE, 16, "bold"),
            fg=FONT_COLOR,
            bg=BACKGROUND_COLOR,
        )
        label.pack(pady=(0, 30))

        self._add_button(frame, "Run!", self.scrape_prices)
        self._add_button(frame, "Edit Config", self._edit_config)
        self._add_button(frame, "Reset Config", self._confirm_reset_config)
        self._add_button(frame, "Show History", self._draw_plot)
        self._add_button(frame, "Export History", self._export_log_file)
        self._add_button(frame, "Import History", self._import_log_file)

    def _configure_checkbox_frame(self, checkbox_frame):
        """Configure the checkbox frame for background tasks and settings."""
        background_checkbox_value = tk.BooleanVar(value=BackgroundTask.identify())
        self._add_checkbox(
            checkbox_frame,
            "Daily Background Calculations",
            background_checkbox_value,
            lambda: self._toggle_background_task(background_checkbox_value.get()),
        )

        discord_webhook_checkbox_value = tk.BooleanVar(
            value=self.scraper.config.getboolean(
                "App Settings", "discord_notifications", fallback=False
            )
        )
        self._add_checkbox(
            checkbox_frame,
            "Receive Discord Notifications",
            discord_webhook_checkbox_value,
            lambda: self._toggle_discord_webhook(discord_webhook_checkbox_value.get()),
        )

        use_proxy_checkbox_value = tk.BooleanVar(
            value=self.scraper.config.getboolean("App Settings", "use_proxy", fallback=False)
        )
        self._add_checkbox(
            checkbox_frame,
            "Proxy Requests",
            use_proxy_checkbox_value,
            lambda: self._toggle_use_proxy(use_proxy_checkbox_value.get()),
        )

    def _configure_window(self):
        """Configure the main application window UI and add buttons for the main
        functionalities.
        """
        window = tk.Tk()
        window.title(APPLICATION_NAME)
        window.geometry(WINDOW_SIZE)
        window.configure(bg=BACKGROUND_COLOR)
        if OS == OSType.WINDOWS:
            app_id = "cs2tracker.unique.id"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        icon = tk.PhotoImage(file=ICON_FILE)
        window.wm_iconphoto(False, icon)

        frame = tk.Frame(window, bg=BACKGROUND_COLOR, padx=30, pady=30)
        frame.pack(expand=True, fill="both")
        self._configure_main_frame(frame)

        checkbox_frame = tk.Frame(frame, bg=BACKGROUND_COLOR)
        checkbox_frame.pack(pady=(20, 0), fill="x")
        self._configure_checkbox_frame(checkbox_frame)

        return window

    def _construct_scraper_command_windows(self):
        """Construct the command to run the scraper in a new window for Windows."""
        get_size = "$size = $Host.UI.RawUI.WindowSize;"
        set_size = "$Host.UI.RawUI.WindowSize = $size;"
        set_window_title = f"$Host.UI.RawUI.WindowTitle = '{APPLICATION_NAME}';"
        set_window_width = (
            f"$size.Width = [Math]::Min({SCRAPER_WINDOW_WIDTH}, $Host.UI.RawUI.BufferSize.Width);"
        )
        set_window_height = f"$size.Height = {SCRAPER_WINDOW_HEIGHT};"
        set_background_color = (
            f"$Host.UI.RawUI.BackgroundColor = '{SCRAPER_WINDOW_BACKGROUND_COLOR}';"
        )
        clear = "Clear-Host;"

        if RUNNING_IN_EXE:
            # The python executable is set as the executable itself in PyInstaller
            scraper_cmd = f"{PYTHON_EXECUTABLE} --only-scrape | {POWERSHELL_COLORIZE_OUTPUT}"
        else:
            scraper_cmd = f"{PYTHON_EXECUTABLE} -m cs2tracker --only-scrape"

        cmd = (
            'start powershell -NoExit -Command "& {'
            + set_window_title
            + get_size
            + set_window_width
            + set_window_height
            + set_size
            + set_background_color
            + clear
            + scraper_cmd
            + '}"'
        )
        return cmd

    def _construct_scraper_command(self):
        """Construct the command to run the scraper in a new window."""
        if OS == OSType.WINDOWS:
            return self._construct_scraper_command_windows()
        else:
            # TODO: Implement for Linux
            return ""

    def scrape_prices(self):
        """Scrape prices from the configured sources, print the total, and save the
        results to a file.
        """
        if OS == OSType.WINDOWS:
            scraper_cmd = self._construct_scraper_command()
            Popen(scraper_cmd, shell=True)
        else:
            # TODO: implement external window for Linux
            self.scraper.scrape_prices()

    def _edit_config(self):
        """Edit the configuration file using the specified text editor."""
        _popen_and_call(
            popen_args={"args": [TEXT_EDITOR, CONFIG_FILE], "shell": True},
            callback=self.scraper.parse_config,
        )

    def _confirm_reset_config(self):
        confirm = messagebox.askokcancel(
            "Reset Config", "Are you sure you want to reset the config file?"
        )
        if confirm:
            self._reset_config()

    def _reset_config(self):
        """Reset the configuration file to its default state."""
        copy(CONFIG_FILE_BACKUP, CONFIG_FILE)
        self.scraper.parse_config()

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
        self.scraper.toggle_use_proxy(enabled)

    def _toggle_discord_webhook(self, enabled: bool):
        """Toggle whether the scraper should send notifications to a Discord webhook."""
        self.scraper.toggle_discord_webhook(enabled)


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
